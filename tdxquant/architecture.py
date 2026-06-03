from __future__ import annotations

from enum import Enum
from typing import Any


class CapabilityRisk(str, Enum):
    READ_ONLY_QUERY = "read_only_query"
    PROVIDER_MUTATION = "provider_mutation"
    NATIVE_TRADE_MUTATION = "native_trade_mutation"
    DESKTOP_TRADE_MUTATION = "desktop_trade_mutation"
    DIAGNOSTIC = "diagnostic"
    UNKNOWN = "unknown"


_READ_ONLY_PREFIXES = (
    "market.",
    "meta.",
    "financial.",
    "transaction.",
    "formula.",
    "runtime.",
    "subscription.",
)
_PROVIDER_MUTATION_PREFIXES = ("block.",)
_NATIVE_TRADE_MUTATION_PREFIXES = ("trade.",)
_DESKTOP_TRADE_MUTATION_PREFIXES = (
    "desktop_trade.",
    "pingan.",
)

_READ_ONLY_CAPABILITIES = {
    "block.user_sectors",
    "block.read_watchlist_snapshot",
}
_PROVIDER_MUTATION_CAPABILITIES = {
    "block.create_sector",
    "block.delete_sector",
    "block.rename_sector",
    "block.clear_sector",
    "block.send_user_block",
    "block.sync_watchlist",
}
_DIAGNOSTIC_CAPABILITIES = {
    "provider.capabilities",
    "provider.health",
    "provider.doctor",
    "trade.broker_capabilities",
}


def classify_capability_risk(capability: str) -> CapabilityRisk:
    normalized = capability.strip()
    if not normalized:
        return CapabilityRisk.UNKNOWN
    if normalized in _DIAGNOSTIC_CAPABILITIES:
        return CapabilityRisk.DIAGNOSTIC
    if normalized in _READ_ONLY_CAPABILITIES:
        return CapabilityRisk.READ_ONLY_QUERY
    if normalized in _PROVIDER_MUTATION_CAPABILITIES:
        return CapabilityRisk.PROVIDER_MUTATION
    if normalized.startswith(_DESKTOP_TRADE_MUTATION_PREFIXES):
        return CapabilityRisk.DESKTOP_TRADE_MUTATION
    if normalized.startswith(_NATIVE_TRADE_MUTATION_PREFIXES):
        return CapabilityRisk.NATIVE_TRADE_MUTATION
    if normalized.startswith(_PROVIDER_MUTATION_PREFIXES):
        return CapabilityRisk.PROVIDER_MUTATION
    if normalized.startswith(_READ_ONLY_PREFIXES):
        return CapabilityRisk.READ_ONLY_QUERY
    return CapabilityRisk.UNKNOWN


def build_capability_risk_metadata(capability: str) -> dict[str, Any]:
    risk = classify_capability_risk(capability)
    return {
        "capability": capability,
        "risk": risk.value,
        "read_only": risk in {CapabilityRisk.READ_ONLY_QUERY, CapabilityRisk.DIAGNOSTIC},
        "mutation": risk
        in {
            CapabilityRisk.PROVIDER_MUTATION,
            CapabilityRisk.NATIVE_TRADE_MUTATION,
            CapabilityRisk.DESKTOP_TRADE_MUTATION,
        },
    }
