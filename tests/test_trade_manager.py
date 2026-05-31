import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tdxquant import TdxTradeManager
from tdxquant.models import ErrorCode, Result
from tdxquant.trade.context import get_trade_profile_path, load_trade_profiles, resolve_trade_profile
from tdxquant.trade.preset import get_trade_preset_path, load_trade_presets, resolve_trade_preset


class TradeProfileTests(unittest.TestCase):
    def test_get_trade_profile_path_is_absolute(self) -> None:
        self.assertTrue(get_trade_profile_path().is_absolute())
        self.assertEqual(get_trade_profile_path().name, "trade-profiles.json")

    def test_load_trade_profiles_reads_json_object(self) -> None:
        with TemporaryDirectory() as temp_dir:
            profile_path = Path(temp_dir) / "trade-profiles.json"
            profile_path.write_text(json.dumps({"balanced": {"post_delay": 0.2}}), encoding="utf-8")
            profiles = load_trade_profiles(profile_path)
        self.assertEqual(profiles["balanced"]["post_delay"], 0.2)

    def test_resolve_trade_profile_prefers_explicit_overrides(self) -> None:
        profiles = {"balanced": {"post_delay": 0.2, "capture_final_uia": False}}
        resolved = resolve_trade_profile("balanced", overrides={"post_delay": 0.1}, profiles=profiles)
        self.assertEqual(resolved["post_delay"], 0.1)
        self.assertFalse(resolved["capture_final_uia"])

    def test_get_trade_preset_path_is_absolute(self) -> None:
        self.assertTrue(get_trade_preset_path().is_absolute())
        self.assertEqual(get_trade_preset_path().name, "trade-presets.json")

    def test_load_trade_presets_reads_json_object(self) -> None:
        with TemporaryDirectory() as temp_dir:
            preset_path = Path(temp_dir) / "trade-presets.json"
            preset_path.write_text(json.dumps({"turbo-buy": {"command": "buy", "options": {"port": "COM3"}}}), encoding="utf-8")
            presets = load_trade_presets(preset_path)
        self.assertEqual(presets["turbo-buy"]["command"], "buy")

    def test_resolve_trade_preset_prefers_explicit_overrides(self) -> None:
        presets = {
            "turbo-buy": {
                "command": "buy",
                "profile": "turbo",
                "title_key": "平安证券",
                "options": {"port": "COM3", "max_depth": 12},
            }
        }
        resolved = resolve_trade_preset("turbo-buy", overrides={"options": {"port": "COM9"}}, presets=presets)
        self.assertEqual(resolved["command"], "buy")
        self.assertEqual(resolved["profile"], "turbo")
        self.assertEqual(resolved["options"]["port"], "COM9")
        self.assertEqual(resolved["options"]["max_depth"], 12)


