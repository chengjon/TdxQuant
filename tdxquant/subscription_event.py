from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from .serialization import serialize_value

SUBSCRIPTION_EVENT_SCHEMA_VERSION = "2026-04-28"
SUBSCRIPTION_EVENT_TYPE = "quote_update"
SUBSCRIPTION_EVENT_CAPABILITY = "subscription.watch"


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def looks_like_symbol(value: str) -> bool:
    normalized = value.strip().upper()
    return bool(re.fullmatch(r"\d{6}(?:\.(?:SH|SZ|BJ))?", normalized))


def extract_subscription_symbol(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("symbol", "stock_code", "stock", "code"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def extract_subscription_source_ts(payload: Any, fallback: Any = None) -> str | None:
    candidates: list[Any] = []
    if isinstance(payload, dict):
        for key in ("source_ts", "UpdateTime", "update_time", "DateTime", "datetime", "time", "Time", "timestamp"):
            candidates.append(payload.get(key))
    candidates.append(fallback)
    for value in candidates:
        serialized = serialize_value(value)
        if isinstance(serialized, str) and serialized.strip():
            return serialized
    return None


def build_subscription_event_row(
    payload: Any,
    *,
    session_id: str,
    provider_instance_id: str,
    subscription_id: str,
    run_id: str,
    capability: str,
    sequence: int,
    symbol: str | None = None,
    source_ts: str | None = None,
    reconnect_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    serialized_payload = serialize_value(payload)
    resolved_symbol = symbol or extract_subscription_symbol(serialized_payload)
    resolved_source_ts = source_ts or extract_subscription_source_ts(serialized_payload)
    return {
        "schema_version": SUBSCRIPTION_EVENT_SCHEMA_VERSION,
        "capability": capability,
        "run_id": run_id,
        "session_id": session_id,
        "provider_instance_id": provider_instance_id,
        "subscription_id": subscription_id,
        "sequence": sequence,
        "event_type": SUBSCRIPTION_EVENT_TYPE,
        "symbol": resolved_symbol,
        "source_ts": resolved_source_ts,
        "event_ts": _now_utc_iso(),
        "reconnect_metadata": dict(reconnect_metadata or {}),
        "payload": serialized_payload,
    }


def normalize_subscription_event_rows(
    raw_payload: Any,
    *,
    session_id: str,
    provider_instance_id: str,
    subscription_id: str,
    run_id: str,
    capability: str = SUBSCRIPTION_EVENT_CAPABILITY,
    start_sequence: int,
    reconnect_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    serialized = serialize_value(raw_payload)
    rows: list[dict[str, Any]] = []
    next_sequence = start_sequence

    if isinstance(serialized, dict):
        symbol_keys = [key for key in serialized.keys() if isinstance(key, str) and looks_like_symbol(key)]
        if symbol_keys and len(symbol_keys) == len(serialized):
            fallback_source_ts = extract_subscription_source_ts(serialized)
            for key in symbol_keys:
                item_payload = serialized.get(key)
                rows.append(
                    build_subscription_event_row(
                        item_payload,
                        session_id=session_id,
                        provider_instance_id=provider_instance_id,
                        subscription_id=subscription_id,
                        run_id=run_id,
                        capability=capability,
                        sequence=next_sequence,
                        symbol=key,
                        source_ts=extract_subscription_source_ts(item_payload, fallback_source_ts),
                        reconnect_metadata=reconnect_metadata,
                    )
                )
                next_sequence += 1
            return rows

        resolved_symbol = extract_subscription_symbol(serialized)
        if resolved_symbol is not None:
            rows.append(
                build_subscription_event_row(
                    serialized,
                    session_id=session_id,
                    provider_instance_id=provider_instance_id,
                    subscription_id=subscription_id,
                    run_id=run_id,
                    capability=capability,
                    sequence=next_sequence,
                    symbol=resolved_symbol,
                    reconnect_metadata=reconnect_metadata,
                )
            )
            return rows

    if isinstance(serialized, list) and all(isinstance(item, dict) for item in serialized):
        for item in serialized:
            rows.append(
                build_subscription_event_row(
                    item,
                    session_id=session_id,
                    provider_instance_id=provider_instance_id,
                    subscription_id=subscription_id,
                    run_id=run_id,
                    capability=capability,
                    sequence=next_sequence,
                    reconnect_metadata=reconnect_metadata,
                )
            )
            next_sequence += 1
        return rows

    rows.append(
        build_subscription_event_row(
            serialized,
            session_id=session_id,
            provider_instance_id=provider_instance_id,
            subscription_id=subscription_id,
            run_id=run_id,
            capability=capability,
            sequence=next_sequence,
            reconnect_metadata=reconnect_metadata,
        )
    )
    return rows
