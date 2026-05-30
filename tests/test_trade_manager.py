import json
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
