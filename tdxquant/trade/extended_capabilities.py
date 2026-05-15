from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ..trader.models import GatewayCapabilities

PINGAN_DESKTOP_EXTENDED_BROKER_CAPABILITIES_SCHEMA = "tdx.desktop_trade.extended_broker_capabilities.v1"
PINGAN_DESKTOP_EXTENDED_BROKER_CAPABILITIES_RISK_DOC = (
    "docs/trading/desktop_trade_extended_broker_capabilities_risk.md"
)


def build_pingan_desktop_gateway_capabilities() -> GatewayCapabilities:
    return GatewayCapabilities(
        supports_cancel=False,
        supports_account_query=False,
        supports_position_query=False,
        supports_push_events=False,
        supports_order_sync=False,
        supports_trade_sync=False,
    )


def build_pingan_desktop_extended_broker_capability_probe(
    *,
    capabilities: GatewayCapabilities | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    resolved = capabilities or build_pingan_desktop_gateway_capabilities()
    generated = generated_at or datetime.now(UTC).isoformat()
    supported_flags = (
        resolved.supports_account_query,
        resolved.supports_position_query,
        resolved.supports_cancel,
        resolved.supports_push_events,
    )
    return {
        "schema_version": PINGAN_DESKTOP_EXTENDED_BROKER_CAPABILITIES_SCHEMA,
        "broker": "pingan_desktop",
        "adapter": "PingAnDesktopTraderGateway",
        "generated_at": generated,
        "overall_status": "partial" if any(supported_flags) else "boundary_only",
        "risk_document": PINGAN_DESKTOP_EXTENDED_BROKER_CAPABILITIES_RISK_DOC,
        "capabilities": {
            "funds": _read_only_entry(
                flag_name="supports_account_query",
                supported=resolved.supports_account_query,
                boundary="The probe reports account-query capability metadata only; it does not extract balances, available cash, account identifiers, or broker screen contents.",
            ),
            "positions": _read_only_entry(
                flag_name="supports_position_query",
                supported=resolved.supports_position_query,
                boundary="The probe reports position-query capability metadata only; it does not extract holdings, lots, costs, market values, or broker screen contents.",
            ),
            "cancel_order": {
                "status": _status(resolved.supports_cancel),
                "probe_mode": "classification_only",
                "side_effect": "broker_state_mutating",
                "evidence": _evidence("supports_cancel", resolved.supports_cancel),
                "boundary": "The probe classifies cancel-order risk only and does not submit a cancel request; any future cancel execution requires a separate broker-state-mutating workflow and explicit risk gate.",
            },
            "broker_native_push": {
                "status": _status(resolved.supports_push_events),
                "probe_mode": "feasibility_boundary",
                "side_effect": "none",
                "evidence": _evidence("supports_push_events", resolved.supports_push_events),
                "boundary": "No broker-native desktop event source is integrated; existing provider event streams and SSE projections do not satisfy broker-native push support.",
            },
        },
        "non_scope": [
            "No live funds query is executed.",
            "No live positions query is executed.",
            "No cancel order request is submitted.",
            "No broker-native push subscription is opened.",
            "This probe is not part of the query-oriented api namespace.",
        ],
    }


def _read_only_entry(*, flag_name: str, supported: bool, boundary: str) -> dict[str, Any]:
    return {
        "status": _status(supported),
        "probe_mode": "read_only_metadata",
        "side_effect": "none",
        "evidence": _evidence(flag_name, supported),
        "boundary": boundary,
    }


def _status(supported: bool) -> str:
    return "available" if supported else "unsupported"


def _evidence(flag_name: str, supported: bool) -> dict[str, Any]:
    return {
        "adapter": "PingAnDesktopTraderGateway",
        "source": "GatewayCapabilities",
        "capability_flag": flag_name,
        "supported": supported,
    }
