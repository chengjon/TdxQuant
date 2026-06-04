"""pytdx-based data provider — cross-platform alternative to the DLL backend."""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any

from ..models import ErrorCode, Result

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Code format helpers
# ---------------------------------------------------------------------------

_SZ_PREFIXES = ("000", "001", "002", "003", "004", "300", "301")
_SH_PREFIXES = ("600", "601", "603", "605", "688", "689")

# pytdx K-line category constants
KLINE_1MIN = 8
KLINE_5MIN = 0
KLINE_15MIN = 1
KLINE_30MIN = 2
KLINE_1HOUR = 3
KLINE_DAILY = 4
KLINE_WEEKLY = 5
KLINE_MONTHLY = 6

_PERIOD_MAP: dict[str, int] = {
    "1m": KLINE_1MIN,
    "5m": KLINE_5MIN,
    "15m": KLINE_15MIN,
    "30m": KLINE_30MIN,
    "1h": KLINE_1HOUR,
    "1d": KLINE_DAILY,
    "1w": KLINE_WEEKLY,
    "1mon": KLINE_MONTHLY,
}

_BLOCK_FILE_MAP: dict[str, str] = {
    "industry": "block_gn.dat",
    "concept": "block_fg.dat",
    "sector": "block_zs.dat",
    "default": "block.dat",
}

DEFAULT_SERVERS: list[tuple[str, int]] = [
    ("119.147.212.81", 7709),
    ("112.74.214.43", 7709),
    ("221.231.141.60", 7709),
    ("101.227.73.20", 7709),
    ("14.215.128.18", 7709),
    ("59.173.18.140", 7709),
    ("180.153.18.170", 7709),
]


def split_code(code: str) -> tuple[int, str]:
    """Convert '600000.SH' → (1, '600000'). Raises ValueError on bad format."""
    parts = code.split(".")
    if len(parts) != 2:
        raise ValueError(f"Invalid stock code format: {code} (expected 'NNNNNN.SS')")
    num, suffix = parts[0], parts[1].upper()
    if suffix == "SH" or num[:3] in _SH_PREFIXES:
        return 1, num
    return 0, num


def join_code(market: int, code: str) -> str:
    """Convert (1, '600000') → '600000.SH'."""
    return f"{code}.{'SH' if market == 1 else 'SZ'}"


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

