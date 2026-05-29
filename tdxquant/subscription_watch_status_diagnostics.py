from __future__ import annotations

from typing import Any


def build_subscription_watch_status_diagnostics(summary_view: dict[str, Any]) -> dict[str, Any]:
    """Build compact diagnostics flags from the existing watch-status summary view."""
    status_summary = summary_view.get("status_summary")
    status_summary = status_summary if isinstance(status_summary, dict) else {}
    governance = summary_view.get("governance")
    governance = governance if isinstance(governance, dict) else {}

    control_rollup = status_summary.get("control_rollup")
    control_rollup = control_rollup if isinstance(control_rollup, dict) else {}
    consistency_rollup = status_summary.get("consistency_rollup")
    consistency_rollup = consistency_rollup if isinstance(consistency_rollup, dict) else {}
    reconnect_rollup = governance.get("reconnect_rollup")
    reconnect_rollup = reconnect_rollup if isinstance(reconnect_rollup, dict) else {}
    evaluation_rollup = governance.get("evaluation_summary")
    evaluation_rollup = evaluation_rollup if isinstance(evaluation_rollup, dict) else {}

    return {
        "has_control_rollup": bool(control_rollup),
        "has_consistency_rollup": bool(consistency_rollup),
        "has_reconnect_rollup": bool(reconnect_rollup),
        "has_evaluation_rollup": bool(evaluation_rollup),
        "has_mismatch": bool(consistency_rollup.get("has_mismatch")),
        "requires_manual_review": bool(governance.get("requires_manual_review")),
        "staleness_evaluated": bool(governance.get("staleness_evaluated")),
        "has_reconnect_failures": bool(reconnect_rollup.get("has_reconnect_failures")),
        "has_reconnect_last_error": bool(reconnect_rollup.get("has_last_error")),
        "has_stale_component": bool(evaluation_rollup.get("has_stale_component")),
        "has_not_evaluated_component": bool(evaluation_rollup.get("has_not_evaluated_component")),
        "all_components_evaluated": bool(evaluation_rollup.get("all_components_evaluated")),
        "boundary": governance.get("boundary"),
    }
