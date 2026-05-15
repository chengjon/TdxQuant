from pathlib import Path
from unittest.mock import patch

from tdxquant.trade import TdxTradeManager
from tdxquant.trade.extended_capabilities import (
    PINGAN_DESKTOP_EXTENDED_BROKER_CAPABILITIES_RISK_DOC,
    build_pingan_desktop_extended_broker_capability_probe,
)
from tdxquant.trader.models import GatewayCapabilities


def test_pingan_desktop_extended_broker_capability_probe_marks_boundaries() -> None:
    payload = build_pingan_desktop_extended_broker_capability_probe(generated_at="2026-05-15T00:00:00+00:00")

    assert payload["schema_version"] == "tdx.desktop_trade.extended_broker_capabilities.v1"
    assert payload["broker"] == "pingan_desktop"
    assert payload["overall_status"] == "boundary_only"
    assert payload["risk_document"] == PINGAN_DESKTOP_EXTENDED_BROKER_CAPABILITIES_RISK_DOC

    capabilities = payload["capabilities"]
    assert set(capabilities) == {"funds", "positions", "cancel_order", "broker_native_push"}

    assert capabilities["funds"]["status"] == "unsupported"
    assert capabilities["funds"]["side_effect"] == "none"
    assert capabilities["funds"]["probe_mode"] == "read_only_metadata"
    assert capabilities["funds"]["evidence"]["capability_flag"] == "supports_account_query"
    assert capabilities["funds"]["boundary"]

    assert capabilities["positions"]["status"] == "unsupported"
    assert capabilities["positions"]["side_effect"] == "none"
    assert capabilities["positions"]["probe_mode"] == "read_only_metadata"
    assert capabilities["positions"]["evidence"]["capability_flag"] == "supports_position_query"

    assert capabilities["cancel_order"]["status"] == "unsupported"
    assert capabilities["cancel_order"]["side_effect"] == "broker_state_mutating"
    assert capabilities["cancel_order"]["probe_mode"] == "classification_only"
    assert "does not submit a cancel request" in capabilities["cancel_order"]["boundary"]

    assert capabilities["broker_native_push"]["status"] == "unsupported"
    assert capabilities["broker_native_push"]["side_effect"] == "none"
    assert capabilities["broker_native_push"]["probe_mode"] == "feasibility_boundary"
    assert capabilities["broker_native_push"]["evidence"]["capability_flag"] == "supports_push_events"
    assert "provider event streams" in capabilities["broker_native_push"]["boundary"]


def test_pingan_desktop_extended_broker_capability_probe_projects_supported_flags() -> None:
    payload = build_pingan_desktop_extended_broker_capability_probe(
        capabilities=GatewayCapabilities(
            supports_cancel=True,
            supports_account_query=True,
            supports_position_query=True,
            supports_push_events=True,
            supports_order_sync=False,
            supports_trade_sync=False,
        ),
        generated_at="2026-05-15T00:00:00+00:00",
    )

    capabilities = payload["capabilities"]
    assert payload["overall_status"] == "partial"
    assert capabilities["funds"]["status"] == "available"
    assert capabilities["positions"]["status"] == "available"
    assert capabilities["cancel_order"]["status"] == "available"
    assert capabilities["cancel_order"]["side_effect"] == "broker_state_mutating"
    assert capabilities["broker_native_push"]["status"] == "available"


def test_trade_manager_extended_broker_capabilities_does_not_touch_live_broker() -> None:
    manager = TdxTradeManager()

    with patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", side_effect=AssertionError("live broker touched")):
        result = manager.pingan.extended_broker_capabilities(generated_at="2026-05-15T00:00:00+00:00")

    assert result.ok
    assert result.data["manager"]["method"] == "extended_broker_capabilities"
    assert result.data["broker_capabilities"]["capabilities"]["cancel_order"]["side_effect"] == "broker_state_mutating"
    assert result.data["broker_capabilities"]["capabilities"]["funds"]["side_effect"] == "none"


def test_extended_broker_capabilities_risk_document_exists() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    risk_document = repo_root / PINGAN_DESKTOP_EXTENDED_BROKER_CAPABILITIES_RISK_DOC

    assert risk_document.is_file()
    text = risk_document.read_text(encoding="utf-8")
    assert "read-only" in text
    assert "local-state-mutating" in text
    assert "broker-state-mutating" in text
