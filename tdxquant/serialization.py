from __future__ import annotations

from datetime import date, datetime
from typing import Any

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None


def _serialize_scalar(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if np is not None and isinstance(value, np.generic):
        return value.item()
    return value


def serialize_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if np is not None and isinstance(value, np.generic):
        return value.item()
    if pd is not None and isinstance(value, pd.Timestamp):
        return value.isoformat()
    if pd is not None and value is pd.NaT:
        return None
    if pd is not None and isinstance(value, pd.DataFrame):
        frame = value.copy()
        index_name = frame.index.name or "index"
        frame = frame.reset_index()
        records = [{k: serialize_value(v) for k, v in row.items()} for row in frame.to_dict(orient="records")]
        return {
            "type": "dataframe",
            "index_name": index_name,
            "records": records,
        }
    if pd is not None and isinstance(value, pd.Series):
        name = value.name or "value"
        index_name = value.index.name or "index"
        records = []
        for idx, item in value.items():
            records.append({index_name: serialize_value(idx), name: serialize_value(item)})
        return {
            "type": "series",
            "name": name,
            "index_name": index_name,
            "records": records,
        }
    if isinstance(value, dict):
        return {str(k): serialize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serialize_value(item) for item in value]
    return _serialize_scalar(value)
