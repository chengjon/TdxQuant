from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import SecurityOrderSnapshot, TradeFill


class TraderStore:
    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir)
        self.order_events_path = self.base_dir / "order-events.jsonl"
        self.order_snapshots_path = self.base_dir / "order-snapshots.jsonl"
        self.trade_fills_path = self.base_dir / "trade-fills.jsonl"
        self.latest_orders_path = self.base_dir / "latest-orders.json"
        self.latest_trades_path = self.base_dir / "latest-trades.json"

    def append_order_event(self, payload: dict[str, Any]) -> Path:
        self._ensure_dir()
        with self.order_events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
        return self.order_events_path

    def write_order_snapshot(self, snapshot: SecurityOrderSnapshot) -> Path:
        self._ensure_dir()
        payload = snapshot.to_dict()
        with self.order_snapshots_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
        latest = self._read_json_object(self.latest_orders_path)
        latest[snapshot.gateway_order_id] = payload
        self.latest_orders_path.write_text(json.dumps(latest, ensure_ascii=True, indent=2), encoding="utf-8")
        return self.order_snapshots_path

    def append_trade_fill(self, fill: TradeFill) -> Path:
        self._ensure_dir()
        payload = fill.to_dict()
        with self.trade_fills_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
        latest = self._read_json_list(self.latest_trades_path)
        latest_by_id = {str(item.get("trade_id")): item for item in latest}
        latest_by_id[fill.trade_id] = payload
        ordered = [latest_by_id[key] for key in sorted(latest_by_id)]
        self.latest_trades_path.write_text(json.dumps(ordered, ensure_ascii=True, indent=2), encoding="utf-8")
        return self.trade_fills_path

    def get_order_snapshot(self, gateway_order_id: str) -> SecurityOrderSnapshot | None:
        latest = self._read_json_object(self.latest_orders_path)
        payload = latest.get(gateway_order_id)
        if payload is None:
            return None
        return SecurityOrderSnapshot.from_dict(payload)

    def list_trade_fills(self) -> list[TradeFill]:
        latest = self._read_json_list(self.latest_trades_path)
        return [TradeFill.from_dict(item) for item in latest]

    def _ensure_dir(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _read_json_object(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_json_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))
