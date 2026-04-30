from __future__ import annotations

from datetime import date, datetime
from typing import Any


def _is_matched_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value) == 1.0
    if isinstance(value, str):
        return value.strip() == "1"
    return False


def _serialize_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _serialize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize_value(item) for item in value]
    return value


def _normalize_formula_points(raw_points: Any) -> tuple[list[dict[str, Any]], list[str]]:
    normalized_points: list[dict[str, Any]] = []
    matched_dates: list[str] = []
    if not isinstance(raw_points, list):
        return normalized_points, matched_dates
    for item in raw_points:
        if isinstance(item, dict):
            date_value = item.get("Date", item.get("date"))
            raw_value = item.get("Value", item.get("value"))
        else:
            date_value = None
            raw_value = item
        normalized_date = _serialize_value(date_value)
        point_matched = _is_matched_value(raw_value)
        if point_matched and isinstance(normalized_date, str):
            matched_dates.append(normalized_date)
        normalized_points.append(
            {
                "date": normalized_date,
                "value": _serialize_value(raw_value),
                "matched": point_matched,
            }
        )
    return normalized_points, matched_dates


def build_formula_screen_payload(
    raw_payload: Any,
    *,
    formula_name: str,
    stock_list: list[str],
    formula_arg: str = "",
    return_count: int = 1,
    return_date: bool = False,
    stock_period: str = "1d",
    start_time: str = "",
    end_time: str = "",
    count: int = 0,
    dividend_type: int = 0,
) -> dict[str, Any]:
    if not isinstance(raw_payload, dict):
        raise ValueError("formula screen raw payload must be a symbol-keyed JSON object")

    rows: list[dict[str, Any]] = []
    matched_symbols: list[str] = []
    unmatched_symbols: list[str] = []
    all_symbols = list(stock_list)
    for symbol in raw_payload.keys():
        if isinstance(symbol, str) and symbol not in all_symbols:
            all_symbols.append(symbol)

    for symbol in all_symbols:
        symbol_payload = raw_payload.get(symbol, {})
        field_names: list[str] = []
        row_matched_dates: list[str] = []
        series: list[dict[str, Any]] = []
        if isinstance(symbol_payload, dict):
            for field_name, field_points in symbol_payload.items():
                field_names.append(str(field_name))
                normalized_points, matched_dates = _normalize_formula_points(field_points)
                row_matched_dates.extend(matched_dates)
                series.append({"field": str(field_name), "points": normalized_points})

        deduped_dates: list[str] = []
        seen_dates: set[str] = set()
        for item in row_matched_dates:
            if item not in seen_dates:
                seen_dates.add(item)
                deduped_dates.append(item)
        matched = bool(deduped_dates)
        if matched:
            matched_symbols.append(symbol)
        else:
            unmatched_symbols.append(symbol)
        rows.append(
            {
                "symbol": symbol,
                "matched": matched,
                "field_names": field_names,
                "matched_dates": deduped_dates,
                "latest_match_date": deduped_dates[-1] if deduped_dates else None,
                "series": series,
            }
        )

    input_symbol_count = len(all_symbols)
    matched_symbol_count = len(matched_symbols)
    unmatched_symbol_count = len(unmatched_symbols)
    return {
        "input": {
            "formula_name": formula_name,
            "formula_arg": formula_arg,
            "stock_list": all_symbols,
            "return_count": return_count,
            "return_date": return_date,
            "stock_period": stock_period,
            "start_time": start_time,
            "end_time": end_time,
            "count": count,
            "dividend_type": dividend_type,
        },
        "summary": {
            "input_symbol_count": input_symbol_count,
            "result_symbol_count": len(rows),
            "matched_symbol_count": matched_symbol_count,
            "unmatched_symbol_count": unmatched_symbol_count,
            "match_rate": round(matched_symbol_count / input_symbol_count, 6) if input_symbol_count else 0.0,
        },
        "matched_symbols": matched_symbols,
        "unmatched_symbols": unmatched_symbols,
        "rows": rows,
    }
