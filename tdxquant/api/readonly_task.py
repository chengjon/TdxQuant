from __future__ import annotations

import copy
import time
from dataclasses import dataclass
from typing import Any, Mapping

from ..models import Result


def _capture_readonly_task_timing(step_name: str, fn: Any) -> tuple[Any, dict[str, Any]]:
    started_at = time.perf_counter()
    value = fn()
    total_ms = round((time.perf_counter() - started_at) * 1000, 3)
    return value, {"task_call": {"name": step_name, "total_ms": total_ms}}


@dataclass(frozen=True)
class ReadOnlyTaskBoundary:
    api_manager: Any
    profile_name: str
    profile_options: Mapping[str, Any]

    def _attach_task_metadata(self, result: Result, *, task_name: str, timing: dict[str, Any]) -> Result:
        result.data["task"] = {
            "entrypoint": "TdxTaskManager",
            "name": task_name,
        }
        result.data["task_profile"] = {
            "name": self.profile_name,
            "options": copy.deepcopy(dict(self.profile_options)),
        }
        result.data.setdefault("timing", {}).update(timing)
        return result

    def watchlist_overview(self, *, stock_list: list[str], fields: list[str] | None = None) -> Result:
        resolved_fields = list(fields) if fields is not None else list(self.profile_options.get("gp_one_fields", []))
        result, timing = _capture_readonly_task_timing(
            "task.watchlist_overview",
            lambda: self.api_manager.meta.gp_one_data(stock_list=stock_list, fields=resolved_fields),
        )
        result.data.setdefault(
            "input",
            {
                "stock_list": stock_list,
                "fields": resolved_fields,
            },
        )
        return self._attach_task_metadata(result, task_name="watchlist_overview", timing=timing)
