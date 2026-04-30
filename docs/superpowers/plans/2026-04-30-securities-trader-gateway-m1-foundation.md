# Securities Trader Gateway M1 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first foundation slice of the broker-neutral securities trader mainline: canonical trader models, registry, file-backed store, and a minimal `TradeService` that can place, persist, and query tracked orders through pluggable gateways.

**Architecture:** Introduce a new `tdxquant/trader/` package that is independent from `TdxTradeManager.pingan.*`. The first slice will be tested with a fake gateway so the domain layer can stabilize before wiring PingAn desktop execution and CLI compatibility. Persistence will use a dedicated `runtime/trader/` directory with append-only JSONL streams and latest-state JSON files.

**Tech Stack:** Python 3.12, `dataclasses`, `decimal.Decimal`, `pathlib`, `json`, `unittest`, `pytest`

---

### Task 1: Add failing tests for the trader foundation slice

**Files:**
- Create: `tests/test_trader_gateway.py`
- Test: `tests/test_trader_gateway.py`

- [ ] **Step 1: Write failing tests for canonical request validation, store persistence, registry resolution, and service orchestration**

```python
import unittest
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from tdxquant.trader.models import SecurityOrderRequest, SecurityOrderSnapshot, TradeFill
from tdxquant.trader.registry import TraderGatewayRegistry
from tdxquant.trader.service import TradeService
from tdxquant.trader.store import TraderStore
```

- [ ] **Step 2: Run the new test file to verify it fails for missing modules**

Run: `pytest tests/test_trader_gateway.py -q`
Expected: FAIL with `ModuleNotFoundError` or import errors for `tdxquant.trader.*`

### Task 2: Implement canonical trader models and registry

**Files:**
- Create: `tdxquant/trader/__init__.py`
- Create: `tdxquant/trader/enums.py`
- Create: `tdxquant/trader/models.py`
- Create: `tdxquant/trader/gateway.py`
- Create: `tdxquant/trader/registry.py`
- Test: `tests/test_trader_gateway.py`

- [ ] **Step 1: Add minimal canonical enums and dataclasses to satisfy the validation tests**

```python
class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"
```

```python
@dataclass(slots=True)
class SecurityOrderRequest:
    broker: str
    client_order_id: str
    symbol: str
    market: str
    side: str
    quantity: int
    limit_price: Decimal
    order_type: str = "limit"
```

- [ ] **Step 2: Add the protocol and registry with a simple register/resolve flow**

Run: `pytest tests/test_trader_gateway.py -q`
Expected: FAIL on missing store/service behavior after import issues are resolved

### Task 3: Implement the file-backed canonical trader store

**Files:**
- Create: `tdxquant/trader/store.py`
- Test: `tests/test_trader_gateway.py`

- [ ] **Step 1: Add append/write/read helpers for canonical events, snapshots, and fills**

```python
class TraderStore:
    def append_order_event(self, payload: dict[str, Any]) -> Path: ...
    def write_order_snapshot(self, snapshot: SecurityOrderSnapshot) -> Path: ...
    def append_trade_fill(self, fill: TradeFill) -> Path: ...
```

- [ ] **Step 2: Run the targeted tests and verify the store tests fail only on service orchestration**

Run: `pytest tests/test_trader_gateway.py -q`
Expected: FAIL only in tests that exercise `TradeService`

### Task 4: Implement the minimal TradeService

**Files:**
- Create: `tdxquant/trader/service.py`
- Modify: `tdxquant/trader/__init__.py`
- Test: `tests/test_trader_gateway.py`

- [ ] **Step 1: Implement `connect`, `heartbeat`, `place_order`, `query_order`, `query_trades`, and `sync_today_trades` against the registry and store**

```python
class TradeService:
    def place_order(self, request: SecurityOrderRequest) -> SecurityOrderSnapshot:
        issues = request.validate()
        if issues:
            raise ValueError("; ".join(issues))
```

- [ ] **Step 2: Run the targeted tests and verify the whole foundation slice is green**

Run: `pytest tests/test_trader_gateway.py -q`
Expected: PASS

### Task 5: Run the broader regression slice

**Files:**
- Test: `tests/test_trader_gateway.py`
- Test: `tests/test_trade_manager.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Run a focused regression set to ensure the new trader package does not break existing trading surfaces**

Run: `pytest tests/test_trader_gateway.py tests/test_trade_manager.py tests/test_api_cli.py -q`
Expected: PASS
