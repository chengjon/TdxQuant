from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def get_provider_replay_fixture_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "provider"


_PROVIDER_REPLAY_FIXTURE_REGISTRY: list[dict[str, str]] = [
    {
        "name": "provider-result-success",
        "capability": "provider.result",
        "format": "json",
        "description": "Minimal successful synchronous provider result envelope sample.",
        "relative_path": "provider-result-success.json",
    },
    {
        "name": "provider-result-failure",
        "capability": "provider.result",
        "format": "json",
        "description": "Minimal failed synchronous provider result envelope sample.",
        "relative_path": "provider-result-failure.json",
    },
    {
        "name": "formula-screen-success",
        "capability": "formula.screen",
        "format": "json",
        "description": "Representative successful formula.screen provider response sample.",
        "relative_path": "formula-screen-success.json",
    },
    {
        "name": "formula-screen-failure",
        "capability": "formula.screen",
        "format": "json",
        "description": "Representative failed formula.screen provider response sample.",
        "relative_path": "formula-screen-failure.json",
    },
    {
        "name": "runtime-capabilities-success",
        "capability": "runtime.capabilities",
        "format": "json",
        "description": "Representative runtime.capabilities provider response sample.",
        "relative_path": "runtime-capabilities-success.json",
    },
    {
        "name": "runtime-health-degraded",
        "capability": "runtime.health",
        "format": "json",
        "description": "Representative degraded runtime.health provider response sample.",
        "relative_path": "runtime-health-degraded.json",
    },
    {
        "name": "runtime-doctor-degraded",
        "capability": "runtime.doctor",
        "format": "json",
        "description": "Representative degraded runtime.doctor provider response sample.",
        "relative_path": "runtime-doctor-degraded.json",
    },
    {
        "name": "market-snapshot-success",
        "capability": "market.snapshot",
        "format": "json",
        "description": "Representative successful market.snapshot provider response sample.",
        "relative_path": "market-snapshot-success.json",
    },
    {
        "name": "market-stock-info-success",
        "capability": "market.stock_info",
        "format": "json",
        "description": "Representative successful market.stock_info provider response sample.",
        "relative_path": "market-stock-info-success.json",
    },
    {
        "name": "market-more-info-success",
        "capability": "market.more_info",
        "format": "json",
        "description": "Representative successful market.more_info provider response sample.",
        "relative_path": "market-more-info-success.json",
    },
    {
        "name": "market-cb-info-success",
        "capability": "market.cb_info",
        "format": "json",
        "description": "Representative successful market.cb_info provider response sample.",
        "relative_path": "market-cb-info-success.json",
    },
    {
        "name": "market-kline-success",
        "capability": "market.kline",
        "format": "json",
        "description": "Representative successful market.kline provider response sample.",
        "relative_path": "market-kline-success.json",
    },
    {
        "name": "market-kline-empty",
        "capability": "market.kline",
        "format": "json",
        "description": "Representative empty-result market.kline provider response sample.",
        "relative_path": "market-kline-empty.json",
    },
    {
        "name": "meta-stock-list-success",
        "capability": "meta.stock_list",
        "format": "json",
        "description": "Representative successful meta.stock_list provider response sample.",
        "relative_path": "meta-stock-list-success.json",
    },
    {
        "name": "meta-sector-stocks-success",
        "capability": "meta.sector_stocks",
        "format": "json",
        "description": "Representative successful meta.sector_stocks provider response sample.",
        "relative_path": "meta-sector-stocks-success.json",
    },
    {
        "name": "meta-sector-stocks-empty",
        "capability": "meta.sector_stocks",
        "format": "json",
        "description": "Representative empty-result meta.sector_stocks provider response sample.",
        "relative_path": "meta-sector-stocks-empty.json",
    },
    {
        "name": "financial-financial-data-success",
        "capability": "financial.financial_data",
        "format": "json",
        "description": "Representative successful financial.financial_data provider response sample.",
        "relative_path": "financial-financial-data-success.json",
    },
    {
        "name": "financial-financial-data-by-date-success",
        "capability": "financial.financial_data_by_date",
        "format": "json",
        "description": "Representative successful financial.financial_data_by_date provider response sample.",
        "relative_path": "financial-financial-data-by-date-success.json",
    },
    {
        "name": "financial-financial-data-failure",
        "capability": "financial.financial_data",
        "format": "json",
        "description": "Representative failed financial.financial_data provider response sample.",
        "relative_path": "financial-financial-data-failure.json",
    },
    {
        "name": "transaction-stock-transaction-data-success",
        "capability": "transaction.stock_transaction_data",
        "format": "json",
        "description": "Representative successful transaction.stock_transaction_data provider response sample.",
        "relative_path": "transaction-stock-transaction-data-success.json",
    },
    {
        "name": "transaction-market-transaction-data-success",
        "capability": "transaction.market_transaction_data",
        "format": "json",
        "description": "Representative successful transaction.market_transaction_data provider response sample.",
        "relative_path": "transaction-market-transaction-data-success.json",
    },
    {
        "name": "transaction-stock-transaction-data-failure",
        "capability": "transaction.stock_transaction_data",
        "format": "json",
        "description": "Representative failed transaction.stock_transaction_data provider response sample.",
        "relative_path": "transaction-stock-transaction-data-failure.json",
    },
    {
        "name": "block-send-user-block-applied",
        "capability": "block.send_user_block",
        "format": "json",
        "description": "Representative successful block mutation provider response sample.",
        "relative_path": "block-send-user-block-applied.json",
    },
    {
        "name": "block-send-user-block-noop",
        "capability": "block.send_user_block",
        "format": "json",
        "description": "Representative skipped block mutation provider response sample.",
        "relative_path": "block-send-user-block-noop.json",
    },
    {
        "name": "block-send-user-block-rejected",
        "capability": "block.send_user_block",
        "format": "json",
        "description": "Representative rejected block mutation provider response sample.",
        "relative_path": "block-send-user-block-rejected.json",
    },
    {
        "name": "block-read-watchlist-success",
        "capability": "block.read_watchlist_snapshot",
        "format": "json",
        "description": "Representative successful block watchlist snapshot provider response sample.",
        "relative_path": "block-read-watchlist-success.json",
    },
    {
        "name": "block-read-watchlist-empty",
        "capability": "block.read_watchlist_snapshot",
        "format": "json",
        "description": "Representative empty block watchlist snapshot provider response sample.",
        "relative_path": "block-read-watchlist-empty.json",
    },
    {
        "name": "block-read-watchlist-missing-block",
        "capability": "block.read_watchlist_snapshot",
        "format": "json",
        "description": "Representative missing block watchlist snapshot provider error sample.",
        "relative_path": "block-read-watchlist-missing-block.json",
    },
    {
        "name": "block-read-watchlist-invalid-member",
        "capability": "block.read_watchlist_snapshot",
        "format": "json",
        "description": "Representative invalid member block watchlist snapshot provider error sample.",
        "relative_path": "block-read-watchlist-invalid-member.json",
    },
    {
        "name": "block-sync-replace-applied",
        "capability": "block.sync_watchlist",
        "format": "json",
        "description": "Representative successful replace-mode block sync provider response sample.",
        "relative_path": "block-sync-replace-applied.json",
    },
    {
        "name": "block-sync-merge-noop",
        "capability": "block.sync_watchlist",
        "format": "json",
        "description": "Representative noop merge-mode block sync provider response sample.",
        "relative_path": "block-sync-merge-noop.json",
    },
    {
        "name": "block-sync-replace-rejected",
        "capability": "block.sync_watchlist",
        "format": "json",
        "description": "Representative rejected replace-mode block sync provider response sample.",
        "relative_path": "block-sync-replace-rejected.json",
    },
    {
        "name": "block-sync-replace-plan",
        "capability": "block.sync_watchlist",
        "format": "json",
        "description": "Representative dry-run replace-mode block sync provider response sample.",
        "relative_path": "block-sync-replace-plan.json",
    },
    {
        "name": "subscription-event-batch",
        "capability": "subscription.quote_update",
        "format": "jsonl",
        "description": "Representative normalized subscription event row batch sample.",
        "relative_path": "subscription-event-batch.jsonl",
    },
    {
        "name": "subscription-watch-events",
        "capability": "subscription.watch",
        "format": "jsonl",
        "description": "Representative canonical subscription-watch event stream sample.",
        "relative_path": "subscription-watch-events.jsonl",
    },
    {
        "name": "subscription-watch-event-stream-frames",
        "capability": "subscription.watch",
        "format": "jsonl",
        "description": "Representative bridge SSE frame payloads for subscription-watch event stream transport.",
        "relative_path": "subscription-watch-event-stream-frames.jsonl",
        "transport": "sse",
        "playback_mode": "immediate",
    },
    {
        "name": "subscription-watch-event-stream-delayed-playback",
        "capability": "subscription.watch",
        "format": "jsonl",
        "description": "Representative delayed playback SSE frame payloads for subscription-watch event stream transport.",
        "relative_path": "subscription-watch-event-stream-delayed-playback.jsonl",
        "transport": "sse",
        "playback_mode": "delayed",
    },
    {
        "name": "subscription-watch-status-completed",
        "capability": "subscription.watch",
        "format": "json",
        "description": "Representative completed subscription-watch status snapshot.",
        "relative_path": "subscription-watch-status-completed.json",
    },
    {
        "name": "subscription-watch-status-reconnecting",
        "capability": "subscription.watch",
        "format": "json",
        "description": "Representative reconnecting subscription-watch status snapshot.",
        "relative_path": "subscription-watch-status-reconnecting.json",
    },
    {
        "name": "subscription-watch-status-degraded",
        "capability": "subscription.watch",
        "format": "json",
        "description": "Representative degraded subscription-watch status snapshot.",
        "relative_path": "subscription-watch-status-degraded.json",
    },
    {
        "name": "subscription-watch-summary-completed",
        "capability": "subscription.watch",
        "format": "json",
        "description": "Representative completed subscription-watch final summary.",
        "relative_path": "subscription-watch-summary-completed.json",
    },
    {
        "name": "subscription-watch-summary-with-reconnect",
        "capability": "subscription.watch",
        "format": "json",
        "description": "Representative completed subscription-watch summary with reconnect recovery.",
        "relative_path": "subscription-watch-summary-with-reconnect.json",
    },
    {
        "name": "subscription-watch-manifest",
        "capability": "subscription.watch",
        "format": "json",
        "description": "Representative subscription-watch run manifest.",
        "relative_path": "subscription-watch-manifest.json",
    },
]


def list_provider_replay_fixtures() -> list[dict[str, str]]:
    return [copy.deepcopy(item) for item in _PROVIDER_REPLAY_FIXTURE_REGISTRY]


def _find_provider_replay_fixture_descriptor(name: str) -> dict[str, str]:
    for item in _PROVIDER_REPLAY_FIXTURE_REGISTRY:
        if item["name"] == name:
            return item
    raise ValueError(f"unsupported provider replay fixture: {name}")
def get_provider_replay_fixture_path(name: str) -> Path:
    descriptor = _find_provider_replay_fixture_descriptor(name)
    return get_provider_replay_fixture_dir() / descriptor["relative_path"]


def load_provider_replay_fixture(name: str) -> Any:
    descriptor = _find_provider_replay_fixture_descriptor(name)
    path = get_provider_replay_fixture_path(name)
    raw_text = path.read_text(encoding="utf-8")
    if descriptor["format"] == "json":
        return json.loads(raw_text)
    if descriptor["format"] == "jsonl":
        rows: list[dict[str, Any]] = []
        for raw_line in raw_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                rows.append(payload)
        return rows
    raise ValueError(f"unsupported provider replay fixture format: {descriptor['format']}")
