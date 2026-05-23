from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


PROVIDER_CONTRACT_STABLE = "provider_contract_stable"
BRIDGE_ONLY = "bridge_only"


@dataclass(frozen=True, slots=True)
class FormulaCapabilityContract:
    capability: str
    manager_method: str
    status: str
    provider_contract_stable: bool
    replay_supported: bool
    evidence: tuple[str, ...]
    boundary: str
    replay_fixtures: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "manager_method": self.manager_method,
            "status": self.status,
            "provider_contract_stable": self.provider_contract_stable,
            "replay_supported": self.replay_supported,
            "replay_fixtures": list(self.replay_fixtures),
            "evidence": list(self.evidence),
            "boundary": self.boundary,
        }


_FORMULA_CAPABILITIES: tuple[FormulaCapabilityContract, ...] = (
    FormulaCapabilityContract(
        capability="formula.screen",
        manager_method="screen",
        status=PROVIDER_CONTRACT_STABLE,
        provider_contract_stable=True,
        replay_supported=True,
        replay_fixtures=("formula-screen-success", "formula-screen-failure"),
        evidence=(
            "tdxquant/formula_screen.py",
            "tdxquant/fixtures/provider/formula-screen-success.json",
            "tdxquant/fixtures/provider/formula-screen-failure.json",
            "openspec/specs/tdx-provider-formula-screen/spec.md",
            "tests/test_api_manager.py",
        ),
        boundary="Stable provider/replay contract for normalized batch stock-screen output; real execution still requires a Windows TongDaXin environment.",
    ),
    FormulaCapabilityContract(
        capability="formula.format_data",
        manager_method="format_data",
        status=BRIDGE_ONLY,
        provider_contract_stable=False,
        replay_supported=False,
        evidence=("tdxquant/api/formula.py", "tdxquant/api/manager.py"),
        boundary="Legacy bridge-only helper; not available as a stable provider/replay contract and has no replay fixture.",
    ),
    FormulaCapabilityContract(
        capability="formula.set_data",
        manager_method="set_data",
        status=BRIDGE_ONLY,
        provider_contract_stable=False,
        replay_supported=False,
        evidence=("tdxquant/api/formula.py", "tdxquant/api/manager.py"),
        boundary="Legacy bridge-only helper; not available as a stable provider/replay contract and has no replay fixture.",
    ),
    FormulaCapabilityContract(
        capability="formula.set_data_info",
        manager_method="set_data_info",
        status=BRIDGE_ONLY,
        provider_contract_stable=False,
        replay_supported=False,
        evidence=("tdxquant/api/formula.py", "tdxquant/api/manager.py"),
        boundary="Legacy bridge-only helper; not available as a stable provider/replay contract and has no replay fixture.",
    ),
    FormulaCapabilityContract(
        capability="formula.get_data",
        manager_method="get_data",
        status=BRIDGE_ONLY,
        provider_contract_stable=False,
        replay_supported=False,
        evidence=("tdxquant/api/formula.py", "tdxquant/api/manager.py"),
        boundary="Legacy bridge-only formula data access; not available as a stable provider/replay contract and has no replay fixture.",
    ),
    FormulaCapabilityContract(
        capability="formula.zb",
        manager_method="zb",
        status=BRIDGE_ONLY,
        provider_contract_stable=False,
        replay_supported=False,
        evidence=("tdxquant/api/formula.py", "tdxquant/api/manager.py"),
        boundary="Legacy bridge-only indicator formula execution; not available as a stable provider/replay contract and has no replay fixture.",
    ),
    FormulaCapabilityContract(
        capability="formula.xg",
        manager_method="xg",
        status=BRIDGE_ONLY,
        provider_contract_stable=False,
        replay_supported=False,
        evidence=("tdxquant/api/formula.py", "tdxquant/api/manager.py"),
        boundary="Legacy bridge-only stock-selection formula execution; not available as a stable provider/replay contract and has no replay fixture.",
    ),
    FormulaCapabilityContract(
        capability="formula.exp",
        manager_method="exp",
        status=BRIDGE_ONLY,
        provider_contract_stable=False,
        replay_supported=False,
        evidence=("tdxquant/api/formula.py", "tdxquant/api/manager.py"),
        boundary="Legacy bridge-only formula export path; not available as a stable provider/replay contract and has no replay fixture.",
    ),
    FormulaCapabilityContract(
        capability="formula.process_mul_xg",
        manager_method="process_mul_xg",
        status=BRIDGE_ONLY,
        provider_contract_stable=False,
        replay_supported=False,
        evidence=("tdxquant/api/formula.py", "tdxquant/api/manager.py"),
        boundary="Legacy bridge-only multi-stock xg formula execution; not available as a stable provider/replay contract and has no replay fixture.",
    ),
    FormulaCapabilityContract(
        capability="formula.process_mul_zb",
        manager_method="process_mul_zb",
        status=BRIDGE_ONLY,
        provider_contract_stable=False,
        replay_supported=False,
        evidence=("tdxquant/api/formula.py", "tdxquant/api/manager.py"),
        boundary="Legacy bridge-only multi-stock indicator formula execution; not available as a stable provider/replay contract and has no replay fixture.",
    ),
)


def list_formula_capability_contracts() -> list[dict[str, Any]]:
    return [item.to_dict() for item in _FORMULA_CAPABILITIES]


def summarize_formula_capability_contracts(capabilities: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total": len(capabilities),
        "provider_contract_stable": sum(1 for item in capabilities if item["provider_contract_stable"]),
        "bridge_only": sum(1 for item in capabilities if item["status"] == BRIDGE_ONLY),
        "replay_supported": sum(1 for item in capabilities if item["replay_supported"]),
    }


def build_formula_capability_registry() -> dict[str, Any]:
    capabilities = list_formula_capability_contracts()
    return {
        "capabilities": capabilities,
        "summary": summarize_formula_capability_contracts(capabilities),
    }