class PytdxProvider:
    """Manages a pytdx TCP connection and exposes data-query methods."""

    def __init__(self, servers: list[tuple[str, int]] | None = None) -> None:
        self._servers = servers or DEFAULT_SERVERS
        self._api: Any = None
        self._lock = threading.Lock()
        self._connected = False

    # -- lifecycle --

    def connect(self, timeout: float = 10.0) -> bool:
        from pytdx.hq import TdxHq_API  # lazy import
        with self._lock:
            if self._connected and self._api is not None:
                return True
            self._api = TdxHq_API()
            for host, port in self._servers:
                try:
                    if self._api.connect(host, port, time_out=timeout):
                        self._connected = True
                        logger.info("pytdx connected to %s:%s", host, port)
                        return True
                except Exception as exc:
                    logger.debug("pytdx connect %s:%s failed: %s", host, port, exc)
                    continue
            self._api = None
            return False

    def disconnect(self) -> None:
        with self._lock:
            if self._api is not None:
                try:
                    self._api.disconnect()
                except Exception:
                    pass
                self._api = None
                self._connected = False

    def ensure_connected(self) -> bool:
        if self._connected and self._api is not None:
            return True
        return self.connect()

    @property
    def available(self) -> bool:
        return self._connected and self._api is not None

    # -- data methods --

    def get_kline(
        self,
        stock_code: str,
        period: str = "1d",
        start_time: str = "",
        end_time: str = "",
        count: int = 800,
    ) -> list[dict[str, Any]]:
        """Fetch K-line bars. Returns list of dicts with OHLCV data."""
        if not self.ensure_connected():
            return []
        category = _PERIOD_MAP.get(period)
        if category is None:
            raise ValueError(f"Unsupported period: {period}")
        market, code = split_code(stock_code)

        all_bars: list[dict[str, Any]] = []
        start_pos = 0
        batch = 800
        max_pages = max(1, count // batch + 1)
        earliest = start_time.replace("-", "") if start_time else ""

        for _ in range(max_pages):
            try:
                bars = self._api.get_security_bars(category, market, code, start_pos, batch)
            except Exception:
                break
            if not bars:
                break
            all_bars.extend(bars)
            if earliest and bars[0].get("datetime", "")[:8].replace("-", "") <= earliest:
                break
            start_pos += batch
            if len(all_bars) >= count:
                break

        result = []
        for b in all_bars:
            dt = str(b.get("datetime", ""))
            dt_compact = dt[:10].replace("-", "")
            if start_time and dt_compact < start_time.replace("-", ""):
                continue
            if end_time and dt_compact > end_time.replace("-", ""):
                continue
            result.append({
                "datetime": dt,
                "open": float(b.get("open", 0)),
                "high": float(b.get("high", 0)),
                "low": float(b.get("low", 0)),
                "close": float(b.get("close", 0)),
                "vol": float(b.get("vol", 0)),
                "amount": float(b.get("amount", 0)),
            })
            if count > 0 and len(result) >= count:
                break
        result.sort(key=lambda x: x["datetime"])
        return result

    def get_quote(self, stock_codes: list[str]) -> list[dict[str, Any]]:
        """Fetch real-time quotes for a list of stocks."""
        if not self.ensure_connected():
            return []
        params = [split_code(c) for c in stock_codes]
        try:
            quotes = self._api.get_security_quotes(params)
        except Exception:
            return []
        if not quotes:
            return []
        results = []
        for q in quotes:
            results.append({
                "code": join_code(q.get("market", 0), q.get("code", "")),
                "name": q.get("name", ""),
                "price": float(q.get("price", 0)),
                "last_close": float(q.get("last_close", 0)),
                "open": float(q.get("open", 0)),
                "high": float(q.get("high", 0)),
                "low": float(q.get("low", 0)),
                "vol": float(q.get("vol", 0)),
                "amount": float(q.get("amount", 0)),
                "bid1": float(q.get("bid1", 0)),
                "bid2": float(q.get("bid2", 0)),
                "bid3": float(q.get("bid3", 0)),
                "bid4": float(q.get("bid4", 0)),
                "bid5": float(q.get("bid5", 0)),
                "ask1": float(q.get("ask1", 0)),
                "ask2": float(q.get("ask2", 0)),
                "ask3": float(q.get("ask3", 0)),
                "ask4": float(q.get("ask4", 0)),
                "ask5": float(q.get("ask5", 0)),
                "bid_vol1": float(q.get("bid_vol1", 0)),
                "bid_vol2": float(q.get("bid_vol2", 0)),
                "bid_vol3": float(q.get("bid_vol3", 0)),
                "bid_vol4": float(q.get("bid_vol4", 0)),
                "bid_vol5": float(q.get("bid_vol5", 0)),
                "ask_vol1": float(q.get("ask_vol1", 0)),
                "ask_vol2": float(q.get("ask_vol2", 0)),
                "ask_vol3": float(q.get("ask_vol3", 0)),
                "ask_vol4": float(q.get("ask_vol4", 0)),
                "ask_vol5": float(q.get("ask_vol5", 0)),
            })
        return results

    def get_stock_list(self, market: str | None = None) -> list[str]:
        """Fetch stock list. market: 'SH'=1, 'SZ'=0, None=both."""
        if not self.ensure_connected():
            return []
        markets = []
        if market is None or market in ("1", "SH"):
            markets.append(1)
        if market is None or market in ("0", "SZ"):
            markets.append(0)

        all_codes: list[str] = []
        for m in markets:
            start = 0
            batch = 1000
            while True:
                try:
                    stocks = self._api.get_security_list(m, start)
                except Exception:
                    break
                if not stocks:
                    break
                for s in stocks:
                    suffix = "SH" if m == 1 else "SZ"
                    all_codes.append(f"{s['code']}.{suffix}")
                if len(stocks) < batch:
                    break
                start += batch
        return all_codes

    def get_sector_list(self) -> list[dict[str, Any]]:
        """Fetch block/sector list from all block files."""
        if not self.ensure_connected():
            return []
        results: list[dict[str, Any]] = []
        for block_type, filename in _BLOCK_FILE_MAP.items():
            try:
                blocks = self._api.get_and_parse_block_info(filename)
            except Exception:
                continue
            if not blocks:
                continue
            for b in blocks:
                results.append({
                    "block_type": block_type,
                    "blockname": b.get("blockname", ""),
                    "code_index": b.get("code_index", ""),
                    "code": b.get("code", ""),
                })
        return results

    def get_sector_stocks(self, block_code: str) -> list[str]:
        """Fetch constituent stocks for a block."""
        if not self.ensure_connected():
            return []
        for filename in _BLOCK_FILE_MAP.values():
            try:
                blocks = self._api.get_and_parse_block_info(filename)
            except Exception:
                continue
            if not blocks:
                continue
            for b in blocks:
                if b.get("blockname") == block_code or b.get("code_index") == block_code:
                    raw_codes = b.get("code", "")
                    if not raw_codes:
                        continue
                    codes: list[str] = []
                    for c in raw_codes.split():
                        c = c.strip()
                        if not c:
                            continue
                        try:
                            m, cd = int(c[0]), c[1:]
                            codes.append(join_code(m, cd))
                        except (ValueError, IndexError):
                            continue
                    return codes
        return []

    def get_divid_factors(self, stock_code: str) -> list[dict[str, Any]]:
        """Fetch ex-rights/ex-dividend data."""
        if not self.ensure_connected():
            return []
        market, code = split_code(stock_code)
        try:
            data = self._api.get_xdxr_info(market, code)
        except Exception:
            return []
        if not data:
            return []
        results = []
        for d in data:
            year = d.get("year", 0)
            month = d.get("month", 0)
            day = d.get("day", 0)
            cat = d.get("category", 0)
            date_str = f"{year}{month:02d}{day:02d}" if year else ""
            results.append({
                "date": date_str,
                "category": cat,
                "name": d.get("name", ""),
                "fenhong": float(d.get("fenhong", 0) or 0),
                "peigujia": float(d.get("peigujia", 0) or 0),
                "songzhuangu": float(d.get("songzhuangu", 0) or 0),
                "peigu": float(d.get("peigu", 0) or 0),
            })
        return results

    def get_financial_info(self, stock_code: str) -> dict[str, Any]:
        """Fetch basic financial snapshot."""
        if not self.ensure_connected():
            return {}
        market, code = split_code(stock_code)
        try:
            data = self._api.get_finance_info(market, code)
        except Exception:
            return {}
        if not data:
            return {}
        return {k: v for k, v in data.items() if v is not None}

    def get_trading_dates(self, start_date: str = "", end_date: str = "") -> list[str]:
        """Fetch trading dates from pytdx built-in calendar."""
        try:
            from pytdx.util.trade_date import trade_date_sse
        except ImportError:
            return []
        if trade_date_sse is None:
            return []
        dates = []
        start_int = int(start_date.replace("-", "")) if start_date else 0
        end_int = int(end_date.replace("-", "")) if end_date else 99991231
        for d in trade_date_sse:
            d_int = int(d)
            if start_int and d_int < start_int:
                continue
            if d_int > end_int:
                continue
            dates.append(str(d_int))
        return dates

    def get_minute_data(self, stock_code: str, date: int | None = None) -> list[dict[str, Any]]:
        """Fetch minute-level data. date=None=today, date=YYYYMMDD=historical."""
        if not self.ensure_connected():
            return []
        market, code = split_code(stock_code)
        try:
            if date:
                data = self._api.get_history_minute_time_data(market, code, date)
            else:
                data = self._api.get_minute_time_data(market, code)
        except Exception:
            return []
        return [{"price": float(d.get("price", 0)), "vol": float(d.get("vol", 0))} for d in (data or [])]

    def get_tick_data(self, stock_code: str, date: int | None = None, count: int = 2000) -> list[dict[str, Any]]:
        """Fetch tick-by-tick transaction data."""
        if not self.ensure_connected():
            return []
        market, code = split_code(stock_code)
        try:
            if date:
                data = self._api.get_history_transaction_data(market, code, 0, count, date)
            else:
                data = self._api.get_transaction_data(market, code, 0, count)
        except Exception:
            return []
        if not data:
            return []
        results = []
        for d in data:
            results.append({
                "time": str(d.get("time", "")),
                "price": float(d.get("price", 0)),
                "vol": float(d.get("vol", 0)),
                "buyorsell": int(d.get("buyorsell", 0)),
            })
        return results


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_provider: PytdxProvider | None = None
_provider_lock = threading.Lock()


def get_provider() -> PytdxProvider:
    global _provider
    if _provider is None:
        with _provider_lock:
            if _provider is None:
                _provider = PytdxProvider()
    return _provider


def is_pytdx_available() -> bool:
    try:
        import pytdx  # noqa: F401
        return True
    except ImportError:
        return False


def run_pytdx_call(action: str, callback) -> Result:
    """Execute a callback with the PytdxProvider, returning a Result envelope."""
    if not is_pytdx_available():
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message=f"{action}: pytdx is not installed",
            next_action="Install pytdx: pip install pytdx",
        )
    provider = get_provider()
    if not provider.ensure_connected():
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"{action}: pytdx connection failed",
            next_action="Check network connectivity to TDX servers.",
        )
    try:
        payload = callback(provider)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message=action,
            data={"provider": "pytdx", "result": payload},
        )
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"{action} failed: {exc}",
        )