class TdxTradeManagerTests(unittest.TestCase):
    def test_public_import_is_available(self) -> None:
        manager = TdxTradeManager(profile="balanced")
        self.assertEqual(manager.profile_name, "balanced")

    def test_pingan_buy_attaches_metadata_and_writes_artifacts(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "result_dialog": {"contract_no": "B202604260001"},
            },
        )
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "pingan-last-order.json"
            log_path = Path(temp_dir) / "pingan-order-events.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with patch("tdxquant.trade.manager.run_pingan_buy_fast", return_value=expected) as mocked:
                manager = TdxTradeManager(
                    profile="turbo",
                    title_keyword="平安证券",
                    exe_path=r"D:\ProgramData\PinganSec\TdxW.exe",
                    state_path=str(state_path),
                    event_log_path=str(log_path),
                    submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="buy-20260428-001",
                    max_price=10.50,
                )
            self.assertTrue(state_path.exists())
            self.assertTrue(log_path.exists())
            state_payload = json.loads(state_path.read_text(encoding="utf-8"))
            event_row = json.loads(log_path.read_text(encoding="utf-8").splitlines()[-1])
            audit_path = Path(result.data["artifacts"]["trade_audit_path"])
            audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertEqual(state_payload["contract_no"], "B202604260001")
            self.assertEqual(state_payload["trade_safety"]["submission_key"], "buy-20260428-001")
            self.assertEqual(event_row["trade_safety"]["submission_key"], "buy-20260428-001")
            self.assertEqual(result.data["trade_audit"]["status"], "confirmed")
            self.assertEqual(state_payload["trade_audit"]["audit_id"], result.data["trade_audit"]["audit_id"])
            self.assertEqual(event_row["trade_audit"]["audit_id"], result.data["trade_audit"]["audit_id"])
            self.assertEqual(audit_payload["trade_audit"]["audit_id"], result.data["trade_audit"]["audit_id"])
            self.assertEqual(audit_payload["trade_audit"]["status"], "confirmed")
            audit_gate = result.data["trade_audit_gate_status"]
            self.assertEqual(audit_gate["schema_version"], "tdx.desktop_trade.pingan_trade_audit_gate_status.v1")
            self.assertEqual(audit_gate["status"], "partial")
            self.assertEqual(audit_gate["covered_audit_status"], "confirmed")
            self.assertEqual(audit_gate["audit_id"], result.data["trade_audit"]["audit_id"])
            self.assertEqual(audit_gate["artifact_paths"]["trade_audit_path"], str(audit_path))
            self.assertTrue(audit_gate["persisted_artifacts"]["last_order_state"])
            self.assertTrue(audit_gate["persisted_artifacts"]["order_event_log"])
            self.assertTrue(audit_gate["persisted_artifacts"]["submission_ledger"])
            self.assertTrue(audit_gate["persisted_artifacts"]["trade_audit"])
            self.assertIn("rejected", audit_gate["remaining_audit_gate_statuses"])
            self.assertIn("exception", audit_gate["remaining_audit_gate_statuses"])
        mocked.assert_called_once()
        self.assertEqual(result.data["manager"]["entrypoint"], "TdxTradeManager")
        self.assertEqual(result.data["manager"]["broker"], "pingan")
        self.assertEqual(result.data["manager"]["method"], "buy")
        self.assertEqual(result.data["trade_profile"]["name"], "turbo")
        self.assertEqual(result.data["trade_safety"]["stability"], "beta")
        self.assertEqual(result.data["trade_safety"]["side_effect_level"], "live_side_effecting")
        self.assertEqual(result.data["trade_safety"]["submission_key"], "buy-20260428-001")
        self.assertTrue(result.data["trade_safety"]["risk_gate"]["passed"])
        self.assertIn("manager_call", result.data["timing"])

    def test_pingan_buy_submit_once_uses_submit_once_profile(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "result_dialog": {"contract_no": "B202604260002"},
            },
        )
        with TemporaryDirectory() as temp_dir:
            with patch("tdxquant.trade.manager.run_pingan_buy_submit_once", return_value=expected) as mocked:
                manager = TdxTradeManager(
                    profile="submit_once",
                    state_path=str(Path(temp_dir) / "state.json"),
                    event_log_path=str(Path(temp_dir) / "events.jsonl"),
                    submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
                )
                result = manager.pingan.buy_submit_once(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="submit-once-20260428-001",
                    max_price=10.50,
                )
        mocked.assert_called_once()
        self.assertEqual(result.data["manager"]["method"], "buy_submit_once")
        self.assertEqual(result.data["trade_profile"]["name"], "submit_once")
        self.assertEqual(result.data["trade_safety"]["submission_key"], "submit-once-20260428-001")
        self.assertTrue(result.data["trade_safety"]["risk_gate"]["passed"])

    def test_pingan_buy_submit_once_requires_broker_readiness_before_desktop_execution(self) -> None:
        broker_health = Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="runtime path resolved but trading window was not found",
            data={"runtime": {"ok": True}, "window": {"ok": False}},
            next_action="Bring Ping An to the foreground and retry.",
        )
        with TemporaryDirectory() as temp_dir:
            manager = TdxTradeManager(
                profile="submit_once",
                state_path=str(Path(temp_dir) / "state.json"),
                event_log_path=str(Path(temp_dir) / "events.jsonl"),
                submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
            )
            with (
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health) as mocked_health,
                patch("tdxquant.trade.manager.run_pingan_buy_submit_once") as mocked_buy,
            ):
                result = manager.pingan.buy_submit_once(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="buy-submit-once-broker-readiness-required-001",
                    max_price=10.50,
                    require_broker_readiness=True,
                )

        mocked_health.assert_called_once()
        mocked_buy.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        risk_gate = result.data["trade_safety"]["risk_gate"]
        self.assertFalse(risk_gate["passed"])
        readiness = risk_gate["broker_readiness_required_status"]
        self.assertTrue(readiness["required"])
        self.assertEqual(readiness["requirement_status"], "failed")
        self.assertFalse(readiness["broker_health_ok"])
        self.assertFalse(readiness["control_dispatch_executed"])
        self.assertFalse(readiness["order_submitted"])

    def test_pingan_sell_submit_once_uses_sell_flow_with_submit_once_identity(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "result_dialog": {"contract_no": "S202604260002"},
            },
        )
        with TemporaryDirectory() as temp_dir:
            with patch("tdxquant.trade.manager.run_pingan_sell_fast", return_value=expected) as mocked:
                manager = TdxTradeManager(
                    profile="submit_once",
                    state_path=str(Path(temp_dir) / "state.json"),
                    event_log_path=str(Path(temp_dir) / "events.jsonl"),
                    submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
                )
                result = manager.pingan.sell_submit_once(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="sell-submit-once-20260428-001",
                    max_price=10.50,
                )
        mocked.assert_called_once()
        self.assertEqual(result.data["manager"]["method"], "sell_submit_once")
        self.assertEqual(result.data["trade_profile"]["name"], "submit_once")
        self.assertEqual(result.data["trade_safety"]["submission_key"], "sell-submit-once-20260428-001")
        self.assertTrue(result.data["trade_safety"]["risk_gate"]["passed"])

    def test_pingan_sell_submit_once_requires_broker_readiness_before_desktop_execution(self) -> None:
        broker_health = Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="runtime path resolved but trading window was not found",
            data={"runtime": {"ok": True}, "window": {"ok": False}},
            next_action="Bring Ping An to the foreground and retry.",
        )
        with TemporaryDirectory() as temp_dir:
            manager = TdxTradeManager(
                profile="submit_once",
                state_path=str(Path(temp_dir) / "state.json"),
                event_log_path=str(Path(temp_dir) / "events.jsonl"),
                submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
            )
            with (
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health) as mocked_health,
                patch("tdxquant.trade.manager.run_pingan_sell_fast") as mocked_sell,
            ):
                result = manager.pingan.sell_submit_once(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="sell-submit-once-broker-readiness-required-001",
                    max_price=10.50,
                    require_broker_readiness=True,
                )

        mocked_health.assert_called_once()
        mocked_sell.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        risk_gate = result.data["trade_safety"]["risk_gate"]
        self.assertFalse(risk_gate["passed"])
        readiness = risk_gate["broker_readiness_required_status"]
        self.assertTrue(readiness["required"])
        self.assertEqual(readiness["requirement_status"], "failed")
        self.assertFalse(readiness["broker_health_ok"])
        self.assertFalse(readiness["control_dispatch_executed"])
        self.assertFalse(readiness["order_submitted"])

    def test_pingan_sell_attaches_metadata_and_writes_artifacts(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "result_dialog": {"contract_no": "S202604260001"},
            },
        )
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "pingan-last-order.json"
            log_path = Path(temp_dir) / "pingan-order-events.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with patch("tdxquant.trade.manager.run_pingan_sell_fast", return_value=expected) as mocked:
                manager = TdxTradeManager(
                    profile="turbo",
                    title_keyword="平安证券",
                    exe_path=r"D:\ProgramData\PinganSec\TdxW.exe",
                    state_path=str(state_path),
                    event_log_path=str(log_path),
                    submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.sell(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="sell-20260430-001",
                    max_price=10.50,
                )
            self.assertTrue(state_path.exists())
            self.assertTrue(log_path.exists())
            state_payload = json.loads(state_path.read_text(encoding="utf-8"))
            event_row = json.loads(log_path.read_text(encoding="utf-8").splitlines()[-1])
            audit_path = Path(result.data["artifacts"]["trade_audit_path"])
            audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertEqual(state_payload["contract_no"], "S202604260001")
            self.assertEqual(state_payload["trade_safety"]["submission_key"], "sell-20260430-001")
            self.assertEqual(event_row["trade_safety"]["submission_key"], "sell-20260430-001")
            self.assertEqual(result.data["trade_audit"]["status"], "confirmed")
            self.assertEqual(audit_payload["trade_audit"]["status"], "confirmed")
        mocked.assert_called_once()
        self.assertEqual(result.data["manager"]["broker"], "pingan")
        self.assertEqual(result.data["manager"]["method"], "sell")
        self.assertEqual(result.data["trade_profile"]["name"], "turbo")
        self.assertEqual(result.data["trade_safety"]["submission_key"], "sell-20260430-001")
        self.assertTrue(result.data["trade_safety"]["risk_gate"]["passed"])

    def test_pingan_sell_requires_broker_readiness_before_desktop_execution(self) -> None:
        broker_health = Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="runtime path resolved but trading window was not found",
            data={"runtime": {"ok": True}, "window": {"ok": False}},
            next_action="Bring Ping An to the foreground and retry.",
        )
        with TemporaryDirectory() as temp_dir:
            manager = TdxTradeManager(
                profile="balanced",
                state_path=str(Path(temp_dir) / "state.json"),
                event_log_path=str(Path(temp_dir) / "events.jsonl"),
                submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
            )
            with (
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health) as mocked_health,
                patch("tdxquant.trade.manager.run_pingan_sell_fast") as mocked_sell,
            ):
                result = manager.pingan.sell(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="sell-broker-readiness-required-001",
                    max_price=10.50,
                    require_broker_readiness=True,
                )

        mocked_health.assert_called_once()
        mocked_sell.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        risk_gate = result.data["trade_safety"]["risk_gate"]
        self.assertFalse(risk_gate["passed"])
        readiness = risk_gate["broker_readiness_required_status"]
        self.assertTrue(readiness["required"])
        self.assertEqual(readiness["requirement_status"], "failed")
        self.assertFalse(readiness["broker_health_ok"])
        self.assertFalse(readiness["control_dispatch_executed"])
        self.assertFalse(readiness["order_submitted"])

    def test_pingan_buy_rejects_required_lifecycle_owner_lock_before_desktop_execution(self) -> None:
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            with patch("tdxquant.trade.manager.run_pingan_buy_fast") as mocked:
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                )
                result = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="buy-owner-lock-required-001",
                    max_price=10.50,
                    lifecycle_statefile_path=str(lifecycle_statefile_path),
                    lifecycle_owner_token="execution-owner",
                    lifecycle_stale_after_seconds=999.0,
                    require_lifecycle_owner_lock=True,
                )

        mocked.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        risk_gate = result.data["trade_safety"]["risk_gate"]
        self.assertFalse(risk_gate["passed"])
        self.assertEqual(risk_gate["rejection_reason"], "lifecycle_owner_lock_status_not_acquired")
        owner_lock = risk_gate["lifecycle_owner_lock_required_status"]
        self.assertTrue(owner_lock["required"])
        self.assertEqual(owner_lock["requirement_status"], "failed")
        self.assertEqual(owner_lock["status"], "not_acquired")
        self.assertFalse(owner_lock["owner_token_matches"])
        self.assertFalse(owner_lock["statefile_write_executed"])
        self.assertFalse(owner_lock["lock_file_write_executed"])
        self.assertFalse(owner_lock["pid_ownership_claimed"])
        self.assertFalse(lifecycle_statefile_path.exists())

    def test_pingan_buy_requires_broker_readiness_before_desktop_execution(self) -> None:
        broker_health = Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="runtime path resolved but trading window was not found",
            data={"runtime": {"ok": True}, "window": {"ok": False}},
            next_action="Bring Ping An to the foreground and retry.",
        )
        with TemporaryDirectory() as temp_dir:
            manager = TdxTradeManager(
                profile="balanced",
                state_path=str(Path(temp_dir) / "state.json"),
                event_log_path=str(Path(temp_dir) / "events.jsonl"),
                submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
            )
            with (
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health) as mocked_health,
                patch("tdxquant.trade.manager.run_pingan_buy_fast") as mocked_buy,
            ):
                result = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="buy-broker-readiness-required-001",
                    max_price=10.50,
                    require_broker_readiness=True,
                )

        mocked_health.assert_called_once()
        mocked_buy.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        risk_gate = result.data["trade_safety"]["risk_gate"]
        self.assertFalse(risk_gate["passed"])
        readiness = risk_gate["broker_readiness_required_status"]
        self.assertTrue(readiness["required"])
        self.assertEqual(readiness["requirement_status"], "failed")
        self.assertFalse(readiness["broker_health_ok"])
        self.assertFalse(readiness["control_dispatch_executed"])
        self.assertFalse(readiness["order_submitted"])

    def test_pingan_buy_submit_once_allows_required_lifecycle_owner_lock_when_owned(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "result_dialog": {"contract_no": "B202604260099"},
            },
        )
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            manager = TdxTradeManager(
                profile="submit_once",
                state_path=str(Path(temp_dir) / "state.json"),
                event_log_path=str(Path(temp_dir) / "events.jsonl"),
                submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
            )
            acquire_result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(lifecycle_statefile_path),
                owner_token="execution-owner",
                stale_after_seconds=999.0,
            )
            self.assertTrue(acquire_result.ok)
            with patch("tdxquant.trade.manager.run_pingan_buy_submit_once", return_value=expected) as mocked:
                result = manager.pingan.buy_submit_once(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="submit-owner-lock-required-001",
                    max_price=10.50,
                    lifecycle_statefile_path=str(lifecycle_statefile_path),
                    lifecycle_owner_token="execution-owner",
                    lifecycle_stale_after_seconds=999.0,
                    require_lifecycle_owner_lock=True,
                )

        mocked.assert_called_once()
        self.assertTrue(result.ok)
        owner_lock = result.data["trade_safety"]["risk_gate"]["lifecycle_owner_lock_required_status"]
        self.assertTrue(owner_lock["required"])
        self.assertEqual(owner_lock["requirement_status"], "passed")
        self.assertEqual(owner_lock["status"], "owned")
        self.assertTrue(owner_lock["owner_token_matches"])
        self.assertFalse(owner_lock["pid_ownership_claimed"])

    def test_pingan_buy_rejects_invalid_order_before_desktop_execution(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with patch("tdxquant.trade.manager.run_pingan_buy_fast") as mocked:
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(Path(temp_dir) / "state.json"),
                    event_log_path=str(Path(temp_dir) / "events.jsonl"),
                    submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
                )
                result = manager.pingan.buy(
                    port="COM3",
                    code="ABC123",
                    price="10.00",
                    quantity=100,
                    submission_key="invalid-20260428-001",
                )
        mocked.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertIn("stock code must be a 6-digit numeric string", result.message)
        self.assertEqual(result.data["trade_safety"]["submission_key"], "invalid-20260428-001")
        self.assertFalse(result.data["trade_safety"]["risk_gate"]["passed"])

    def test_pingan_buy_rejects_requested_price_above_max_price_before_desktop_execution(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with patch("tdxquant.trade.manager.run_pingan_buy_fast") as mocked:
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(Path(temp_dir) / "state.json"),
                    event_log_path=str(Path(temp_dir) / "events.jsonl"),
                )
                result = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    max_price=9.50,
                )
        mocked.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertIn("max_price", result.message)
        self.assertFalse(result.data["trade_safety"]["risk_gate"]["passed"])

    def test_pingan_health_returns_non_side_effecting_summary(self) -> None:
        broker_health = Result(
            ok=True,
            code=ErrorCode.OK,
            message="health-check passed",
            data={"runtime": {"ok": True}, "window": {"ok": True}},
        )
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "pingan-last-order.json"
            event_log_path = Path(temp_dir) / "pingan-order-events.jsonl"
            ledger_path = Path(temp_dir) / "pingan-submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.health()
        self.assertTrue(result.ok)
        self.assertEqual(result.data["manager"]["method"], "health")
        self.assertEqual(result.data["health"]["overall_status"], "ok")
        self.assertEqual(result.data["health"]["requested"]["port"], None)
        self.assertEqual(result.data["health"]["artifact_targets"]["trade_audit_dir"], str(audit_dir))
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertNotIn("artifacts", result.data)

    def test_pingan_health_runs_requested_hid_ping(self) -> None:
        broker_health = Result(
            ok=True,
            code=ErrorCode.OK,
            message="health-check passed",
            data={"runtime": {"ok": True}, "window": {"ok": True}},
        )
        hid_ping = Result(ok=True, code=ErrorCode.OK, message="hid bridge ping completed", data={"response": "OK"})
        with patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health), patch(
            "tdxquant.trade.manager.run_hid_ping",
            return_value=hid_ping,
        ) as mocked_hid:
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.health(port="COM3", baudrate=9600, timeout=1.5, pre_delay=0.2)
        self.assertTrue(result.ok)
        mocked_hid.assert_called_once_with(port="COM3", baudrate=9600, timeout=1.5, pre_delay=0.2)
        checks = {item["name"]: item for item in result.data["health"]["checks"]}
        self.assertEqual(checks["hid_ping"]["status"], "ok")

    def test_pingan_health_fails_when_broker_health_check_fails(self) -> None:
        broker_health = Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="runtime path resolved but trading window was not found",
            data={"runtime": {"ok": True}, "window": {"ok": False}},
            next_action="Bring Ping An to the foreground and retry.",
        )
        with patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health):
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.health()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.CONTROL_NOT_FOUND)
        self.assertEqual(result.data["health"]["overall_status"], "failed")
        self.assertEqual(result.next_action, "Bring Ping An to the foreground and retry.")

    def test_pingan_preflight_returns_non_side_effecting_summary(self) -> None:
        broker_health = Result(
            ok=True,
            code=ErrorCode.OK,
            message="health-check passed",
            data={"runtime": {"ok": True}, "window": {"ok": True}},
        )
        detect_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="detected Ping An buy-page controls",
            data={"detection": {"code_hwnd": 1, "quantity_hwnd": 2, "buy_button_hwnd": 3}},
        )
        hid_ping = Result(ok=True, code=ErrorCode.OK, message="hid bridge ping completed", data={"response": "OK"})
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "pingan-last-order.json"
            event_log_path = Path(temp_dir) / "pingan-order-events.jsonl"
            ledger_path = Path(temp_dir) / "pingan-submission-ledger.jsonl"
            with (
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health),
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.detect", return_value=detect_result),
                patch("tdxquant.trade.manager.run_hid_ping", return_value=hid_ping),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                )
                result = manager.pingan.preflight(port="COM3", code="000001", price="10.00", quantity=100)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["manager"]["method"], "preflight")
        self.assertEqual(result.data["preflight"]["overall_status"], "ok")
        self.assertEqual(result.data["preflight"]["requested"]["port"], "COM3")
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertNotIn("artifacts", result.data)

    def test_pingan_preflight_reports_provider_safety_promotion_gate_status(self) -> None:
        broker_health = Result(
            ok=True,
            code=ErrorCode.OK,
            message="health-check passed",
            data={"runtime": {"ok": True}, "window": {"ok": True}},
        )
        detect_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="detected Ping An buy-page controls",
            data={"detection": {"code_hwnd": 1, "quantity_hwnd": 2, "buy_button_hwnd": 3}},
        )
        hid_ping = Result(ok=True, code=ErrorCode.OK, message="hid bridge ping completed", data={"response": "OK"})
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "pingan-last-order.json"
            event_log_path = Path(temp_dir) / "pingan-order-events.jsonl"
            ledger_path = Path(temp_dir) / "pingan-submission-ledger.jsonl"
            with (
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health),
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.detect", return_value=detect_result),
                patch("tdxquant.trade.manager.run_hid_ping", return_value=hid_ping),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                )
                result = manager.pingan.preflight(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="preflight-gate-001",
                    max_price=10.50,
                )

        self.assertTrue(result.ok)
        provenance = result.data["artifact_provenance"]
        self.assertEqual(provenance["schema"], "tdx.desktop_trade.pingan_readiness_evidence_artifact.v1")
        self.assertEqual(provenance["source_kind"], "preflight")
        self.assertEqual(provenance["producer"], "trade preflight")
        self.assertEqual(provenance["evidence_schema"], "tdx.desktop_trade.pingan_promotion_gate_status.v1")
        gate_status = result.data["promotion_gate_status"]
        self.assertEqual(gate_status["schema_version"], "tdx.desktop_trade.pingan_promotion_gate_status.v1")
        self.assertEqual(gate_status["status"], "partial")
        self.assertEqual(gate_status["execution_mode"], "readonly_preflight")
        self.assertFalse(gate_status["dispatch_executed"])
        self.assertFalse(gate_status["order_submitted"])
        ownership = gate_status["provider_broker_ownership"]
        self.assertEqual(ownership["broker"], "pingan_desktop")
        self.assertEqual(ownership["manager_entrypoint"], "TdxTradeManager.pingan.preflight")
        self.assertEqual(ownership["supported_brokers"], ["pingan_desktop"])
        safety = gate_status["safety_gates"]
        self.assertEqual(safety["max_price_guard"]["status"], "configured")
        self.assertEqual(safety["submission_key"]["status"], "provided")
        self.assertEqual(safety["idempotency"]["decision"], "execute")
        self.assertTrue(safety["risk_gate"]["passed"])
        self.assertEqual(safety["explicit_approval"]["status"], "not_granted")
        self.assertIn("desktop_lifecycle", gate_status["remaining_gates"])
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())

    def test_pingan_preflight_reports_lifecycle_owner_lock_status_without_side_effects(self) -> None:
        broker_health = Result(
            ok=True,
            code=ErrorCode.OK,
            message="health-check passed",
            data={"runtime": {"ok": True}, "window": {"ok": True}},
        )
        detect_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="detected Ping An buy-page controls",
            data={"detection": {"code_hwnd": 1, "quantity_hwnd": 2, "buy_button_hwnd": 3}},
        )
        hid_ping = Result(ok=True, code=ErrorCode.OK, message="hid bridge ping completed", data={"response": "OK"})
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "pingan-last-order.json"
            event_log_path = Path(temp_dir) / "pingan-order-events.jsonl"
            ledger_path = Path(temp_dir) / "pingan-submission-ledger.jsonl"
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            lifecycle_lock_path = Path(f"{lifecycle_statefile_path}.lock")
            manager = TdxTradeManager(
                profile="balanced",
                state_path=str(state_path),
                event_log_path=str(event_log_path),
                submission_ledger_path=str(ledger_path),
            )
            acquire_result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(lifecycle_statefile_path),
                owner_token="preflight-owner",
                stale_after_seconds=999.0,
            )
            self.assertTrue(acquire_result.ok)
            before_statefile = lifecycle_statefile_path.read_text(encoding="utf-8")
            before_lock_file = lifecycle_lock_path.read_text(encoding="utf-8")
            with (
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health),
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.detect", return_value=detect_result),
                patch("tdxquant.trade.manager.run_hid_ping", return_value=hid_ping),
            ):
                result = manager.pingan.preflight(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="preflight-owner-lock-001",
                    max_price=10.50,
                    lifecycle_statefile_path=str(lifecycle_statefile_path),
                    lifecycle_owner_token="preflight-owner",
                    lifecycle_stale_after_seconds=999.0,
                    require_lifecycle_owner_lock=True,
                )
            after_statefile = lifecycle_statefile_path.read_text(encoding="utf-8")
            after_lock_file = lifecycle_lock_path.read_text(encoding="utf-8")
            state_path_exists = state_path.exists()
            event_log_path_exists = event_log_path.exists()
            ledger_path_exists = ledger_path.exists()

        self.assertTrue(result.ok)
        owner_lock_status = result.data["promotion_gate_status"]["lifecycle_owner_lock_status"]
        self.assertTrue(owner_lock_status["configured"])
        self.assertTrue(owner_lock_status["status_check_executed"])
        self.assertEqual(owner_lock_status["status"], "owned")
        self.assertEqual(owner_lock_status["statefile_path"], str(lifecycle_statefile_path))
        self.assertEqual(owner_lock_status["lock_path"], str(lifecycle_lock_path))
        self.assertEqual(owner_lock_status["owner_token"], "preflight-owner")
        self.assertEqual(owner_lock_status["current_owner_token"], "preflight-owner")
        self.assertTrue(owner_lock_status["statefile_present"])
        self.assertTrue(owner_lock_status["lock_file_present"])
        self.assertFalse(owner_lock_status["stale_detected"])
        self.assertTrue(owner_lock_status["owner_pid_alive"])
        self.assertEqual(owner_lock_status["owner_pid_status"], "alive")
        self.assertFalse(owner_lock_status["pid_ownership_claimed"])
        self.assertEqual(owner_lock_status["side_effect_level"], "none")
        self.assertFalse(owner_lock_status["statefile_write_executed"])
        self.assertFalse(owner_lock_status["lock_file_write_executed"])
        self.assertFalse(owner_lock_status["order_submitted"])
        self.assertFalse(owner_lock_status["control_dispatch_executed"])
        self.assertTrue(owner_lock_status["required"])
        self.assertEqual(owner_lock_status["requirement_status"], "passed")
        self.assertTrue(owner_lock_status["owner_token_matches"])
        self.assertEqual(after_statefile, before_statefile)
        self.assertEqual(after_lock_file, before_lock_file)
        self.assertFalse(state_path_exists)
        self.assertFalse(event_log_path_exists)
        self.assertFalse(ledger_path_exists)

    def test_pingan_preflight_fails_when_required_lifecycle_owner_lock_is_missing(self) -> None:
        broker_health = Result(
            ok=True,
            code=ErrorCode.OK,
            message="health-check passed",
            data={"runtime": {"ok": True}, "window": {"ok": True}},
        )
        detect_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="detected Ping An buy-page controls",
            data={"detection": {"code_hwnd": 1, "quantity_hwnd": 2, "buy_button_hwnd": 3}},
        )
        hid_ping = Result(ok=True, code=ErrorCode.OK, message="hid bridge ping completed", data={"response": "OK"})
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "pingan-last-order.json"
            event_log_path = Path(temp_dir) / "pingan-order-events.jsonl"
            ledger_path = Path(temp_dir) / "pingan-submission-ledger.jsonl"
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            lifecycle_lock_path = Path(f"{lifecycle_statefile_path}.lock")
            with (
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health),
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.detect", return_value=detect_result),
                patch("tdxquant.trade.manager.run_hid_ping", return_value=hid_ping),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                )
                result = manager.pingan.preflight(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="preflight-owner-lock-missing",
                    max_price=10.50,
                    lifecycle_statefile_path=str(lifecycle_statefile_path),
                    lifecycle_owner_token="preflight-owner",
                    lifecycle_stale_after_seconds=999.0,
                    require_lifecycle_owner_lock=True,
                )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        owner_lock_status = result.data["promotion_gate_status"]["lifecycle_owner_lock_status"]
        self.assertTrue(owner_lock_status["required"])
        self.assertEqual(owner_lock_status["requirement_status"], "failed")
        self.assertEqual(owner_lock_status["status"], "not_acquired")
        self.assertFalse(owner_lock_status["owner_token_matches"])
        self.assertFalse(owner_lock_status["statefile_present"])
        self.assertFalse(owner_lock_status["lock_file_present"])
        self.assertFalse(owner_lock_status["statefile_write_executed"])
        self.assertFalse(owner_lock_status["lock_file_write_executed"])
        self.assertFalse(owner_lock_status["order_submitted"])
        self.assertFalse(owner_lock_status["control_dispatch_executed"])
        self.assertFalse(lifecycle_statefile_path.exists())
        self.assertFalse(lifecycle_lock_path.exists())
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())

    def test_pingan_lifecycle_supervisor_tick_rejects_missing_owner_lock_without_health_check(self) -> None:
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            manager = TdxTradeManager(profile="balanced")

            with patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check") as mocked_health:
                result = manager.pingan.lifecycle_supervisor_tick(
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    stale_after_seconds=999.0,
                    max_restart_attempts=2,
                    backoff_seconds=30.0,
                )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        supervisor = result.data["lifecycle_supervisor"]
        self.assertEqual(supervisor["status"], "owner_lock_not_owned")
        self.assertFalse(supervisor["supervisor_owned"])
        self.assertFalse(supervisor["control_dispatch_executed"])
        self.assertFalse(supervisor["restart_executed"])
        self.assertFalse(supervisor["backoff_executed"])
        self.assertFalse(supervisor["statefile_write_executed"])
        self.assertFalse(supervisor["order_submitted"])
        self.assertFalse(supervisor["process_kill_executed"])
        self.assertFalse(supervisor["pid_ownership_claimed"])
        self.assertEqual(supervisor["side_effect_level"], "none")
        self.assertFalse(lifecycle_statefile_path.exists())
        mocked_health.assert_not_called()

    def test_pingan_lifecycle_supervisor_tick_records_restart_then_backoff(self) -> None:
        unhealthy = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="PingAn broker health failed",
            data={"runtime": {"ok": False}, "window": {"ok": False}},
        )
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            manager = TdxTradeManager(profile="balanced")
            acquire_result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(lifecycle_statefile_path),
                owner_token="operator-a",
                stale_after_seconds=999.0,
            )
            self.assertTrue(acquire_result.ok)

            with patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=unhealthy) as mocked_health:
                first = manager.pingan.lifecycle_supervisor_tick(
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    stale_after_seconds=999.0,
                    max_restart_attempts=2,
                    backoff_seconds=600.0,
                )
                second = manager.pingan.lifecycle_supervisor_tick(
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    stale_after_seconds=999.0,
                    max_restart_attempts=2,
                    backoff_seconds=600.0,
                )
            state_payload = json.loads(lifecycle_statefile_path.read_text(encoding="utf-8"))

        self.assertTrue(first.ok)
        first_payload = first.data["lifecycle_supervisor"]
        self.assertEqual(first_payload["status"], "restart_recorded")
        self.assertTrue(first_payload["supervisor_owned"])
        self.assertTrue(first_payload["control_dispatch_executed"])
        self.assertFalse(first_payload["broker_health_ok"])
        self.assertTrue(first_payload["restart_executed"])
        self.assertFalse(first_payload["backoff_executed"])
        self.assertTrue(first_payload["statefile_write_executed"])
        self.assertEqual(first_payload["restart_attempt_count"], 1)
        self.assertFalse(first_payload["order_submitted"])
        self.assertFalse(first_payload["process_kill_executed"])
        self.assertFalse(first_payload["pid_ownership_claimed"])
        self.assertEqual(first_payload["side_effect_level"], "local_lifecycle_statefile")

        self.assertTrue(second.ok)
        second_payload = second.data["lifecycle_supervisor"]
        self.assertEqual(second_payload["status"], "backoff_waiting")
        self.assertTrue(second_payload["supervisor_owned"])
        self.assertTrue(second_payload["backoff_executed"])
        self.assertFalse(second_payload["restart_executed"])
        self.assertEqual(second_payload["restart_attempt_count"], 1)
        self.assertEqual(state_payload["supervisor"]["status"], "backoff_waiting")
        self.assertEqual(state_payload["supervisor"]["restart_attempt_count"], 1)
        self.assertEqual(mocked_health.call_count, 2)

    def test_pingan_lifecycle_supervisor_run_bounds_ticks(self) -> None:
        healthy = Result(
            ok=True,
            code=ErrorCode.OK,
            message="PingAn broker health ok",
            data={"runtime": {"ok": True}, "window": {"ok": True}},
        )
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            manager = TdxTradeManager(profile="balanced")
            acquire_result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(lifecycle_statefile_path),
                owner_token="operator-a",
                stale_after_seconds=999.0,
            )
            self.assertTrue(acquire_result.ok)

            with patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=healthy) as mocked_health:
                result = manager.pingan.lifecycle_supervisor_run(
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    stale_after_seconds=999.0,
                    max_restart_attempts=2,
                    backoff_seconds=30.0,
                    max_ticks=3,
                    interval_seconds=0.0,
                )

        self.assertTrue(result.ok)
        run = result.data["lifecycle_supervisor_run"]
        self.assertEqual(run["tick_count"], 3)
        self.assertEqual(run["max_ticks"], 3)
        self.assertEqual(run["execution_mode"], "explicit_operator_lifecycle_supervisor_control")
        self.assertEqual([item["status"] for item in run["ticks"]], ["healthy", "healthy", "healthy"])
        self.assertFalse(run["order_submitted"])
        self.assertFalse(run["process_kill_executed"])
        self.assertFalse(run["pid_ownership_claimed"])
        self.assertEqual(mocked_health.call_count, 3)

    def test_pingan_lifecycle_process_start_rejects_missing_owner_lock_without_spawn(self) -> None:
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            exe_path = Path(temp_dir) / "TdxW.exe"
            exe_path.write_text("placeholder", encoding="utf-8")
            manager = TdxTradeManager(profile="balanced")

            with patch("tdxquant.trade.manager.subprocess.Popen") as mocked_popen:
                result = manager.pingan.lifecycle_process(
                    action="start",
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    exe_path=str(exe_path),
                    stale_after_seconds=999.0,
                )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        process = result.data["lifecycle_process"]
        self.assertEqual(process["status"], "owner_lock_not_owned")
        self.assertFalse(process["process_start_executed"])
        self.assertFalse(process["process_stop_executed"])
        self.assertFalse(process["process_kill_executed"])
        self.assertFalse(process["pid_ownership_claimed"])
        self.assertFalse(process["statefile_write_executed"])
        self.assertEqual(process["side_effect_level"], "none")
        self.assertFalse(lifecycle_statefile_path.exists())
        mocked_popen.assert_not_called()

    def test_pingan_lifecycle_process_start_records_spawned_pid(self) -> None:
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            exe_path = Path(temp_dir) / "TdxW.exe"
            exe_path.write_text("placeholder", encoding="utf-8")
            manager = TdxTradeManager(profile="balanced")
            acquire_result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(lifecycle_statefile_path),
                owner_token="operator-a",
                stale_after_seconds=999.0,
            )
            self.assertTrue(acquire_result.ok)
            spawned = type("SpawnedProcess", (), {"pid": 4242})()

            with patch("tdxquant.trade.manager.subprocess.Popen", return_value=spawned) as mocked_popen:
                result = manager.pingan.lifecycle_process(
                    action="start",
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    exe_path=str(exe_path),
                    stale_after_seconds=999.0,
                )
            state_payload = json.loads(lifecycle_statefile_path.read_text(encoding="utf-8"))

        self.assertTrue(result.ok)
        process = result.data["lifecycle_process"]
        self.assertEqual(process["status"], "started")
        self.assertEqual(process["process_pid"], 4242)
        self.assertEqual(process["process_command"], [str(exe_path)])
        self.assertTrue(process["process_start_executed"])
        self.assertFalse(process["process_stop_executed"])
        self.assertFalse(process["process_kill_executed"])
        self.assertTrue(process["pid_ownership_claimed"])
        self.assertTrue(process["statefile_write_executed"])
        self.assertEqual(process["side_effect_level"], "local_lifecycle_statefile_and_process")
        self.assertEqual(state_payload["process"]["process_pid"], 4242)
        self.assertEqual(state_payload["process"]["process_owner_token"], "operator-a")
        self.assertEqual(state_payload["process"]["process_command"], [str(exe_path)])
        mocked_popen.assert_called_once_with([str(exe_path)], start_new_session=True)

    def test_pingan_lifecycle_process_restart_stops_recorded_pid_and_records_new_pid(self) -> None:
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            exe_path = Path(temp_dir) / "TdxW.exe"
            exe_path.write_text("placeholder", encoding="utf-8")
            manager = TdxTradeManager(profile="balanced")
            acquire_result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(lifecycle_statefile_path),
                owner_token="operator-a",
                stale_after_seconds=999.0,
            )
            self.assertTrue(acquire_result.ok)
            first_process = type("SpawnedProcess", (), {"pid": 4242})()
            restarted_process = type("SpawnedProcess", (), {"pid": 4343})()
            killed: list[int] = []

            def fake_kill(pid: int, sig: int) -> None:
                if pid in {os.getpid(), 4242} and sig == 0:
                    return
                if pid == 4242:
                    killed.append(pid)
                    return
                raise OSError("unexpected pid")

            with patch("tdxquant.trade.manager.subprocess.Popen", return_value=first_process):
                start_result = manager.pingan.lifecycle_process(
                    action="start",
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    exe_path=str(exe_path),
                    stale_after_seconds=999.0,
                )
            self.assertTrue(start_result.ok)

            with (
                patch("tdxquant.trade.manager.os.kill", side_effect=fake_kill),
                patch("tdxquant.trade.manager.subprocess.Popen", return_value=restarted_process) as mocked_popen,
            ):
                result = manager.pingan.lifecycle_process(
                    action="restart",
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    exe_path=str(exe_path),
                    stale_after_seconds=999.0,
                )
            state_payload = json.loads(lifecycle_statefile_path.read_text(encoding="utf-8"))

        self.assertTrue(result.ok)
        process = result.data["lifecycle_process"]
        self.assertEqual(process["status"], "restarted")
        self.assertEqual(process["previous_process_pid"], 4242)
        self.assertEqual(process["process_pid"], 4343)
        self.assertTrue(process["process_stop_executed"])
        self.assertTrue(process["process_start_executed"])
        self.assertTrue(process["process_kill_executed"])
        self.assertTrue(process["pid_ownership_claimed"])
        self.assertEqual(killed, [4242])
        self.assertEqual(state_payload["process"]["process_pid"], 4343)
        self.assertEqual(state_payload["process"]["previous_process_pid"], 4242)
        mocked_popen.assert_called_once_with([str(exe_path)], start_new_session=True)

    def test_pingan_lifecycle_supervisor_tick_opt_in_restarts_recorded_process(self) -> None:
        unhealthy = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="PingAn broker health failed",
            data={"runtime": {"ok": False}, "window": {"ok": False}},
        )
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            exe_path = Path(temp_dir) / "TdxW.exe"
            exe_path.write_text("placeholder", encoding="utf-8")
            manager = TdxTradeManager(profile="balanced")
            acquire_result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(lifecycle_statefile_path),
                owner_token="operator-a",
                stale_after_seconds=999.0,
            )
            self.assertTrue(acquire_result.ok)
            started_process = type("SpawnedProcess", (), {"pid": 4242})()
            restarted_process = type("SpawnedProcess", (), {"pid": 4343})()

            with patch("tdxquant.trade.manager.subprocess.Popen", return_value=started_process):
                start_result = manager.pingan.lifecycle_process(
                    action="start",
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    exe_path=str(exe_path),
                    stale_after_seconds=999.0,
                )
            self.assertTrue(start_result.ok)
            killed: list[int] = []

            def fake_kill(pid: int, sig: int) -> None:
                if pid in {os.getpid(), 4242} and sig == 0:
                    return
                if pid == 4242:
                    killed.append(pid)
                    return
                raise OSError("unexpected pid")

            with (
                patch("tdxquant.trade.manager.os.kill", side_effect=fake_kill),
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=unhealthy),
                patch("tdxquant.trade.manager.subprocess.Popen", return_value=restarted_process) as mocked_popen,
            ):
                result = manager.pingan.lifecycle_supervisor_tick(
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    stale_after_seconds=999.0,
                    max_restart_attempts=2,
                    backoff_seconds=600.0,
                    process_restart_enabled=True,
                    process_restart_exe_path=str(exe_path),
                )
            state_payload = json.loads(lifecycle_statefile_path.read_text(encoding="utf-8"))

        self.assertTrue(result.ok)
        supervisor = result.data["lifecycle_supervisor"]
        self.assertEqual(supervisor["status"], "process_restarted")
        self.assertTrue(supervisor["restart_executed"])
        self.assertTrue(supervisor["process_restart_requested"])
        self.assertTrue(supervisor["process_restart_executed"])
        self.assertEqual(supervisor["process_restart_status"], "restarted")
        self.assertEqual(supervisor["process_restart_result"]["process_pid"], 4343)
        self.assertEqual(supervisor["process_restart_result"]["previous_process_pid"], 4242)
        self.assertEqual(killed, [4242])
        self.assertEqual(state_payload["process"]["process_pid"], 4343)
        mocked_popen.assert_called_once_with([str(exe_path)], start_new_session=True)

    def test_pingan_lifecycle_supervisor_restart_recheck_reports_recovered(self) -> None:
        unhealthy = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="PingAn broker health failed",
            data={"runtime": {"ok": False}, "window": {"ok": False}},
        )
        recovered = Result(
            ok=True,
            code=ErrorCode.OK,
            message="PingAn broker health recovered",
            data={"runtime": {"ok": True}, "window": {"ok": True}},
        )
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            exe_path = Path(temp_dir) / "TdxW.exe"
            exe_path.write_text("placeholder", encoding="utf-8")
            manager = TdxTradeManager(profile="balanced")
            acquire_result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(lifecycle_statefile_path),
                owner_token="operator-a",
                stale_after_seconds=999.0,
            )
            self.assertTrue(acquire_result.ok)
            started_process = type("SpawnedProcess", (), {"pid": 4242})()
            restarted_process = type("SpawnedProcess", (), {"pid": 4343})()

            with patch("tdxquant.trade.manager.subprocess.Popen", return_value=started_process):
                start_result = manager.pingan.lifecycle_process(
                    action="start",
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    exe_path=str(exe_path),
                    stale_after_seconds=999.0,
                )
            self.assertTrue(start_result.ok)

            def fake_kill(pid: int, sig: int) -> None:
                if pid in {os.getpid(), 4242} and sig == 0:
                    return
                if pid == 4242:
                    return
                raise OSError("unexpected pid")

            with (
                patch("tdxquant.trade.manager.os.kill", side_effect=fake_kill),
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", side_effect=[unhealthy, recovered]) as mocked_health,
                patch("tdxquant.trade.manager.subprocess.Popen", return_value=restarted_process),
            ):
                result = manager.pingan.lifecycle_supervisor_tick(
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    stale_after_seconds=999.0,
                    max_restart_attempts=2,
                    backoff_seconds=600.0,
                    process_restart_enabled=True,
                    process_restart_exe_path=str(exe_path),
                    process_restart_recheck_enabled=True,
                    process_restart_recheck_delay_seconds=0.0,
                )

        self.assertTrue(result.ok)
        supervisor = result.data["lifecycle_supervisor"]
        self.assertEqual(supervisor["status"], "process_restarted")
        self.assertTrue(supervisor["process_restart_executed"])
        self.assertTrue(supervisor["process_restart_recheck_requested"])
        self.assertTrue(supervisor["process_restart_recheck_executed"])
        self.assertTrue(supervisor["post_restart_broker_health_ok"])
        self.assertEqual(supervisor["post_restart_broker_health_message"], "PingAn broker health recovered")
        self.assertEqual(supervisor["lifecycle_recovery_status"], "recovered")
        self.assertEqual(mocked_health.call_count, 2)

    def test_pingan_lifecycle_supervisor_restart_recheck_reports_still_unhealthy(self) -> None:
        unhealthy = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="PingAn broker health failed",
            data={"runtime": {"ok": False}, "window": {"ok": False}},
        )
        still_unhealthy = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="PingAn broker health still failed",
            data={"runtime": {"ok": False}, "window": {"ok": False}},
        )
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            exe_path = Path(temp_dir) / "TdxW.exe"
            exe_path.write_text("placeholder", encoding="utf-8")
            manager = TdxTradeManager(profile="balanced")
            acquire_result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(lifecycle_statefile_path),
                owner_token="operator-a",
                stale_after_seconds=999.0,
            )
            self.assertTrue(acquire_result.ok)
            started_process = type("SpawnedProcess", (), {"pid": 4242})()
            restarted_process = type("SpawnedProcess", (), {"pid": 4343})()

            with patch("tdxquant.trade.manager.subprocess.Popen", return_value=started_process):
                start_result = manager.pingan.lifecycle_process(
                    action="start",
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    exe_path=str(exe_path),
                    stale_after_seconds=999.0,
                )
            self.assertTrue(start_result.ok)

            def fake_kill(pid: int, sig: int) -> None:
                if pid in {os.getpid(), 4242} and sig == 0:
                    return
                if pid == 4242:
                    return
                raise OSError("unexpected pid")

            with (
                patch("tdxquant.trade.manager.os.kill", side_effect=fake_kill),
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", side_effect=[unhealthy, still_unhealthy]),
                patch("tdxquant.trade.manager.subprocess.Popen", return_value=restarted_process),
            ):
                result = manager.pingan.lifecycle_supervisor_tick(
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    stale_after_seconds=999.0,
                    max_restart_attempts=2,
                    backoff_seconds=600.0,
                    process_restart_enabled=True,
                    process_restart_exe_path=str(exe_path),
                    process_restart_recheck_enabled=True,
                    process_restart_recheck_delay_seconds=0.0,
                )

        self.assertTrue(result.ok)
        supervisor = result.data["lifecycle_supervisor"]
        self.assertEqual(supervisor["status"], "process_restarted")
        self.assertTrue(supervisor["process_restart_executed"])
        self.assertTrue(supervisor["process_restart_recheck_executed"])
        self.assertFalse(supervisor["post_restart_broker_health_ok"])
        self.assertEqual(supervisor["post_restart_broker_health_message"], "PingAn broker health still failed")
        self.assertEqual(supervisor["lifecycle_recovery_status"], "still_unhealthy")
        self.assertFalse(supervisor["order_submitted"])

    def test_pingan_lifecycle_supervisor_backoff_prevents_opt_in_process_restart(self) -> None:
        unhealthy = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="PingAn broker health failed",
            data={"runtime": {"ok": False}, "window": {"ok": False}},
        )
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            exe_path = Path(temp_dir) / "TdxW.exe"
            exe_path.write_text("placeholder", encoding="utf-8")
            manager = TdxTradeManager(profile="balanced")
            acquire_result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(lifecycle_statefile_path),
                owner_token="operator-a",
                stale_after_seconds=999.0,
            )
            self.assertTrue(acquire_result.ok)
            started_process = type("SpawnedProcess", (), {"pid": 4242})()
            restarted_process = type("SpawnedProcess", (), {"pid": 4343})()

            with patch("tdxquant.trade.manager.subprocess.Popen", return_value=started_process):
                start_result = manager.pingan.lifecycle_process(
                    action="start",
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    exe_path=str(exe_path),
                    stale_after_seconds=999.0,
                )
            self.assertTrue(start_result.ok)

            def fake_kill(pid: int, sig: int) -> None:
                if pid in {os.getpid(), 4242, 4343} and sig == 0:
                    return
                if pid == 4242:
                    return
                raise OSError("unexpected pid")

            with (
                patch("tdxquant.trade.manager.os.kill", side_effect=fake_kill),
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=unhealthy),
                patch("tdxquant.trade.manager.subprocess.Popen", return_value=restarted_process) as mocked_popen,
            ):
                first = manager.pingan.lifecycle_supervisor_tick(
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    stale_after_seconds=999.0,
                    max_restart_attempts=2,
                    backoff_seconds=600.0,
                    process_restart_enabled=True,
                    process_restart_exe_path=str(exe_path),
                )
                second = manager.pingan.lifecycle_supervisor_tick(
                    statefile_path=str(lifecycle_statefile_path),
                    owner_token="operator-a",
                    stale_after_seconds=999.0,
                    max_restart_attempts=2,
                    backoff_seconds=600.0,
                    process_restart_enabled=True,
                    process_restart_exe_path=str(exe_path),
                )

        self.assertTrue(first.ok)
        self.assertEqual(first.data["lifecycle_supervisor"]["status"], "process_restarted")
        self.assertTrue(second.ok)
        second_payload = second.data["lifecycle_supervisor"]
        self.assertEqual(second_payload["status"], "backoff_waiting")
        self.assertTrue(second_payload["backoff_executed"])
        self.assertFalse(second_payload["restart_executed"])
        self.assertFalse(second_payload["process_restart_requested"])
        self.assertFalse(second_payload["process_restart_executed"])
        self.assertEqual(mocked_popen.call_count, 1)

    def test_pingan_preflight_fails_on_conflicting_submission_key_without_writing_ledger(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "result_dialog": {"contract_no": "B202604260010"},
            },
        )
        broker_health = Result(
            ok=True,
            code=ErrorCode.OK,
            message="health-check passed",
            data={"runtime": {"ok": True}, "window": {"ok": True}},
        )
        detect_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="detected Ping An buy-page controls",
            data={"detection": {"code_hwnd": 1, "quantity_hwnd": 2, "buy_button_hwnd": 3}},
        )
        hid_ping = Result(ok=True, code=ErrorCode.OK, message="hid bridge ping completed", data={"response": "OK"})
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            with patch("tdxquant.trade.manager.run_pingan_buy_fast", return_value=expected):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                )
                trade_result = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="conflict-preflight-001",
                )
                self.assertTrue(trade_result.ok)
            before_lines = ledger_path.read_text(encoding="utf-8").splitlines()
            with (
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health),
                patch("tdxquant.trade.manager.PingAnBrokerAdapter.detect", return_value=detect_result),
                patch("tdxquant.trade.manager.run_hid_ping", return_value=hid_ping),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                )
                result = manager.pingan.preflight(
                    port="COM3",
                    code="000001",
                    price="10.20",
                    quantity=100,
                    submission_key="conflict-preflight-001",
                )
            after_lines = ledger_path.read_text(encoding="utf-8").splitlines()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.data["preflight"]["overall_status"], "failed")
        checks = {item["name"]: item for item in result.data["preflight"]["checks"]}
        self.assertEqual(checks["idempotency"]["status"], "failed")
        self.assertEqual(before_lines, after_lines)

    def test_pingan_dialog_readiness_warns_when_requested_dialog_is_absent_without_require_visible(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            with patch("tdxquant.trade.manager._find_pingan_confirm_button", return_value={"ok": False, "last_error": "confirm button not found"}):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                )
                result = manager.pingan.dialog_readiness(dialog="confirm", require_visible=False)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["manager"]["method"], "dialog_readiness")
        self.assertEqual(result.data["dialog_readiness"]["overall_status"], "degraded")
        checks = {item["name"]: item for item in result.data["dialog_readiness"]["checks"]}
        self.assertEqual(checks["confirm_lookup"]["status"], "warning")
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertNotIn("artifacts", result.data)

    def test_pingan_dialog_readiness_fails_when_visibility_is_required(self) -> None:
        with patch("tdxquant.trade.manager._find_pingan_confirm_button", return_value={"ok": False, "last_error": "confirm button not found"}):
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.dialog_readiness(dialog="confirm", require_visible=True)
        self.assertFalse(result.ok)
        self.assertEqual(result.data["dialog_readiness"]["overall_status"], "failed")
        checks = {item["name"]: item for item in result.data["dialog_readiness"]["checks"]}
        self.assertEqual(checks["confirm_lookup"]["status"], "failed")

    def test_pingan_dialog_readiness_uses_result_lookup_when_dialog_is_visible(self) -> None:
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        with (
            patch("tdxquant.trade.manager._find_pingan_result_dialog", return_value=result_dialog),
            patch("tdxquant.trade.manager._find_pingan_result_confirm_button", return_value=result_confirm),
        ):
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.dialog_readiness(dialog="result", require_visible=True)
        self.assertTrue(result.ok)
        checks = {item["name"]: item for item in result.data["dialog_readiness"]["checks"]}
        self.assertEqual(checks["result_dialog_lookup"]["status"], "ok")
        self.assertEqual(checks["result_confirm_lookup"]["status"], "ok")

    def test_pingan_dialog_readiness_reports_exception_popup_lookup_without_side_effects(self) -> None:
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        text_payload = {
            "merged_texts": ["系统异常：委托失败", "请联系柜台"],
            "contract_no": None,
            "uia_texts": ["系统异常：委托失败"],
            "win32_child_texts": [{"text": "请联系柜台"}],
        }
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with (
                patch("tdxquant.trade.manager._find_pingan_result_dialog", return_value=result_dialog),
                patch("tdxquant.trade.manager._find_pingan_result_confirm_button", return_value=result_confirm),
                patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value=text_payload),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.dialog_readiness(dialog="result", require_visible=True)

        self.assertTrue(result.ok)
        checks = {item["name"]: item for item in result.data["dialog_readiness"]["checks"]}
        exception_check = checks["exception_popup_lookup"]
        self.assertEqual(exception_check["status"], "warning")
        self.assertTrue(exception_check["detail"]["exception_detected"])
        self.assertIn("异常", exception_check["detail"]["matched_keywords"])
        self.assertEqual(exception_check["detail"]["text_payload"], text_payload)
        lifecycle = result.data["desktop_lifecycle_gate_status"]
        self.assertEqual(lifecycle["side_effect_level"], "none")
        self.assertFalse(lifecycle["order_submitted"])
        self.assertFalse(lifecycle["control_dispatch_executed"])
        self.assertEqual(lifecycle["dialog_checks"]["exception_popup_lookup"]["status"], "warning")
        self.assertIn("exception_popup_lookup", lifecycle["covered_lifecycle_gates"])
        self.assertIn("exception_popup_handling", lifecycle["remaining_lifecycle_gates"])
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertFalse(audit_dir.exists())

    def test_pingan_exception_popup_inspect_reports_lookup_without_side_effects(self) -> None:
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        text_payload = {
            "merged_texts": ["系统异常：委托失败", "请联系柜台"],
            "contract_no": None,
            "uia_texts": ["系统异常：委托失败"],
            "win32_child_texts": [{"text": "请联系柜台"}],
        }
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with (
                patch("tdxquant.trade.manager._find_result_dialog_for_lookup", return_value=result_dialog),
                patch("tdxquant.trade.manager._find_result_confirm_target_for_lookup", return_value=result_confirm),
                patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value=text_payload),
                patch("tdxquant.trade.manager._click_lookup_target") as mocked_click,
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.exception_popup(action="inspect", dialog_lookup_mode="uia", result_timeout=1.8)

        mocked_click.assert_not_called()
        self.assertTrue(result.ok)
        self.assertEqual(result.data["manager"]["method"], "exception_popup")
        control = result.data["exception_popup_control"]
        self.assertEqual(control["action"], "inspect")
        self.assertTrue(control["exception_detected"])
        self.assertFalse(control["close_executed"])
        self.assertFalse(control["confirm_click_executed"])
        self.assertFalse(control["retry_executed"])
        self.assertFalse(control["recovery_executed"])
        self.assertFalse(control["resubmission_executed"])
        self.assertFalse(control["order_submitted"])
        self.assertEqual(control["side_effect_level"], "none")
        self.assertEqual(result.data["trade_safety"]["side_effect_level"], "none")
        self.assertNotIn("artifacts", result.data)
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertFalse(audit_dir.exists())

    def test_pingan_exception_popup_close_requires_explicit_confirmation(self) -> None:
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        text_payload = {"merged_texts": ["系统异常：委托失败"]}
        with (
            patch("tdxquant.trade.manager._find_result_dialog_for_lookup", return_value=result_dialog),
            patch("tdxquant.trade.manager._find_result_confirm_target_for_lookup", return_value=result_confirm),
            patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value=text_payload),
            patch("tdxquant.trade.manager._click_lookup_target") as mocked_click,
        ):
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.exception_popup(action="close", confirm_close=False)

        mocked_click.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        control = result.data["exception_popup_control"]
        self.assertEqual(control["action"], "close")
        self.assertTrue(control["exception_detected"])
        self.assertFalse(control["close_executed"])
        self.assertFalse(control["confirm_click_executed"])
        self.assertFalse(control["retry_executed"])
        self.assertFalse(control["recovery_executed"])
        self.assertFalse(control["resubmission_executed"])
        self.assertEqual(result.data["trade_safety"]["side_effect_level"], "none")

    def test_pingan_exception_popup_confirmed_close_clicks_recognized_popup_only(self) -> None:
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "hwnd": 1002, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        text_payload = {"merged_texts": ["系统异常：委托失败"]}
        click_result = Result(ok=True, code=ErrorCode.OK, message="clicked result confirm", data={"strategy": "wm_command"})
        with (
            patch("tdxquant.trade.manager._find_result_dialog_for_lookup", return_value=result_dialog),
            patch("tdxquant.trade.manager._find_result_confirm_target_for_lookup", return_value=result_confirm),
            patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value=text_payload),
            patch("tdxquant.trade.manager._click_lookup_target", return_value=click_result) as mocked_click,
        ):
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.exception_popup(action="close", confirm_close=True, result_close_pre_delay=0.2)

        mocked_click.assert_called_once_with(result_confirm, post_delay=0.2)
        self.assertTrue(result.ok)
        control = result.data["exception_popup_control"]
        self.assertEqual(control["action"], "close")
        self.assertTrue(control["exception_detected"])
        self.assertTrue(control["close_executed"])
        self.assertTrue(control["confirm_click_executed"])
        self.assertFalse(control["retry_executed"])
        self.assertFalse(control["recovery_executed"])
        self.assertFalse(control["resubmission_executed"])
        self.assertFalse(control["order_submitted"])
        self.assertEqual(control["side_effect_level"], "live_side_effecting")
        self.assertEqual(result.data["trade_safety"]["side_effect_level"], "live_side_effecting")

    def test_pingan_exception_popup_close_skips_non_exception_result_dialog(self) -> None:
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "hwnd": 1002, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        text_payload = {"merged_texts": ["委托已提交"]}
        with (
            patch("tdxquant.trade.manager._find_result_dialog_for_lookup", return_value=result_dialog),
            patch("tdxquant.trade.manager._find_result_confirm_target_for_lookup", return_value=result_confirm),
            patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value=text_payload),
            patch("tdxquant.trade.manager._click_lookup_target") as mocked_click,
        ):
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.exception_popup(action="close", confirm_close=True)

        mocked_click.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.CONTROL_NOT_FOUND)
        control = result.data["exception_popup_control"]
        self.assertFalse(control["exception_detected"])
        self.assertFalse(control["close_executed"])
        self.assertFalse(control["confirm_click_executed"])
        self.assertFalse(control["retry_executed"])
        self.assertFalse(control["recovery_executed"])
        self.assertFalse(control["resubmission_executed"])

    def test_pingan_dialog_readiness_reports_desktop_lifecycle_gate_status(self) -> None:
        confirm_target = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1000, "name": "确认买入", "class_name": "Button", "automation_id": "1", "control_type": "Button"})()}
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with (
                patch("tdxquant.trade.manager._find_pingan_confirm_button", return_value=confirm_target),
                patch("tdxquant.trade.manager._find_pingan_result_dialog", return_value=result_dialog),
                patch("tdxquant.trade.manager._find_pingan_result_confirm_button", return_value=result_confirm),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    title_keyword="平安证券",
                    exe_path=r"D:\ProgramData\PinganSec\TdxW.exe",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.dialog_readiness(
                    dialog="both",
                    require_visible=True,
                    dialog_lookup_mode="uia",
                    confirm_timeout=2.5,
                    result_timeout=3.5,
                )

        self.assertTrue(result.ok)
        provenance = result.data["artifact_provenance"]
        self.assertEqual(provenance["schema"], "tdx.desktop_trade.pingan_readiness_evidence_artifact.v1")
        self.assertEqual(provenance["source_kind"], "dialog_readiness")
        self.assertEqual(provenance["producer"], "trade dialog-readiness")
        self.assertEqual(provenance["evidence_schema"], "tdx.desktop_trade.pingan_desktop_lifecycle_gate_status.v1")
        lifecycle = result.data["desktop_lifecycle_gate_status"]
        self.assertEqual(lifecycle["schema_version"], "tdx.desktop_trade.pingan_desktop_lifecycle_gate_status.v1")
        self.assertEqual(lifecycle["status"], "partial")
        self.assertEqual(lifecycle["execution_mode"], "readonly_dialog_readiness")
        self.assertEqual(lifecycle["side_effect_level"], "none")
        self.assertFalse(lifecycle["order_submitted"])
        self.assertFalse(lifecycle["control_dispatch_executed"])
        self.assertEqual(lifecycle["dialog_checks"]["confirm_lookup"]["status"], "ok")
        self.assertEqual(lifecycle["dialog_checks"]["result_dialog_lookup"]["status"], "ok")
        self.assertEqual(lifecycle["dialog_checks"]["result_confirm_lookup"]["status"], "ok")
        self.assertEqual(lifecycle["timeouts"]["confirm_timeout"], 2.5)
        self.assertEqual(lifecycle["timeouts"]["result_timeout"], 3.5)
        self.assertEqual(lifecycle["declared_process_window_ownership"]["title_keyword"], "平安证券")
        self.assertEqual(lifecycle["declared_process_window_ownership"]["exe_path"], r"D:\ProgramData\PinganSec\TdxW.exe")
        self.assertIn("exception_popup_handling", lifecycle["remaining_lifecycle_gates"])
        self.assertIn("retry_policy", lifecycle["remaining_lifecycle_gates"])
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertFalse(audit_dir.exists())

    def test_pingan_dialog_readiness_reports_observed_process_window_ownership_without_side_effects(self) -> None:
        confirm_target = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1000, "name": "确认买入", "class_name": "Button", "automation_id": "1", "control_type": "Button"})()}
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        health = Result(
            ok=True,
            code=ErrorCode.OK,
            message="health-check passed",
            data={
                "runtime": {"ok": True, "data": {"windows_path": r"D:\ProgramData\PinganSec\TdxW.exe"}},
                "window": {"ok": True, "data": {"main_hwnd": 1000, "title_keyword": "平安证券"}},
                "path_mapping": {"windows_path": r"D:\ProgramData\PinganSec\TdxW.exe", "wsl_path": None},
            },
        )
        adapter = type("Adapter", (), {"health_check": lambda self: health})()
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with (
                patch("tdxquant.trade.manager.PingAnBrokerAdapter", return_value=adapter) as adapter_cls,
                patch("tdxquant.trade.manager._find_pingan_confirm_button", return_value=confirm_target),
                patch("tdxquant.trade.manager._find_pingan_result_dialog", return_value=result_dialog),
                patch("tdxquant.trade.manager._find_pingan_result_confirm_button", return_value=result_confirm),
                patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value={"merged_texts": []}),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    title_keyword="平安证券",
                    exe_path=r"D:\ProgramData\PinganSec\TdxW.exe",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.dialog_readiness(dialog="both", require_visible=True)

        self.assertTrue(result.ok)
        lifecycle = result.data["desktop_lifecycle_gate_status"]
        ownership = lifecycle["observed_process_window_ownership"]
        adapter_cls.assert_called_once_with(
            title_keyword="平安证券",
            exe_path=r"D:\ProgramData\PinganSec\TdxW.exe",
        )
        self.assertEqual(ownership["status"], "observed")
        self.assertEqual(ownership["title_keyword"], "平安证券")
        self.assertEqual(ownership["exe_path"], r"D:\ProgramData\PinganSec\TdxW.exe")
        self.assertTrue(ownership["runtime_ok"])
        self.assertTrue(ownership["window_ok"])
        self.assertEqual(ownership["health_result"], health.to_dict())
        self.assertEqual(lifecycle["side_effect_level"], "none")
        self.assertFalse(lifecycle["order_submitted"])
        self.assertFalse(lifecycle["control_dispatch_executed"])
        self.assertIn("process_window_lifecycle_ownership", lifecycle["remaining_lifecycle_gates"])
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertFalse(audit_dir.exists())

    def test_pingan_dialog_readiness_reports_retry_policy_status_without_executing_retry(self) -> None:
        confirm_target = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1000, "name": "确认买入", "class_name": "Button", "automation_id": "1", "control_type": "Button"})()}
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with (
                patch("tdxquant.trade.manager._find_pingan_confirm_button", return_value=confirm_target),
                patch("tdxquant.trade.manager._find_pingan_result_dialog", return_value=result_dialog),
                patch("tdxquant.trade.manager._find_pingan_result_confirm_button", return_value=result_confirm),
                patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value={"merged_texts": []}),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.dialog_readiness(dialog="both", require_visible=True)

        self.assertTrue(result.ok)
        lifecycle = result.data["desktop_lifecycle_gate_status"]
        retry_policy = lifecycle["retry_policy_status"]
        self.assertEqual(retry_policy["status"], "not_configured")
        self.assertEqual(retry_policy["execution_mode"], "readonly_policy_status")
        self.assertEqual(retry_policy["policy_source"], "trade_profile")
        self.assertEqual(retry_policy["configured_policy"], {})
        self.assertFalse(retry_policy["retry_executed"])
        self.assertFalse(retry_policy["backoff_executed"])
        self.assertFalse(retry_policy["recovery_executed"])
        self.assertFalse(retry_policy["resubmission_executed"])
        self.assertEqual(lifecycle["side_effect_level"], "none")
        self.assertFalse(lifecycle["order_submitted"])
        self.assertFalse(lifecycle["control_dispatch_executed"])
        self.assertIn("retry_policy", lifecycle["remaining_lifecycle_gates"])
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertFalse(audit_dir.exists())

    def test_pingan_dialog_readiness_reports_exception_popup_handling_status_without_handling(self) -> None:
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        text_payload = {
            "merged_texts": ["系统异常：委托失败"],
            "contract_no": None,
            "uia_texts": ["系统异常：委托失败"],
        }
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with (
                patch("tdxquant.trade.manager._find_pingan_result_dialog", return_value=result_dialog),
                patch("tdxquant.trade.manager._find_pingan_result_confirm_button", return_value=result_confirm),
                patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value=text_payload),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.dialog_readiness(dialog="result", require_visible=True)

        self.assertTrue(result.ok)
        lifecycle = result.data["desktop_lifecycle_gate_status"]
        handling = lifecycle["exception_popup_handling_status"]
        self.assertEqual(handling["status"], "manual_required")
        self.assertEqual(handling["execution_mode"], "readonly_handling_status")
        self.assertFalse(handling["handling_available"])
        self.assertTrue(handling["exception_detected"])
        self.assertEqual(handling["lookup_status"], "warning")
        self.assertIn("异常", handling["matched_keywords"])
        self.assertFalse(handling["close_executed"])
        self.assertFalse(handling["confirm_click_executed"])
        self.assertFalse(handling["recovery_executed"])
        self.assertFalse(handling["retry_executed"])
        self.assertFalse(handling["resubmission_executed"])
        self.assertTrue(handling["manual_action_required"])
        self.assertEqual(lifecycle["side_effect_level"], "none")
        self.assertFalse(lifecycle["order_submitted"])
        self.assertFalse(lifecycle["control_dispatch_executed"])
        self.assertIn("exception_popup_handling", lifecycle["remaining_lifecycle_gates"])
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertFalse(audit_dir.exists())

    def test_pingan_dialog_readiness_reports_statefile_lock_status_without_locking(self) -> None:
        confirm_target = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1000, "name": "确认买入", "class_name": "Button", "automation_id": "1", "control_type": "Button"})()}
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with (
                patch("tdxquant.trade.manager._find_pingan_confirm_button", return_value=confirm_target),
                patch("tdxquant.trade.manager._find_pingan_result_dialog", return_value=result_dialog),
                patch("tdxquant.trade.manager._find_pingan_result_confirm_button", return_value=result_confirm),
                patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value={"merged_texts": []}),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.dialog_readiness(dialog="both", require_visible=True)

        self.assertTrue(result.ok)
        lifecycle = result.data["desktop_lifecycle_gate_status"]
        lock_status = lifecycle["statefile_lock_status"]
        self.assertEqual(lock_status["status"], "not_acquired")
        self.assertEqual(lock_status["execution_mode"], "readonly_lock_status")
        self.assertFalse(lock_status["lock_acquired"])
        self.assertIsNone(lock_status["owner_token"])
        self.assertFalse(lock_status["statefile_write_executed"])
        self.assertFalse(lock_status["event_log_write_executed"])
        self.assertFalse(lock_status["submission_ledger_write_executed"])
        self.assertFalse(lock_status["trade_audit_write_executed"])
        self.assertEqual(lock_status["artifact_targets"]["last_order_state_path"], str(state_path))
        self.assertEqual(lock_status["artifact_targets"]["order_event_log_path"], str(event_log_path))
        self.assertEqual(lock_status["artifact_targets"]["submission_ledger_path"], str(ledger_path))
        self.assertEqual(lock_status["artifact_targets"]["trade_audit_dir"], str(audit_dir))
        self.assertEqual(lifecycle["side_effect_level"], "none")
        self.assertFalse(lifecycle["order_submitted"])
        self.assertFalse(lifecycle["control_dispatch_executed"])
        self.assertIn("process_window_lifecycle_ownership", lifecycle["remaining_lifecycle_gates"])
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertFalse(audit_dir.exists())

    def test_pingan_dialog_readiness_reports_lifecycle_control_status_without_control(self) -> None:
        confirm_target = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1000, "name": "确认买入", "class_name": "Button", "automation_id": "1", "control_type": "Button"})()}
        result_dialog = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})()}
        result_confirm = {"ok": True, "lookup_mode": "uia", "info": type("Info", (), {"handle": 1002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})()}
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with (
                patch("tdxquant.trade.manager._find_pingan_confirm_button", return_value=confirm_target),
                patch("tdxquant.trade.manager._find_pingan_result_dialog", return_value=result_dialog),
                patch("tdxquant.trade.manager._find_pingan_result_confirm_button", return_value=result_confirm),
                patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value={"merged_texts": []}),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    title_keyword="平安证券",
                    exe_path=r"D:\ProgramData\PinganSec\TdxW.exe",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.dialog_readiness(dialog="both", require_visible=True)

        self.assertTrue(result.ok)
        lifecycle = result.data["desktop_lifecycle_gate_status"]
        control = lifecycle["lifecycle_control_status"]
        self.assertEqual(control["status"], "not_owned")
        self.assertEqual(control["execution_mode"], "readonly_lifecycle_control_status")
        self.assertFalse(control["control_available"])
        self.assertEqual(control["title_keyword"], "平安证券")
        self.assertEqual(control["exe_path"], r"D:\ProgramData\PinganSec\TdxW.exe")
        self.assertFalse(control["start_executed"])
        self.assertFalse(control["stop_executed"])
        self.assertFalse(control["restart_executed"])
        self.assertFalse(control["supervisor_owned"])
        self.assertFalse(control["backoff_executed"])
        self.assertFalse(control["process_kill_executed"])
        self.assertFalse(control["pid_ownership_claimed"])
        self.assertEqual(lifecycle["side_effect_level"], "none")
        self.assertFalse(lifecycle["order_submitted"])
        self.assertFalse(lifecycle["control_dispatch_executed"])
        self.assertIn("process_window_lifecycle_ownership", lifecycle["remaining_lifecycle_gates"])
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertFalse(audit_dir.exists())

    def test_pingan_lifecycle_owner_lock_acquires_statefile_without_desktop_control(self) -> None:
        with TemporaryDirectory() as temp_dir:
            statefile_path = Path(temp_dir) / "lifecycle" / "pingan-owner.json"
            lock_path = Path(str(statefile_path) + ".lock")
            manager = TdxTradeManager(profile="balanced")

            result = manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(statefile_path),
                owner_token="owner-a",
                stale_after_seconds=60.0,
            )

            self.assertTrue(result.ok)
            owner_lock = result.data["lifecycle_owner_lock"]
            self.assertEqual(owner_lock["status"], "owned")
            self.assertEqual(owner_lock["action"], "acquire")
            self.assertEqual(owner_lock["execution_mode"], "explicit_operator_lifecycle_owner_lock")
            self.assertEqual(owner_lock["statefile_path"], str(statefile_path))
            self.assertEqual(owner_lock["lock_path"], str(lock_path))
            self.assertEqual(owner_lock["owner_token"], "owner-a")
            self.assertTrue(owner_lock["lock_acquired"])
            self.assertTrue(owner_lock["statefile_write_executed"])
            self.assertTrue(owner_lock["lock_file_write_executed"])
            self.assertFalse(owner_lock["event_log_write_executed"])
            self.assertFalse(owner_lock["submission_ledger_write_executed"])
            self.assertFalse(owner_lock["trade_audit_write_executed"])
            self.assertFalse(owner_lock["order_submitted"])
            self.assertFalse(owner_lock["control_dispatch_executed"])
            self.assertFalse(owner_lock["start_executed"])
            self.assertFalse(owner_lock["stop_executed"])
            self.assertFalse(owner_lock["restart_executed"])
            self.assertFalse(owner_lock["supervisor_owned"])
            self.assertFalse(owner_lock["backoff_executed"])
            self.assertFalse(owner_lock["process_kill_executed"])
            self.assertFalse(owner_lock["pid_ownership_claimed"])
            self.assertEqual(owner_lock["side_effect_level"], "local_lifecycle_statefile")
            self.assertTrue(statefile_path.exists())
            self.assertTrue(lock_path.exists())

            state_payload = json.loads(statefile_path.read_text(encoding="utf-8"))
            self.assertEqual(state_payload["schema_version"], "tdx.desktop_trade.pingan_lifecycle_owner_state.v1")
            self.assertEqual(state_payload["status"], "owned")
            self.assertEqual(state_payload["owner_token"], "owner-a")
            self.assertEqual(state_payload["statefile_path"], str(statefile_path))
            self.assertEqual(state_payload["lock_path"], str(lock_path))

    def test_pingan_lifecycle_owner_lock_releases_owned_statefile(self) -> None:
        with TemporaryDirectory() as temp_dir:
            statefile_path = Path(temp_dir) / "pingan-owner.json"
            lock_path = Path(str(statefile_path) + ".lock")
            manager = TdxTradeManager(profile="balanced")
            manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(statefile_path),
                owner_token="owner-a",
                stale_after_seconds=60.0,
            )

            result = manager.pingan.lifecycle_owner_lock(
                action="release",
                statefile_path=str(statefile_path),
                owner_token="owner-a",
                stale_after_seconds=60.0,
            )

            self.assertTrue(result.ok)
            owner_lock = result.data["lifecycle_owner_lock"]
            self.assertEqual(owner_lock["status"], "released")
            self.assertEqual(owner_lock["action"], "release")
            self.assertTrue(owner_lock["lock_released"])
            self.assertTrue(owner_lock["statefile_write_executed"])
            self.assertFalse(owner_lock["lock_acquired"])
            self.assertFalse(owner_lock["control_dispatch_executed"])
            self.assertFalse(owner_lock["restart_executed"])
            self.assertFalse(lock_path.exists())
            state_payload = json.loads(statefile_path.read_text(encoding="utf-8"))
            self.assertEqual(state_payload["status"], "released")
            self.assertEqual(state_payload["owner_token"], "owner-a")

    def test_pingan_lifecycle_owner_lock_status_reports_stale_without_writing(self) -> None:
        with TemporaryDirectory() as temp_dir:
            statefile_path = Path(temp_dir) / "pingan-owner.json"
            lock_path = Path(str(statefile_path) + ".lock")
            statefile_path.write_text(
                json.dumps(
                    {
                        "schema_version": "tdx.desktop_trade.pingan_lifecycle_owner_state.v1",
                        "status": "owned",
                        "owner_token": "owner-a",
                        "updated_at": "2000-01-01T00:00:00+00:00",
                        "statefile_path": str(statefile_path),
                        "lock_path": str(lock_path),
                    }
                ),
                encoding="utf-8",
            )
            lock_path.write_text("owner-a", encoding="utf-8")
            before_payload = statefile_path.read_text(encoding="utf-8")

            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.lifecycle_owner_lock(
                action="status",
                statefile_path=str(statefile_path),
                owner_token="owner-b",
                stale_after_seconds=1.0,
            )

            self.assertTrue(result.ok)
            owner_lock = result.data["lifecycle_owner_lock"]
            self.assertEqual(owner_lock["status"], "stale")
            self.assertEqual(owner_lock["action"], "status")
            self.assertTrue(owner_lock["stale_detected"])
            self.assertEqual(owner_lock["current_owner_token"], "owner-a")
            self.assertFalse(owner_lock["statefile_write_executed"])
            self.assertFalse(owner_lock["lock_file_write_executed"])
            self.assertFalse(owner_lock["lock_released"])
            self.assertEqual(statefile_path.read_text(encoding="utf-8"), before_payload)

    def test_pingan_lifecycle_owner_lock_status_reports_owner_pid_alive_without_claiming_ownership(self) -> None:
        with TemporaryDirectory() as temp_dir:
            statefile_path = Path(temp_dir) / "pingan-owner.json"
            manager = TdxTradeManager(profile="balanced")
            manager.pingan.lifecycle_owner_lock(
                action="acquire",
                statefile_path=str(statefile_path),
                owner_token="owner-a",
                stale_after_seconds=60.0,
            )

            result = manager.pingan.lifecycle_owner_lock(
                action="status",
                statefile_path=str(statefile_path),
                owner_token="owner-a",
                stale_after_seconds=60.0,
            )

            self.assertTrue(result.ok)
            owner_lock = result.data["lifecycle_owner_lock"]
            self.assertTrue(owner_lock["pid_validation_executed"])
            self.assertEqual(owner_lock["owner_pid"], os.getpid())
            self.assertTrue(owner_lock["owner_pid_alive"])
            self.assertEqual(owner_lock["owner_pid_status"], "alive")
            self.assertFalse(owner_lock["pid_ownership_claimed"])
            self.assertFalse(owner_lock["process_kill_executed"])
            self.assertFalse(owner_lock["restart_executed"])

    def test_pingan_lifecycle_owner_lock_status_reports_missing_owner_pid(self) -> None:
        with TemporaryDirectory() as temp_dir:
            statefile_path = Path(temp_dir) / "pingan-owner.json"
            lock_path = Path(str(statefile_path) + ".lock")
            statefile_path.write_text(
                json.dumps(
                    {
                        "schema_version": "tdx.desktop_trade.pingan_lifecycle_owner_state.v1",
                        "status": "owned",
                        "owner_token": "owner-a",
                        "updated_at": "2099-01-01T00:00:00+00:00",
                        "statefile_path": str(statefile_path),
                        "lock_path": str(lock_path),
                    }
                ),
                encoding="utf-8",
            )
            lock_path.write_text("owner-a", encoding="utf-8")

            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.lifecycle_owner_lock(
                action="status",
                statefile_path=str(statefile_path),
                owner_token="owner-a",
                stale_after_seconds=60.0,
            )

            self.assertTrue(result.ok)
            owner_lock = result.data["lifecycle_owner_lock"]
            self.assertTrue(owner_lock["pid_validation_executed"])
            self.assertIsNone(owner_lock["owner_pid"])
            self.assertIsNone(owner_lock["owner_pid_alive"])
            self.assertEqual(owner_lock["owner_pid_status"], "missing")
            self.assertFalse(owner_lock["pid_ownership_claimed"])

    def test_pingan_submit_ready_reaches_confirm_boundary_without_writing_live_artifacts(self) -> None:
        probe_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="completed pingan HID submit probe",
            data={"input": {"code": "000001", "price": "10.00", "quantity": 100}, "steps": []},
        )
        confirm_target = {
            "ok": True,
            "lookup_mode": "uia",
            "info": type(
                "Info",
                (),
                {"handle": 1001, "name": "确认买入", "class_name": "Button", "automation_id": "1", "control_type": "Button"},
            )(),
        }
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with (
                patch("tdxquant.trade.manager.run_pingan_hid_submit_probe", return_value=probe_result) as mocked_probe,
                patch("tdxquant.trade.manager._find_confirm_target_for_lookup", return_value=confirm_target),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.submit_ready(port="COM3", code="000001", price="10.00", quantity=100, max_price=10.50)
        self.assertTrue(result.ok)
        mocked_probe.assert_called_once()
        self.assertEqual(result.data["manager"]["method"], "submit_ready")
        self.assertEqual(result.data["submit_ready"]["overall_status"], "ok")
        self.assertTrue(result.data["submit_ready"]["manual_confirmation_required"])
        self.assertEqual(result.data["trade_safety"]["side_effect_level"], "local_state_mutating")
        self.assertTrue(result.data["trade_safety"]["risk_gate"]["passed"])
        self.assertFalse(state_path.exists())
        self.assertFalse(event_log_path.exists())
        self.assertFalse(ledger_path.exists())
        self.assertFalse(audit_dir.exists())
        self.assertNotIn("artifacts", result.data)

    def test_pingan_submit_ready_fails_when_confirm_dialog_is_not_detected(self) -> None:
        probe_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="completed pingan HID submit probe",
            data={"input": {"code": "000001", "price": "10.00", "quantity": 100}, "steps": []},
        )
        with (
            patch("tdxquant.trade.manager.run_pingan_hid_submit_probe", return_value=probe_result),
            patch(
                "tdxquant.trade.manager._find_confirm_target_for_lookup",
                return_value={"ok": False, "lookup_mode": "uia", "last_error": "confirm button not found"},
            ),
        ):
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.submit_ready(port="COM3", code="000001", price="10.00", quantity=100)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.CONTROL_NOT_FOUND)
        self.assertEqual(result.data["submit_ready"]["overall_status"], "failed")
        checks = {item["name"]: item for item in result.data["submit_ready"]["checks"]}
        self.assertEqual(checks["confirm_lookup"]["status"], "failed")
        self.assertTrue(result.data["submit_ready"]["manual_confirmation_required"])

    def test_pingan_submit_ready_rejects_risk_gate_before_ui_side_effects(self) -> None:
        with patch("tdxquant.trade.manager.run_pingan_hid_submit_probe") as mocked_probe:
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.submit_ready(port="COM3", code="000001", price="10.00", quantity=100, max_price=9.50)
        mocked_probe.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertFalse(result.data["trade_safety"]["risk_gate"]["passed"])

    def test_pingan_submit_ready_requires_owner_lock_before_ui_side_effects(self) -> None:
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            lifecycle_lock_path = Path(f"{lifecycle_statefile_path}.lock")
            manager = TdxTradeManager(profile="balanced")
            with (
                patch("tdxquant.trade.manager.run_pingan_hid_submit_probe") as mocked_probe,
                patch("tdxquant.trade.manager._find_confirm_target_for_lookup") as mocked_lookup,
            ):
                result = manager.pingan.submit_ready(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    lifecycle_statefile_path=str(lifecycle_statefile_path),
                    lifecycle_owner_token="submit-ready-owner",
                    lifecycle_stale_after_seconds=60.0,
                    require_lifecycle_owner_lock=True,
                )

        mocked_probe.assert_not_called()
        mocked_lookup.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        risk_gate = result.data["trade_safety"]["risk_gate"]
        self.assertFalse(risk_gate["passed"])
        owner_lock_status = risk_gate["lifecycle_owner_lock_required_status"]
        self.assertTrue(owner_lock_status["required"])
        self.assertEqual(owner_lock_status["requirement_status"], "failed")
        self.assertEqual(owner_lock_status["status"], "not_acquired")
        self.assertFalse(owner_lock_status["statefile_write_executed"])
        self.assertFalse(owner_lock_status["lock_file_write_executed"])
        self.assertFalse(owner_lock_status["control_dispatch_executed"])
        self.assertFalse(lifecycle_statefile_path.exists())
        self.assertFalse(lifecycle_lock_path.exists())

    def test_pingan_confirm_current_advances_confirmation_and_writes_artifacts(self) -> None:
        confirm_target = {
            "ok": True,
            "hwnd": 1001,
            "lookup_mode": "uia",
            "info": type("Info", (), {"handle": 1001, "name": "确认买入", "class_name": "Button", "automation_id": "1", "control_type": "Button"})(),
        }
        result_dialog = {
            "ok": True,
            "lookup_mode": "uia",
            "info": type("Info", (), {"handle": 2001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})(),
            "element": object(),
        }
        result_confirm = {
            "ok": True,
            "hwnd": 2002,
            "lookup_mode": "uia",
            "info": type("Info", (), {"handle": 2002, "name": "确认", "class_name": "Button", "automation_id": "7015", "control_type": "Button"})(),
        }
        click_ok = Result(ok=True, code=ErrorCode.OK, message="clicked runtime Win32 control via wm_command", data={"hwnd": 1001})
        close_ok = Result(ok=True, code=ErrorCode.OK, message="clicked runtime Win32 control via wm_command", data={"hwnd": 2002})
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with (
                patch("tdxquant.trade.manager._find_confirm_target_for_lookup", return_value=confirm_target),
                patch("tdxquant.trade.manager._click_runtime_hwnd", side_effect=[click_ok, close_ok]) as mocked_click,
                patch("tdxquant.trade.manager._find_result_dialog_for_lookup", return_value=result_dialog),
                patch("tdxquant.trade.manager._find_result_confirm_target_for_lookup", return_value=result_confirm),
                patch("tdxquant.trade.manager._safe_serialize_runtime_element", return_value={"handle": 2001, "name": "提示"}),
                patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value={"contract_no": "B202604290001"}),
            ):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.confirm_current(close_result_dialog=True)
                state_exists = state_path.exists()
                event_exists = event_log_path.exists()
                ledger_exists = ledger_path.exists()
                audit_path = Path(result.data["artifacts"]["trade_audit_path"])
                audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
                state_payload = json.loads(state_path.read_text(encoding="utf-8"))
                event_row = json.loads(event_log_path.read_text(encoding="utf-8").splitlines()[-1])
        self.assertTrue(result.ok)
        self.assertEqual(result.data["manager"]["method"], "confirm_current")
        self.assertEqual(result.data["confirm_current"]["overall_status"], "ok")
        self.assertTrue(result.data["confirm_current"]["result_dialog_closed"])
        self.assertEqual(result.data["trade_safety"]["side_effect_level"], "live_side_effecting")
        self.assertEqual(result.data["trade_audit"]["status"], "confirmed")
        self.assertTrue(state_exists)
        self.assertTrue(event_exists)
        self.assertFalse(ledger_exists)
        self.assertEqual(state_payload["trade_audit"]["audit_id"], result.data["trade_audit"]["audit_id"])
        self.assertEqual(event_row["trade_audit"]["audit_id"], result.data["trade_audit"]["audit_id"])
        self.assertEqual(audit_payload["trade_audit"]["audit_id"], result.data["trade_audit"]["audit_id"])
        self.assertNotIn("submission_ledger_path", result.data.get("artifacts", {}))
        self.assertEqual(mocked_click.call_count, 2)

    def test_pingan_confirm_current_requires_owner_lock_before_ui_side_effects(self) -> None:
        with TemporaryDirectory() as temp_dir:
            lifecycle_statefile_path = Path(temp_dir) / "pingan-lifecycle-owner.json"
            lifecycle_lock_path = Path(f"{lifecycle_statefile_path}.lock")
            manager = TdxTradeManager(profile="balanced")
            with patch("tdxquant.trade.manager._find_confirm_target_for_lookup") as mocked_lookup:
                result = manager.pingan.confirm_current(
                    lifecycle_statefile_path=str(lifecycle_statefile_path),
                    lifecycle_owner_token="confirm-owner",
                    lifecycle_stale_after_seconds=60.0,
                    require_lifecycle_owner_lock=True,
                )

        mocked_lookup.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        risk_gate = result.data["trade_safety"]["risk_gate"]
        self.assertFalse(risk_gate["passed"])
        owner_lock_status = risk_gate["lifecycle_owner_lock_required_status"]
        self.assertTrue(owner_lock_status["required"])
        self.assertEqual(owner_lock_status["requirement_status"], "failed")
        self.assertEqual(owner_lock_status["status"], "not_acquired")
        self.assertFalse(owner_lock_status["statefile_write_executed"])
        self.assertFalse(owner_lock_status["lock_file_write_executed"])
        self.assertFalse(owner_lock_status["control_dispatch_executed"])
        self.assertFalse(lifecycle_statefile_path.exists())
        self.assertFalse(lifecycle_lock_path.exists())

    def test_pingan_confirm_current_requires_broker_readiness_before_ui_side_effects(self) -> None:
        broker_health = Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="runtime path resolved but trading window was not found",
            data={"runtime": {"ok": True}, "window": {"ok": False}},
            next_action="Bring Ping An to the foreground and retry.",
        )
        manager = TdxTradeManager(profile="balanced")
        with (
            patch("tdxquant.trade.manager.PingAnBrokerAdapter.health_check", return_value=broker_health) as mocked_health,
            patch("tdxquant.trade.manager._find_confirm_target_for_lookup") as mocked_lookup,
            patch("tdxquant.trade.manager._click_lookup_target") as mocked_click,
        ):
            result = manager.pingan.confirm_current(require_broker_readiness=True)

        mocked_health.assert_called_once()
        mocked_lookup.assert_not_called()
        mocked_click.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.CONTROL_NOT_FOUND)
        self.assertEqual(result.data["manager"]["method"], "confirm_current")
        self.assertEqual(result.data["trade_safety"]["side_effect_level"], "none")
        risk_gate = result.data["trade_safety"]["risk_gate"]
        self.assertFalse(risk_gate["passed"])
        readiness = risk_gate["broker_readiness_required_status"]
        self.assertTrue(readiness["required"])
        self.assertEqual(readiness["requirement_status"], "failed")
        self.assertFalse(readiness["broker_health_ok"])
        self.assertFalse(readiness["control_dispatch_executed"])
        self.assertFalse(result.data["confirm_current"]["confirmation_advanced"])
        self.assertFalse(result.data["confirm_current"]["result_dialog_closed"])
        self.assertEqual(result.next_action, "Bring Ping An to the foreground and retry.")

    def test_pingan_confirm_current_warns_when_result_dialog_is_not_detected(self) -> None:
        confirm_target = {
            "ok": True,
            "hwnd": 1001,
            "lookup_mode": "uia",
            "info": type("Info", (), {"handle": 1001, "name": "确认买入", "class_name": "Button", "automation_id": "1", "control_type": "Button"})(),
        }
        click_ok = Result(ok=True, code=ErrorCode.OK, message="clicked runtime Win32 control via wm_command", data={"hwnd": 1001})
        with (
            patch("tdxquant.trade.manager._find_confirm_target_for_lookup", return_value=confirm_target),
            patch("tdxquant.trade.manager._click_runtime_hwnd", return_value=click_ok),
            patch(
                "tdxquant.trade.manager._find_result_dialog_for_lookup",
                return_value={"ok": False, "lookup_mode": "uia", "last_error": "result dialog not found"},
            ),
        ):
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.confirm_current(close_result_dialog=True)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["confirm_current"]["overall_status"], "degraded")
        checks = {item["name"]: item for item in result.data["confirm_current"]["checks"]}
        self.assertEqual(checks["result_dialog_lookup"]["status"], "warning")

    def test_pingan_confirm_current_keeps_result_dialog_open_when_requested(self) -> None:
        confirm_target = {
            "ok": True,
            "hwnd": 1001,
            "lookup_mode": "uia",
            "info": type("Info", (), {"handle": 1001, "name": "确认买入", "class_name": "Button", "automation_id": "1", "control_type": "Button"})(),
        }
        result_dialog = {
            "ok": True,
            "lookup_mode": "uia",
            "info": type("Info", (), {"handle": 2001, "name": "提示", "class_name": "#32770", "automation_id": "", "control_type": "Pane"})(),
            "element": object(),
        }
        click_ok = Result(ok=True, code=ErrorCode.OK, message="clicked runtime Win32 control via wm_command", data={"hwnd": 1001})
        with (
            patch("tdxquant.trade.manager._find_confirm_target_for_lookup", return_value=confirm_target),
            patch("tdxquant.trade.manager._click_runtime_hwnd", return_value=click_ok),
            patch("tdxquant.trade.manager._find_result_dialog_for_lookup", return_value=result_dialog),
            patch("tdxquant.trade.manager._find_result_confirm_target_for_lookup") as mocked_result_confirm,
            patch("tdxquant.trade.manager._safe_serialize_runtime_element", return_value={"handle": 2001, "name": "提示"}),
            patch("tdxquant.trade.manager._extract_dialog_text_payload_from_sources", return_value={"contract_no": "B202604290002"}),
        ):
            manager = TdxTradeManager(profile="balanced")
            result = manager.pingan.confirm_current(close_result_dialog=False)
        self.assertTrue(result.ok)
        self.assertFalse(result.data["confirm_current"]["result_dialog_closed"])
        mocked_result_confirm.assert_not_called()

    def test_pingan_buy_duplicate_submission_key_skips_desktop_and_reuses_prior_outcome(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "result_dialog": {"contract_no": "B202604260003"},
            },
        )
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with patch("tdxquant.trade.manager.run_pingan_buy_fast", return_value=expected) as mocked:
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                first = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="dup-20260428-001",
                )
                second = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="dup-20260428-001",
                )
                ledger_rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
                audit_files = sorted(audit_dir.glob("*.json"))
        mocked.assert_called_once()
        self.assertTrue(first.ok)
        self.assertTrue(second.ok)
        self.assertEqual(second.data["result_dialog"]["contract_no"], "B202604260003")
        self.assertEqual(first.data["trade_audit"]["status"], "confirmed")
        self.assertEqual(second.data["trade_audit"]["status"], "replayed")
        self.assertEqual(second.data["trade_safety"]["idempotency"]["decision"], "skip_duplicate")
        self.assertTrue(any("duplicate submission_key skipped" in warning for warning in second.warnings))
        self.assertEqual(second.data["artifacts"]["submission_ledger_path"], str(ledger_path))
        self.assertEqual(len(audit_files), 2)
        self.assertEqual(len(ledger_rows), 2)
        self.assertEqual(ledger_rows[0]["idempotency"]["decision"], "execute")
        self.assertEqual(ledger_rows[1]["idempotency"]["decision"], "skip_duplicate")

    def test_pingan_buy_rejected_request_writes_trade_audit_artifact(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with patch("tdxquant.trade.manager.run_pingan_buy_fast") as mocked:
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.buy(
                    port="COM3",
                    code="ABC123",
                    price="10.00",
                    quantity=100,
                )
                audit_path = Path(result.data["artifacts"]["trade_audit_path"])
                audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
                state_payload = json.loads(state_path.read_text(encoding="utf-8"))
                event_row = json.loads(event_log_path.read_text(encoding="utf-8").splitlines()[-1])
        mocked.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.data["trade_audit"]["status"], "rejected")
        self.assertEqual(audit_payload["trade_audit"]["status"], "rejected")
        self.assertEqual(state_payload["trade_audit"]["audit_id"], result.data["trade_audit"]["audit_id"])
        self.assertEqual(event_row["trade_audit"]["audit_id"], result.data["trade_audit"]["audit_id"])
        audit_gate = result.data["trade_audit_gate_status"]
        self.assertEqual(audit_gate["covered_audit_status"], "rejected")
        self.assertEqual(audit_gate["artifact_paths"]["trade_audit_path"], str(audit_path))
        self.assertTrue(audit_gate["persisted_artifacts"]["last_order_state"])
        self.assertTrue(audit_gate["persisted_artifacts"]["order_event_log"])
        self.assertFalse(audit_gate["persisted_artifacts"]["submission_ledger"])
        self.assertIn("confirmed", audit_gate["remaining_audit_gate_statuses"])

    def test_pingan_buy_exception_result_writes_exception_audit_status(self) -> None:
        expected = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="desktop exception while waiting for result dialog",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "desktop_exception": {
                    "type": "TimeoutError",
                    "stage": "result_dialog",
                    "message": "result dialog timed out",
                },
            },
        )
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with patch("tdxquant.trade.manager.run_pingan_buy_fast", return_value=expected) as mocked:
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="exception-20260428-001",
                )
                audit_path = Path(result.data["artifacts"]["trade_audit_path"])
                audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
        mocked.assert_called_once()
        self.assertFalse(result.ok)
        self.assertEqual(result.data["trade_audit"]["status"], "exception")
        self.assertEqual(audit_payload["trade_audit"]["status"], "exception")
        self.assertEqual(audit_payload["result"]["data"]["desktop_exception"]["stage"], "result_dialog")
        audit_gate = result.data["trade_audit_gate_status"]
        self.assertEqual(audit_gate["covered_audit_status"], "exception")
        self.assertEqual(audit_gate["artifact_paths"]["trade_audit_path"], str(audit_path))
        self.assertIn("failed", audit_gate["remaining_audit_gate_statuses"])

    def test_pingan_buy_failed_result_exposes_audit_status_classification(self) -> None:
        expected = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="desktop execution failed without explicit exception metadata",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "result_dialog": {
                    "status": "failed",
                    "message": "result dialog reported a generic failure",
                },
            },
        )
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            event_log_path = Path(temp_dir) / "events.jsonl"
            ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            audit_dir = Path(temp_dir) / "trade-audits"
            with patch("tdxquant.trade.manager.run_pingan_buy_fast", return_value=expected):
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(state_path),
                    event_log_path=str(event_log_path),
                    submission_ledger_path=str(ledger_path),
                    trade_audit_dir=str(audit_dir),
                )
                result = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="failed-20260428-001",
                )
                audit_path = Path(result.data["artifacts"]["trade_audit_path"])
                audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
        self.assertFalse(result.ok)
        self.assertEqual(result.data["trade_audit"]["status"], "failed")
        self.assertEqual(audit_payload["trade_audit"]["status"], "failed")
        audit_gate = result.data["trade_audit_gate_status"]
        self.assertEqual(audit_gate["covered_audit_status"], "failed")
        self.assertEqual(audit_gate["audit_status_classification"]["source"], "generic_execution_failure")
        self.assertFalse(audit_gate["audit_status_classification"]["explicit_exception_metadata"])
        self.assertFalse(audit_gate["audit_status_classification"]["rejected_request"])
        self.assertIn("exception", audit_gate["remaining_audit_gate_statuses"])

    def test_pingan_buy_rejects_conflicting_submission_key_after_side_effecting_attempt(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "result_dialog": {"contract_no": "B202604260004"},
            },
        )
        with TemporaryDirectory() as temp_dir:
            with patch("tdxquant.trade.manager.run_pingan_buy_fast", return_value=expected) as mocked:
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(Path(temp_dir) / "state.json"),
                    event_log_path=str(Path(temp_dir) / "events.jsonl"),
                    submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
                )
                first = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="conflict-20260428-001",
                )
                second = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.01",
                    quantity=100,
                    submission_key="conflict-20260428-001",
                )
        mocked.assert_called_once()
        self.assertTrue(first.ok)
        self.assertFalse(second.ok)
        self.assertEqual(second.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(second.data["trade_safety"]["idempotency"]["decision"], "reject_conflict")
        self.assertIn("submission_key", second.message)

    def test_pingan_buy_allows_retry_with_same_submission_key_after_pre_trade_rejection(self) -> None:
        expected = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "input": {"code": "000001", "price": "10.00", "quantity": 100},
                "result_dialog": {"contract_no": "B202604260005"},
            },
        )
        with TemporaryDirectory() as temp_dir:
            with patch("tdxquant.trade.manager.run_pingan_buy_fast", return_value=expected) as mocked:
                manager = TdxTradeManager(
                    profile="balanced",
                    state_path=str(Path(temp_dir) / "state.json"),
                    event_log_path=str(Path(temp_dir) / "events.jsonl"),
                    submission_ledger_path=str(Path(temp_dir) / "submission-ledger.jsonl"),
                )
                first = manager.pingan.buy(
                    port="COM3",
                    code="BAD000",
                    price="10.00",
                    quantity=100,
                    submission_key="retry-20260428-001",
                )
                second = manager.pingan.buy(
                    port="COM3",
                    code="000001",
                    price="10.00",
                    quantity=100,
                    submission_key="retry-20260428-001",
                )
        self.assertFalse(first.ok)
        self.assertEqual(first.code, ErrorCode.INVALID_REQUEST)
        self.assertTrue(second.ok)
        mocked.assert_called_once()
        self.assertEqual(second.data["trade_safety"]["idempotency"]["decision"], "execute")


if __name__ == "__main__":
    unittest.main()
