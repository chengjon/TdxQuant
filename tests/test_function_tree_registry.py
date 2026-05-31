from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_function_tree_registry.py"


def _run_validator(root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(root), *extra_args],
        check=False,
        capture_output=True,
        text=True,
    )


def _write_function_tree(root: Path, body: str) -> None:
    (root / "FUNCTION_TREE.md").write_text(textwrap.dedent(body).strip() + "\n", encoding="utf-8")


def _write_openspec_change(root: Path, change_id: str, *, archived: bool) -> None:
    if archived:
        change_dir = root / "openspec" / "changes" / "archive" / f"2026-05-23-{change_id}"
    else:
        change_dir = root / "openspec" / "changes" / change_id
    change_dir.mkdir(parents=True)
    (change_dir / ".openspec.yaml").write_text("id: test\n", encoding="utf-8")


def _current_function_tree_rows() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in (REPO_ROOT / "FUNCTION_TREE.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) < 5 or columns[0] in {"ID", "---"}:
            continue
        rows[columns[0]] = {
            "feature": columns[1],
            "status": columns[2],
            "evidence": columns[3],
            "boundary": columns[4],
        }
    return rows


class FunctionTreeRegistryValidatorTests(unittest.TestCase):
    def test_current_function_tree_passes_validation(self) -> None:
        result = _run_validator(REPO_ROOT)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rows=", result.stdout)
        self.assertIn("[已实现]", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validator_json_report_summarizes_current_function_tree(self) -> None:
        result = _run_validator(REPO_ROOT, "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["valid"], True)
        self.assertGreater(payload["row_count"], 0)
        self.assertEqual(payload["problem_count"], 0)
        self.assertEqual(payload["errors"], [])
        self.assertIn("[已实现]", payload["status_counts"])
        self.assertEqual(result.stderr, "")

    def test_subscription_long_run_control_nodes_are_registered_as_implemented(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("B-16", "E-09"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[已实现]`")
                self.assertIn("SubscriptionWatchBackgroundController.restart", combined)
                self.assertIn("supervisor_tick", combined)
                self.assertIn("supervisor_run", combined)
                self.assertIn("statefile ownership", combined)
                self.assertIn("operator", combined)
                self.assertIn("不代表 live provider availability", combined)
                self.assertIn("不代表 broker readiness", combined)
                self.assertIn("不代表交易 readiness", combined)

    def test_pingan_task_plan_boundary_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("catalog plan --entry task-buy --view summary", combined)
        self.assertIn("catalog plan --entry task-sell --view summary", combined)
        self.assertIn("catalog plan --entry task-confirm-current --view summary", combined)
        self.assertIn("catalog preview --entry task-buy --view summary", combined)
        self.assertIn("catalog preview --entry task-sell --view summary", combined)
        self.assertIn("catalog preview --entry task-confirm-current --view summary", combined)
        self.assertIn("non_executing_catalog_plan", combined)
        self.assertIn("不执行 task/trade/report/bundle step", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("交易安全审批", combined)

    def test_pingan_bundle_command_rollup_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("catalog plan --bundle buy-pingan-complete-review --view summary", combined)
        self.assertIn("catalog preview --bundle buy-pingan-complete-review --view summary", combined)
        self.assertIn("catalog plan --bundle sell-pingan-complete-review --view summary", combined)
        self.assertIn("catalog preview --bundle sell-pingan-complete-review --view summary", combined)
        self.assertIn("catalog plan --bundle confirm-current-pingan-complete-review --view summary", combined)
        self.assertIn("catalog preview --bundle confirm-current-pingan-complete-review --view summary", combined)
        self.assertIn("trade_plan_boundary_commands", combined)
        self.assertIn("trade-buy", combined)
        self.assertIn("trade-sell", combined)
        self.assertIn("confirm-current", combined)
        self.assertIn("不执行 task/trade/report/bundle step", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("交易安全审批", combined)

    def test_pingan_bundle_slice_presence_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("catalog plan --bundle buy-pingan-complete-review --from-step success --view summary", combined)
        self.assertIn("catalog preview --bundle buy-pingan-complete-review --from-step success --view summary", combined)
        self.assertIn("catalog plan --bundle buy-pingan-complete-review --to-step trade --view summary", combined)
        self.assertIn("catalog preview --bundle confirm-current-pingan-complete-review --to-step confirm --view summary", combined)
        self.assertIn("has_trade_plan_boundary", combined)
        self.assertIn("selected steps", combined)
        self.assertIn("不执行 task/trade/report/bundle step", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("交易安全审批", combined)

    def test_pingan_bundle_coverage_status_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("trade_plan_boundary_input_coverage_status_counts", combined)
        self.assertIn("missing_required_inputs", combined)
        self.assertIn("no_required_inputs", combined)
        self.assertIn("selected steps", combined)
        self.assertIn("不执行 task/trade/report/bundle step", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("交易安全审批", combined)

    def test_pingan_bundle_input_kind_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("trade_plan_boundary_input_kind_counts", combined)
        self.assertIn("order", combined)
        self.assertIn("confirmation", combined)
        self.assertIn("catalog preview --bundle confirm-current-pingan-complete-review --view summary", combined)
        self.assertIn("catalog plan --bundle buy-pingan-complete-review --from-step success --view summary", combined)
        self.assertIn("只读", combined)
        self.assertIn("不执行 task/trade/report/bundle step", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("交易安全审批", combined)
        self.assertIn("production readiness", combined)

    def test_pingan_live_manual_acceptance_evidence_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-live-manual-acceptance-evidence", combined)
                self.assertIn("live_manual_acceptance_complete", combined)
                self.assertIn("acceptance_complete", combined)
                self.assertIn("read-only report evidence", combined)
                self.assertIn("不执行 trades/workflows", combined)
                self.assertIn("不证明 broker production readiness", combined)
                self.assertIn("不证明 UI login readiness", combined)
                self.assertIn("不证明 implemented status", combined)

    def test_pingan_readiness_manifest_sample_registry_evidence_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-promotion-readiness-manifest-sample-registry", combined)
                self.assertIn("runtime/pingan/promotion-readiness-manifest.example.json", combined)
                self.assertIn("plan-pingan-promotion-readiness", combined)
                self.assertIn("task run --preset plan-pingan-promotion-readiness", combined)
                self.assertIn("catalog plan --entry plan-pingan-promotion-readiness", combined)
                self.assertIn("只读 discovery/registration", combined)
                self.assertIn("不执行 broker/desktop/trade/report/task/bundle workflow", combined)
                self.assertIn("不刷新 source evidence", combined)
                self.assertIn("不证明 production readiness", combined)
                self.assertIn("不证明 implemented status", combined)

    def test_submit_once_task_plan_preview_boundary_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["D-08"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("catalog plan --entry task-buy-submit-once --view summary", combined)
        self.assertIn("catalog preview --entry task-buy-submit-once --view summary", combined)
        self.assertIn("catalog plan --entry task-sell-submit-once --view summary", combined)
        self.assertIn("catalog preview --entry task-sell-submit-once --view summary", combined)
        self.assertIn("trade-submit-once", combined)
        self.assertIn("non_executing_catalog_plan", combined)
        self.assertIn("不执行 task/trade/report/bundle step", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("交易安全审批", combined)
        self.assertIn("桌面执行原语", combined)

    def test_submit_once_bundle_boundary_rollup_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["D-08"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("catalog plan --bundle buy-submit-once-pingan-complete-review --view summary", combined)
        self.assertIn("catalog preview --bundle buy-submit-once-pingan-complete-review --view summary", combined)
        self.assertIn("catalog plan --bundle sell-submit-once-pingan-complete-review --view summary", combined)
        self.assertIn("catalog preview --bundle sell-submit-once-pingan-complete-review --view summary", combined)
        self.assertIn("trade_plan_boundary_step_count", combined)
        self.assertIn("trade_plan_boundary_sides", combined)
        self.assertIn("不执行 task/trade/report/bundle step", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("交易安全审批", combined)
        self.assertIn("桌面执行原语", combined)

    def test_submit_once_bundle_coverage_status_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["D-08"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("trade_plan_boundary_input_coverage_status_counts", combined)
        self.assertIn("missing_required_inputs", combined)
        self.assertIn("has_trade_plan_boundary", combined)
        self.assertIn(
            "catalog plan --bundle buy-submit-once-pingan-complete-review --from-step success --view summary",
            combined,
        )
        self.assertIn("不执行 task/trade/report/bundle step", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("交易安全审批", combined)
        self.assertIn("桌面执行原语", combined)

    def test_submit_once_bundle_input_kind_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["D-08"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("trade_plan_boundary_input_kind_counts", combined)
        self.assertIn("submit_once_order", combined)
        self.assertIn("catalog preview --bundle sell-submit-once-pingan-complete-review --view summary", combined)
        self.assertIn(
            "catalog plan --bundle buy-submit-once-pingan-complete-review --from-step success --view summary",
            combined,
        )
        self.assertIn("只读", combined)
        self.assertIn("不执行 task/trade/report/bundle step", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("交易安全审批", combined)
        self.assertIn("production readiness", combined)
        self.assertIn("桌面执行原语", combined)

    def test_pingan_submit_once_broker_readiness_guard_is_registered_without_status_change(self) -> None:
        row = _current_function_tree_rows()["D-08"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("pingan-submit-once-broker-readiness-guard", combined)
        self.assertIn("trade submit-once --require-broker-readiness", combined)
        self.assertIn("task trade-submit-once --require-broker-readiness", combined)
        self.assertIn("TdxTradeManager.pingan.buy_submit_once/sell_submit_once", combined)
        self.assertIn("submit-once 只做 broker runtime health guard 校验", combined)
        self.assertIn("不 start/stop/restart/kill/supervise/backoff", combined)
        self.assertIn("不 retry/backoff/recovery", combined)
        self.assertIn("production trading readiness", combined)

    def test_pingan_trading_implemented_promotion_plan_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-trading-implemented-promotion-plan", combined)
                self.assertIn("provider/broker ownership", combined)
                self.assertIn("safety gates", combined)
                self.assertIn("desktop lifecycle", combined)
                self.assertIn("audit evidence", combined)
                self.assertIn("acceptance gates", combined)
                self.assertIn("只读 catalog", combined)
                self.assertIn("broker readiness", combined)
                self.assertIn("交易安全审批", combined)
                self.assertIn("production readiness", combined)

    def test_pingan_preflight_owner_lock_status_gate_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-preflight-owner-lock-status-gate", combined)
                self.assertIn("promotion_gate_status.lifecycle_owner_lock_status", combined)
                self.assertIn("owner_pid_status/owner_pid_alive", combined)
                self.assertIn("pid_ownership_claimed=false", combined)
                self.assertIn("side_effect_level=none", combined)
                self.assertIn("不 acquire/release owner lock", combined)
                self.assertIn("不写 lifecycle statefile/lock", combined)
                self.assertIn("broker readiness", combined)
                self.assertIn("live/manual acceptance", combined)

    def test_pingan_preflight_owner_lock_required_gate_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-preflight-owner-lock-required-gate", combined)
                self.assertIn("trade preflight --require-lifecycle-owner-lock", combined)
                self.assertIn("lifecycle_owner_lock_status.required=true", combined)
                self.assertIn("owner_token_matches", combined)
                self.assertIn("requirement_status", combined)
                self.assertIn("failed-style", combined)
                self.assertIn("不 acquire/release owner lock", combined)
                self.assertIn("不写 lifecycle statefile/lock", combined)
                self.assertIn("broker readiness", combined)
                self.assertIn("live/manual acceptance", combined)

    def test_pingan_execution_owner_lock_required_guard_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-execution-owner-lock-required-guard", combined)
                self.assertIn("trade buy/sell/submit-once --require-lifecycle-owner-lock", combined)
                self.assertIn("require_lifecycle_owner_lock=true", combined)
                self.assertIn("trade_safety.risk_gate.lifecycle_owner_lock_required_status", combined)
                self.assertIn("owner_token_matches", combined)
                self.assertIn("requirement_status", combined)
                self.assertIn("桌面自动化", combined)
                self.assertIn("不 acquire/release owner lock", combined)
                self.assertIn("不写 lifecycle statefile/lock", combined)
                self.assertIn("不 start/stop/restart/kill/supervise/backoff", combined)
                self.assertIn("broker readiness", combined)
                self.assertIn("live/manual acceptance", combined)

    def test_pingan_task_execution_owner_lock_required_guard_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-task-execution-owner-lock-required-guard", combined)
                self.assertIn("task trade-buy/trade-sell/trade-submit-once --require-lifecycle-owner-lock", combined)
                self.assertIn("TdxTaskManager.trade_buy/trade_sell/trade_submit_once", combined)
                self.assertIn("task layer 只转发", combined)
                self.assertIn("不 acquire/release owner lock", combined)
                self.assertIn("不直接写 lifecycle statefile/lock", combined)
                self.assertIn("不 start/stop/restart/kill/supervise/backoff", combined)
                self.assertIn("broker readiness", combined)
                self.assertIn("live/manual acceptance", combined)

    def test_pingan_task_run_owner_lock_guard_overrides_are_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-task-run-owner-lock-guard-overrides", combined)
                self.assertIn("task run --preset", combined)
                self.assertIn("lifecycle owner-lock preset/CLI override", combined)
                self.assertIn("task-run layer 只解析/合并/转发", combined)
                self.assertIn("不 acquire/release owner lock", combined)
                self.assertIn("不直接写 lifecycle statefile/lock", combined)
                self.assertIn("不 start/stop/restart/kill/supervise/backoff", combined)
                self.assertIn("broker readiness", combined)
                self.assertIn("live/manual acceptance", combined)

    def test_pingan_guarded_trade_owner_lock_guard_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()
        row = rows["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("pingan-guarded-trade-owner-lock-guard", combined)
        self.assertIn("task guarded-trade-buy --require-lifecycle-owner-lock", combined)
        self.assertIn("guarded_trade_buy", combined)
        self.assertIn("guarded workflow 只转发", combined)
        self.assertIn("不 acquire/release owner lock", combined)
        self.assertIn("不直接写 lifecycle statefile/lock", combined)
        self.assertIn("不 start/stop/restart/kill/supervise/backoff", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("live/manual acceptance", combined)

    def test_pingan_confirm_current_owner_lock_guard_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()
        row = rows["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("pingan-confirm-current-owner-lock-guard", combined)
        self.assertIn("trade confirm-current --require-lifecycle-owner-lock", combined)
        self.assertIn("task trade-confirm-current --require-lifecycle-owner-lock", combined)
        self.assertIn("TdxTradeManager.pingan.confirm_current", combined)
        self.assertIn("confirm-current 只做 owner-lock guard 校验", combined)
        self.assertIn("不 acquire/release owner lock", combined)
        self.assertIn("不 start/stop/restart/kill/supervise/backoff", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("live/manual acceptance", combined)

    def test_pingan_submit_ready_owner_lock_guard_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()
        row = rows["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("pingan-submit-ready-owner-lock-guard", combined)
        self.assertIn("trade submit-ready --require-lifecycle-owner-lock", combined)
        self.assertIn("task trade-submit-ready --require-lifecycle-owner-lock", combined)
        self.assertIn("TdxTradeManager.pingan.submit_ready", combined)
        self.assertIn("submit-ready 只做 owner-lock guard 校验", combined)
        self.assertIn("不 acquire/release owner lock", combined)
        self.assertIn("不 start/stop/restart/kill/supervise/backoff", combined)
        self.assertIn("broker readiness", combined)
        self.assertIn("live/manual acceptance", combined)

    def test_pingan_exception_popup_manual_close_control_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-exception-popup-manual-close-control", combined)
                self.assertIn("TdxTradeManager.pingan.exception_popup", combined)
                self.assertIn("trade exception-popup --action inspect", combined)
                self.assertIn("trade exception-popup --action close --confirm-close", combined)
                self.assertIn("只做 exception popup inspect/close", combined)
                self.assertIn("不 retry/recover/resubmit", combined)
                self.assertIn("broker readiness", combined)
                self.assertIn("live/manual acceptance", combined)
                self.assertIn("workflow/lifecycle governance", combined)

    def test_pingan_confirm_current_broker_readiness_guard_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()
        row = rows["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("pingan-confirm-current-broker-readiness-guard", combined)
        self.assertIn("trade confirm-current --require-broker-readiness", combined)
        self.assertIn("task trade-confirm-current --require-broker-readiness", combined)
        self.assertIn("TdxTradeManager.pingan.confirm_current", combined)
        self.assertIn("confirm-current 只做 broker runtime health guard 校验", combined)
        self.assertIn("不 start/stop/restart/kill/supervise/backoff", combined)
        self.assertIn("不 retry/backoff/recovery", combined)
        self.assertIn("live/manual acceptance", combined)

    def test_pingan_buy_sell_broker_readiness_guard_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()
        row = rows["D-07"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("pingan-buy-sell-broker-readiness-guard", combined)
        self.assertIn("trade buy --require-broker-readiness", combined)
        self.assertIn("trade sell --require-broker-readiness", combined)
        self.assertIn("task trade-buy --require-broker-readiness", combined)
        self.assertIn("task trade-sell --require-broker-readiness", combined)
        self.assertIn("TdxTradeManager.pingan.buy/sell", combined)
        self.assertIn("buy/sell 只做 broker runtime health guard 校验", combined)
        self.assertIn("不 start/stop/restart/kill/supervise/backoff", combined)
        self.assertIn("不 retry/backoff/recovery", combined)
        self.assertIn("production trading readiness", combined)

    def test_pingan_lifecycle_supervisor_control_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-lifecycle-supervisor-control", combined)
                self.assertIn("TdxTradeManager.pingan.lifecycle_supervisor_tick", combined)
                self.assertIn("TdxTradeManager.pingan.lifecycle_supervisor_run", combined)
                self.assertIn("trade lifecycle-supervisor-tick", combined)
                self.assertIn("trade lifecycle-supervisor-run", combined)
                self.assertIn("restart/backoff", combined)
                self.assertIn("statefile-backed lifecycle control", combined)
                self.assertIn("不提交订单", combined)
                self.assertIn("不执行 catalog/task/report/bundle workflow", combined)
                self.assertIn("不 own/kill/start 真实 PingAn 进程", combined)
                self.assertIn("production trading readiness", combined)

    def test_pingan_process_lifecycle_control_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-process-lifecycle-control", combined)
                self.assertIn("TdxTradeManager.pingan.lifecycle_process", combined)
                self.assertIn("trade lifecycle-process", combined)
                self.assertIn("owner-locked local process start/stop/restart", combined)
                self.assertIn("recorded PID", combined)
                self.assertIn("不提交订单", combined)
                self.assertIn("不执行 catalog/task/report/bundle workflow", combined)
                self.assertIn("不证明 broker readiness", combined)
                self.assertIn("不证明 UI login readiness", combined)
                self.assertIn("production trading readiness", combined)

    def test_pingan_supervisor_process_restart_control_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-supervisor-process-restart-control", combined)
                self.assertIn("process_restart_enabled", combined)
                self.assertIn("trade lifecycle-supervisor-tick --process-restart", combined)
                self.assertIn("trade lifecycle-supervisor-run --process-restart", combined)
                self.assertIn("recorded-PID lifecycle process guard", combined)
                self.assertIn("显式 opt-in", combined)
                self.assertIn("不提交订单", combined)
                self.assertIn("不执行 catalog/task/report/bundle workflow", combined)
                self.assertIn("不证明 broker readiness", combined)
                self.assertIn("不证明 UI login readiness", combined)
                self.assertIn("production trading readiness", combined)

    def test_pingan_supervisor_restart_readiness_summary_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-supervisor-restart-readiness-summary", combined)
                self.assertIn("process_restart_recheck_enabled", combined)
                self.assertIn("lifecycle_recovery_status", combined)
                self.assertIn("post-restart broker health recheck", combined)
                self.assertIn("immediate lifecycle evidence", combined)
                self.assertIn("不证明 order readiness", combined)
                self.assertIn("不证明 broker production readiness", combined)
                self.assertIn("不证明 UI login readiness", combined)
                self.assertIn("live/manual acceptance", combined)

    def test_pingan_promotion_readiness_rollup_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-promotion-readiness-rollup", combined)
                self.assertIn("promotion_readiness_rollup", combined)
                self.assertIn("completed_gates", combined)
                self.assertIn("incomplete_gates", combined)
                self.assertIn("read-only evidence aggregation", combined)
                self.assertIn("不执行 broker/desktop/trade/report/catalog workflow", combined)
                self.assertIn("不证明 production readiness", combined)
                self.assertIn("不证明 implemented status", combined)

    def test_pingan_implemented_status_promotion_decision_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-implemented-status-promotion-decision", combined)
                self.assertIn("implemented_status_promotion_decision", combined)
                self.assertIn("eligible_for_review", combined)
                self.assertIn("blocked_reasons", combined)
                self.assertIn("read-only fail-closed", combined)
                self.assertIn("不执行 PingAn workflow", combined)
                self.assertIn("不自动修改 FUNCTION_TREE status", combined)
                self.assertIn("不证明 production readiness", combined)
                self.assertIn("不证明 implemented status", combined)

    def test_pingan_evidence_provenance_gate_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-evidence-provenance-promotion-gate", combined)
                self.assertIn("evidence_contract_status", combined)
                self.assertIn("unverified_evidence_contract", combined)
                self.assertIn("schema-contract", combined)
                self.assertIn("只读 schema-contract validation", combined)
                self.assertIn("不执行 PingAn workflow", combined)
                self.assertIn("不证明 production readiness", combined)
                self.assertIn("不证明 implemented status", combined)

    def test_pingan_artifact_provenance_gate_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-artifact-provenance-promotion-gate", combined)
                self.assertIn("artifact_provenance_status", combined)
                self.assertIn("unverified_artifact_provenance", combined)
                self.assertIn("artifact provenance", combined)
                self.assertIn("只读 artifact provenance validation", combined)
                self.assertIn("不执行 PingAn workflow", combined)
                self.assertIn("不证明 production readiness", combined)
                self.assertIn("不证明 implemented status", combined)

    def test_pingan_promotion_readiness_freshness_gate_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-promotion-readiness-freshness-gate", combined)
                self.assertIn("max_evidence_age_seconds", combined)
                self.assertIn("evidence_freshness_status", combined)
                self.assertIn("stale_evidence_kinds", combined)
                self.assertIn("stale evidence", combined)
                self.assertIn("过期 evidence 不能计入 complete gate", combined)
                self.assertIn("不执行 broker/desktop/trade/report/catalog workflow", combined)
                self.assertIn("不证明 production readiness", combined)
                self.assertIn("不证明 implemented status", combined)

    def test_pingan_promotion_readiness_artifact_output_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-promotion-readiness-artifact-output", combined)
                self.assertIn("json_output_path", combined)
                self.assertIn("promotion_readiness_rollup_artifact", combined)
                self.assertIn("readonly artifact write", combined)
                self.assertIn("不刷新 source evidence", combined)
                self.assertIn("不执行 broker/desktop/trade/report/catalog workflow", combined)
                self.assertIn("不证明 production readiness", combined)
                self.assertIn("不证明 implemented status", combined)

    def test_pingan_promotion_readiness_manifest_input_is_registered_without_status_change(self) -> None:
        rows = _current_function_tree_rows()

        for node_id in ("D-07", "D-08"):
            with self.subTest(node_id=node_id):
                row = rows[node_id]
                combined = f"{row['evidence']} {row['boundary']}"
                self.assertEqual(row["status"], "`[部分实现]`")
                self.assertIn("pingan-promotion-readiness-manifest-input", combined)
                self.assertIn("evidence_manifest_path", combined)
                self.assertIn("evidence_manifest", combined)
                self.assertIn("expected_gates", combined)
                self.assertIn("missing_expected_gates", combined)
                self.assertIn("read-only evidence selection", combined)
                self.assertIn("不刷新 source evidence", combined)
                self.assertIn("不执行 broker/desktop/trade/report/catalog workflow", combined)
                self.assertIn("不证明 production readiness", combined)
                self.assertIn("不证明 implemented status", combined)

    def test_task_report_bundle_source_label_evidence_is_registered(self) -> None:
        row = _current_function_tree_rows()["E-11"]
        combined = f"{row['evidence']} {row['boundary']}"

        self.assertEqual(row["status"], "`[部分实现]`")
        self.assertIn("catalog validate --kind bundle --label followup --view summary", combined)
        self.assertIn("bundle_step_source_label_counts", combined)
        self.assertIn("task_report_bundle_step_source_label_counts", combined)
        self.assertIn("task:followup", combined)
        self.assertIn("report:followup", combined)
        self.assertIn("只读", combined)
        self.assertIn("不执行 task/report/trade/bundle step", combined)
        self.assertIn("不是任意 workflow builder", combined)
        self.assertIn("production readiness", combined)

    def test_validator_json_report_returns_errors_without_stderr(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` |  | implemented boundary |
                """,
            )

            result = _run_validator(root, "--json")

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["valid"], False)
        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["problem_count"], 1)
        self.assertIn("A-01", payload["errors"][0])
        self.assertEqual(result.stderr, "")

    def test_validator_rejects_missing_evidence_or_boundary(self) -> None:
        cases = {
            "missing evidence": "| A-01 | sample | `[已实现]` |  | implemented boundary |",
            "missing boundary": "| A-01 | sample | `[已实现]` | source.py |  |",
        }
        for name, row in cases.items():
            with self.subTest(name=name), TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                _write_function_tree(
                    root,
                    f"""
                    | ID | 功能 | 状态 | 证据 | 边界 |
                    | --- | --- | --- | --- | --- |
                    {row}
                    """,
                )

                result = _run_validator(root)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("A-01", result.stderr)

    def test_validator_rejects_duplicate_ids_bad_status_and_unsafe_pending_rows(self) -> None:
        cases = {
            "duplicate id": """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | source.py | implemented boundary |
                | A-01 | sample again | `[部分实现]` | tests.py | partial boundary |
            """,
            "bad status": """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[完成]` | source.py | implemented boundary |
            """,
            "unsafe pending row": """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已设计/待实现]` | design.md | ready for users |
            """,
        }
        for name, body in cases.items():
            with self.subTest(name=name), TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                _write_function_tree(root, body)

                result = _run_validator(root)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("A-01", result.stderr)

    def test_validator_rejects_competing_root_roadmap(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | source.py | implemented boundary |
                """,
            )
            (root / "ROADMAP.md").write_text("competing roadmap\n", encoding="utf-8")

            result = _run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ROADMAP.md", result.stderr)

    def test_validator_accepts_archived_and_active_openspec_evidence(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | archived | `[已实现]` | source.py；OpenSpec `archived-change` | implemented boundary |
                | A-02 | active | `[部分实现]` | tests.py；OpenSpec `active-change` | partial boundary |
                """,
            )
            _write_openspec_change(root, "archived-change", archived=True)
            _write_openspec_change(root, "active-change", archived=False)

            result = _run_validator(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("rows=2", result.stdout)

    def test_validator_rejects_missing_openspec_evidence(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | source.py；OpenSpec `missing-change` | implemented boundary |
                """,
            )

            result = _run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("A-01", result.stderr)
            self.assertIn("missing-change", result.stderr)

    def test_validator_accepts_existing_local_evidence_paths(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "tests").mkdir()
            (root / "scripts").mkdir()
            (root / "tests" / "test_registry.py").write_text("def test_ok():\n    pass\n", encoding="utf-8")
            (root / "scripts" / "validate_registry.py").write_text("print('ok')\n", encoding="utf-8")
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | `tests/test_registry.py`；`scripts/validate_registry.py` | implemented boundary |
                """,
            )

            result = _run_validator(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("rows=1", result.stdout)

    def test_validator_rejects_missing_local_evidence_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | `tests/missing_registry_test.py` | implemented boundary |
                """,
            )

            result = _run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("A-01", result.stderr)
            self.assertIn("tests/missing_registry_test.py", result.stderr)

    def test_validator_ignores_non_literal_evidence_paths(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_function_tree(
                root,
                """
                | ID | 功能 | 状态 | 证据 | 边界 |
                | --- | --- | --- | --- | --- |
                | A-01 | sample | `[已实现]` | `build_subscription_watch_status_summary()`；`catalog validate --kind all`；`runtime/trade-audits/*`；`runtime/watchlist-imports/zxg-watchlist-import.example.json/csv/txt` | implemented boundary |
                """,
            )

            result = _run_validator(root)

            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
