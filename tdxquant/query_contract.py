from __future__ import annotations

import copy
from typing import Any

from .models import Result


_QUERY_CONTRACT_REGISTRY: dict[str, dict[str, Any]] = {
    "market.snapshot": {
        "query_shapes": [{"query_kind": "market.snapshot", "selectors": ["symbol"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "market.full_tick": {
        "query_shapes": [{"query_kind": "market.full_tick", "selectors": ["symbol"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "market.market_snapshot": {
        "query_shapes": [{"query_kind": "market.market_snapshot", "selectors": ["symbol"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "market.kline": {
        "query_shapes": [
            {
                "query_kind": "market.kline",
                "selectors": ["symbols", "date_range"],
                "query_params": ["period", "count", "dividend_type", "fill_data"],
            }
        ],
        "supports_requested_fields": True,
    },
    "market.stock_info": {
        "query_shapes": [{"query_kind": "market.stock_info", "selectors": ["symbol"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "market.more_info": {
        "query_shapes": [{"query_kind": "market.more_info", "selectors": ["symbol"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "market.cb_info": {
        "query_shapes": [{"query_kind": "market.cb_info", "selectors": ["symbol"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "meta.stock_list": {
        "query_shapes": [{"query_kind": "meta.stock_list", "selectors": ["market"], "query_params": ["list_type"]}],
        "supports_requested_fields": False,
    },
    "meta.sector_list": {
        "query_shapes": [{"query_kind": "meta.sector_list", "selectors": [], "query_params": ["list_type"]}],
        "supports_requested_fields": False,
    },
    "meta.sector_stocks": {
        "query_shapes": [
            {
                "query_kind": "meta.sector_stocks",
                "selectors": ["block_code"],
                "query_params": ["block_type", "list_type"],
            }
        ],
        "supports_requested_fields": False,
    },
    "block.read_watchlist_snapshot": {
        "query_shapes": [
            {
                "query_kind": "block.read_watchlist_snapshot",
                "selectors": ["block_code"],
                "query_params": [],
            }
        ],
        "supports_requested_fields": False,
    },
    "meta.divid_factors": {
        "query_shapes": [{"query_kind": "meta.divid_factors", "selectors": ["symbol", "date_range"], "query_params": []}],
        "supports_requested_fields": False,
    },
    "meta.ipo_info": {
        "query_shapes": [{"query_kind": "meta.ipo_info", "selectors": [], "query_params": ["ipo_type", "ipo_date"]}],
        "supports_requested_fields": False,
    },
    "meta.gb_info": {
        "query_shapes": [{"query_kind": "meta.gb_info", "selectors": ["symbol"], "query_params": ["date_list", "count"]}],
        "supports_requested_fields": False,
    },
    "meta.gp_one_data": {
        "query_shapes": [{"query_kind": "meta.gp_one_data", "selectors": ["symbols"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "financial.financial_data": {
        "query_shapes": [
            {
                "query_kind": "financial.financial_data",
                "selectors": ["symbols", "date_range"],
                "query_params": ["report_type"],
            }
        ],
        "supports_requested_fields": True,
    },
    "financial.financial_data_by_date": {
        "query_shapes": [{"query_kind": "financial.financial_data_by_date", "selectors": ["symbols", "date"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "transaction.stock_transaction_data": {
        "query_shapes": [{"query_kind": "transaction.stock_transaction_data", "selectors": ["symbols", "date_range"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "transaction.stock_transaction_data_by_date": {
        "query_shapes": [{"query_kind": "transaction.stock_transaction_data_by_date", "selectors": ["symbols", "date"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "transaction.sector_transaction_data": {
        "query_shapes": [{"query_kind": "transaction.sector_transaction_data", "selectors": ["symbols", "date_range"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "transaction.sector_transaction_data_by_date": {
        "query_shapes": [{"query_kind": "transaction.sector_transaction_data_by_date", "selectors": ["symbols", "date"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "transaction.market_transaction_data": {
        "query_shapes": [{"query_kind": "transaction.market_transaction_data", "selectors": ["date_range"], "query_params": []}],
        "supports_requested_fields": True,
    },
    "transaction.market_transaction_data_by_date": {
        "query_shapes": [{"query_kind": "transaction.market_transaction_data_by_date", "selectors": ["date"], "query_params": []}],
        "supports_requested_fields": True,
    },
}

_QUERY_REPLAY_SUPPORTED_CAPABILITIES = {
    "market.snapshot",
    "market.stock_info",
    "market.more_info",
    "market.kline",
    "meta.stock_list",
    "meta.sector_stocks",
    "financial.financial_data",
    "financial.financial_data_by_date",
    "transaction.stock_transaction_data",
    "transaction.market_transaction_data",
    "block.read_watchlist_snapshot",
}


def get_query_discovery_metadata(capability: str) -> dict[str, Any] | None:
    config = _QUERY_CONTRACT_REGISTRY.get(capability)
    if config is None:
        return None
    return {
        "query_shapes": copy.deepcopy(config["query_shapes"]),
        "supports_requested_fields": bool(config["supports_requested_fields"]),
        "supports_empty_results": True,
        "supports_replay": capability in _QUERY_REPLAY_SUPPORTED_CAPABILITIES,
    }


def _extract_rows(data: dict[str, Any]) -> list[Any]:
    rows = data.get("rows")
    if isinstance(rows, list):
        return rows

    raw = data.get("result")
    if isinstance(raw, dict):
        payload_type = raw.get("type")
        if payload_type in {"dataframe", "series"} and isinstance(raw.get("records"), list):
            return list(raw["records"])
        return [raw]
    if isinstance(raw, list):
        return list(raw)
    return []


def _infer_returned_fields(rows: list[Any]) -> list[str]:
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in row.keys():
            normalized = str(key)
            if normalized in seen:
                continue
            seen.add(normalized)
            fields.append(normalized)
    return fields


def _normalize_requested_fields(requested_fields: list[str] | None) -> list[str]:
    if requested_fields is None:
        return []
    return [str(item) for item in requested_fields]


def _normalize_selectors(selectors: dict[str, Any] | None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in (selectors or {}).items():
        if key == "query_params":
            continue
        if value is None:
            continue
        payload[key] = copy.deepcopy(value)
    return payload


def _normalize_query_params(query_params: dict[str, Any] | None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in (query_params or {}).items():
        if value is None:
            continue
        payload[str(key)] = copy.deepcopy(value)
    return payload


def attach_query_contract(
    result: Result,
    *,
    capability: str,
    requested_fields: list[str] | None = None,
    selectors: dict[str, Any] | None = None,
    query_params: dict[str, Any] | None = None,
) -> Result:
    if capability not in _QUERY_CONTRACT_REGISTRY:
        return result

    rows = _extract_rows(result.data)
    if "rows" not in result.data:
        result.data["rows"] = rows

    query_meta = {
        "query_kind": capability,
        "row_count": len(rows),
        "requested_fields": _normalize_requested_fields(requested_fields),
        "returned_fields": _infer_returned_fields(rows),
    }
    query_meta.update(_normalize_selectors(selectors))
    query_meta["query_params"] = _normalize_query_params(query_params)
    result.data["query_meta"] = query_meta
    return result
