"""tdx-api HTTP REST data provider — connects to tdx-api Docker container."""

from __future__ import annotations

import logging
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import quote
import json

from ..models import ErrorCode, Result

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://192.168.123.104:8089"
_TIMEOUT = 10  # seconds


def _http_get(url: str, timeout: int = _TIMEOUT) -> dict[str, Any]:
    """Simple GET returning parsed JSON."""
    req = Request(url)
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _http_post(url: str, body: dict[str, Any], timeout: int = _TIMEOUT) -> dict[str, Any]:
    """Simple POST with JSON body returning parsed JSON."""
    data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _price_from_li(val: int) -> float:
    """Convert tdx-api price (厘) to yuan."""
    return val / 1000.0


def _strip_code_suffix(code: str) -> str:
    """'600000.SH' → '600000', '000001.SZ' → '000001'."""
    return code.split(".")[0]


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

class TdxApiProvider:
    """HTTP client for tdx-api Docker container."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")

    def health(self) -> bool:
        try:
            _http_get(f"{self.base_url}/api/health")
            return True
        except Exception:
            return False

    # -- data methods --

    def get_kline(self, code: str, kline_type: str = "day", start_time: str = "", end_time: str = "", count: int = 0) -> list[dict[str, Any]]:
        """Fetch K-line data. code='600000.SH', kline_type='day'/'week'/'month'/'minute1'/'5'/'15'/'30'/'hour'."""
        raw_code = _strip_code_suffix(code)
        resp = _http_get(f"{self.base_url}/api/kline?code={raw_code}&type={kline_type}")
        if resp.get("code") != 0:
            return []
        data = resp.get("data", {})
        items = data.get("List", [])
        results = []
        start_compact = start_time.replace("-", "") if start_time else ""
        end_compact = end_time.replace("-", "") if end_time else ""
        for item in items:
            dt = item.get("Time", "")
            dt_compact = dt[:10].replace("-", "")
            if start_compact and dt_compact < start_compact:
                continue
            if end_compact and dt_compact > end_compact:
                continue
            results.append({
                "datetime": dt,
                "open": _price_from_li(item.get("Open", 0)),
                "high": _price_from_li(item.get("High", 0)),
                "low": _price_from_li(item.get("Low", 0)),
                "close": _price_from_li(item.get("Close", 0)),
                "vol": item.get("Volume", 0),
                "amount": item.get("Amount", 0),
            })
        if count > 0 and len(results) > count:
            results = results[-count:]
        return results

    def get_quote(self, codes: list[str]) -> list[dict[str, Any]]:
        """Fetch real-time quotes."""
        raw_codes = ",".join(_strip_code_suffix(c) for c in codes)
        resp = _http_get(f"{self.base_url}/api/quote?code={raw_codes}")
        if resp.get("code") != 0:
            return []
        items = resp.get("data", [])
        results = []
        for q in items:
            k = q.get("K", {})
            buy_levels = q.get("BuyLevel", [])
            sell_levels = q.get("SellLevel", [])
            results.append({
                "code": f"{q.get('Code', '')}.{'SH' if q.get('Exchange') == 1 else 'SZ'}",
                "price": _price_from_li(k.get("Close", 0)),
                "open": _price_from_li(k.get("Open", 0)),
                "high": _price_from_li(k.get("High", 0)),
                "low": _price_from_li(k.get("Low", 0)),
                "last_close": _price_from_li(k.get("Last", 0)),
                "vol": q.get("TotalHand", 0),
                "amount": q.get("Amount", 0),
                "bid1": _price_from_li(buy_levels[0]["Price"]) if len(buy_levels) > 0 else 0,
                "bid2": _price_from_li(buy_levels[1]["Price"]) if len(buy_levels) > 1 else 0,
                "bid3": _price_from_li(buy_levels[2]["Price"]) if len(buy_levels) > 2 else 0,
                "bid4": _price_from_li(buy_levels[3]["Price"]) if len(buy_levels) > 3 else 0,
                "bid5": _price_from_li(buy_levels[4]["Price"]) if len(buy_levels) > 4 else 0,
                "ask1": _price_from_li(sell_levels[0]["Price"]) if len(sell_levels) > 0 else 0,
                "ask2": _price_from_li(sell_levels[1]["Price"]) if len(sell_levels) > 1 else 0,
                "ask3": _price_from_li(sell_levels[2]["Price"]) if len(sell_levels) > 2 else 0,
                "ask4": _price_from_li(sell_levels[3]["Price"]) if len(sell_levels) > 3 else 0,
                "ask5": _price_from_li(sell_levels[4]["Price"]) if len(sell_levels) > 4 else 0,
            })
        return results

    def get_stock_list(self, exchange: str = "all") -> list[str]:
        """Fetch stock code list."""
        resp = _http_get(f"{self.base_url}/api/codes?exchange={exchange}")
        if resp.get("code") != 0:
            return []
        codes = resp.get("data", {}).get("codes", [])
        return [f"{c['code']}.{c['exchange'].upper()}" for c in codes if c.get("code")]

    def get_trading_dates(self, start: str = "", end: str = "") -> list[str]:
        """Fetch trading dates in range. Dates as YYYY-MM-DD."""
        params = []
        if start:
            params.append(f"start={start}")
        if end:
            params.append(f"end={end}")
        qs = "&".join(params)
        url = f"{self.base_url}/api/workday/range?{qs}" if qs else f"{self.base_url}/api/workday/range"
        resp = _http_get(url)
        if resp.get("code") != 0:
            return []
        items = resp.get("data", {}).get("list", [])
        return [str(item.get("iso", item.get("numeric", ""))).replace("-", "") for item in items]

    def get_minute(self, code: str, date: str = "") -> list[dict[str, Any]]:
        """Fetch minute-level data."""
        raw_code = _strip_code_suffix(code)
        url = f"{self.base_url}/api/minute?code={raw_code}"
        if date:
            url += f"&date={date}"
        resp = _http_get(url)
        if resp.get("code") != 0:
            return []
        data = resp.get("data", {})
        if isinstance(data, list):
            return data
        items = data.get("List") or []
        return [
            {
                "time": item.get("Time", ""),
                "price": _price_from_li(item.get("Price", 0)),
                "vol": item.get("Number", 0),
            }
            for item in items
        ]

    def get_trade(self, code: str, date: str = "") -> list[dict[str, Any]]:
        """Fetch tick-by-tick trade data."""
        raw_code = _strip_code_suffix(code)
        url = f"{self.base_url}/api/trade?code={raw_code}"
        if date:
            url += f"&date={date}"
        resp = _http_get(url)
        if resp.get("code") != 0:
            return []
        data = resp.get("data", {})
        if isinstance(data, list):
            return data
        items = data.get("List") or []
        return [
            {
                "time": item.get("Time", ""),
                "price": _price_from_li(item.get("Price", 0)),
                "vol": item.get("Volume", 0),
                "buyorsell": item.get("Status", 0),
            }
            for item in items
        ]

    def search(self, keyword: str) -> list[dict[str, Any]]:
        """Search stocks by name/code."""
        resp = _http_get(f"{self.base_url}/api/search?keyword={quote(keyword)}")
        if resp.get("code") != 0:
            return []
        return resp.get("data", [])

    def get_market_stats(self) -> dict[str, Any]:
        """Get market statistics (up/down/flat counts)."""
        resp = _http_get(f"{self.base_url}/api/market-stats")
        if resp.get("code") != 0:
            return {}
        return resp.get("data", {})


# ---------------------------------------------------------------------------
# Singleton + helpers
# ---------------------------------------------------------------------------

_provider: TdxApiProvider | None = None


def get_provider(base_url: str = DEFAULT_BASE_URL) -> TdxApiProvider:
    global _provider
    if _provider is None or _provider.base_url != base_url.rstrip("/"):
        _provider = TdxApiProvider(base_url)
    return _provider


def is_tdxapi_available(base_url: str = DEFAULT_BASE_URL) -> bool:
    try:
        return get_provider(base_url).health()
    except Exception:
        return False


def run_tdxapi_call(action: str, callback, base_url: str = DEFAULT_BASE_URL) -> Result:
    """Execute a callback with TdxApiProvider."""
    provider = get_provider(base_url)
    if not provider.health():
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"{action}: tdx-api service unavailable at {base_url}",
            next_action="Check that tdx-api Docker container is running.",
        )
    try:
        payload = callback(provider)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message=action,
            data={"provider": "tdxapi", "base_url": base_url, "result": payload},
        )
    except ValueError as exc:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"{action} failed: {exc}",
        )
