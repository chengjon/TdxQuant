import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from tdxquant.block_sync import sync_watchlist_to_block
from tdxquant.models import ErrorCode, Result


class BlockSyncTests(unittest.TestCase):
    def test_dry_run_replace_plans_create_and_member_diff_without_runtime_writes(self) -> None:
        create_block = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="created", data={}))
        sync_members = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="synced", data={}))
        with TemporaryDirectory() as temp_dir:
            result = sync_watchlist_to_block(
                block_code="LZXG",
                symbols=["600519.SH", "000001.SZ", "600519.SH"],
                mode="replace",
                create_if_missing=True,
                dry_run=True,
                show=True,
                observed_state=lambda: {"block_code": "LZXG", "exists": False},
                create_block=create_block,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.code, ErrorCode.OK)
            self.assertEqual(result.data["sync"]["block_code"], "LZXG")
            self.assertEqual(result.data["sync"]["mode"], "replace")
            self.assertTrue(result.data["sync"]["dry_run"])
            self.assertFalse(result.data["sync"]["created_block"])
            self.assertTrue(result.data["sync"]["would_create_block"])
            self.assertEqual(result.data["sync"]["added_symbols"], ["000001.SZ", "600519.SH"])
            self.assertEqual(result.data["sync"]["removed_symbols"], [])
            self.assertEqual(result.data["sync"]["desired_symbols"], ["000001.SZ", "600519.SH"])
            self.assertEqual(result.data["sync"]["observed_symbols"], [])
            self.assertEqual(result.data["sync"]["governance_decision"], "execute")
            self.assertIn("audit_log_path", result.data["artifacts"])
            self.assertTrue(Path(result.data["artifacts"]["audit_log_path"]).exists())
            create_block.assert_not_called()
            sync_members.assert_not_called()

    def test_merge_returns_noop_when_requested_symbols_are_already_present(self) -> None:
        create_block = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="created", data={}))
        sync_members = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="synced", data={}))
        with TemporaryDirectory() as temp_dir:
            result = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["600519.SH", "000001.SZ"],
                mode="merge",
                create_if_missing=False,
                dry_run=False,
                show=False,
                observed_state=lambda: {
                    "block_code": "ZXG",
                    "exists": True,
                    "block_name": "自选股",
                    "stocks": ["000001.SZ", "600519.SH"],
                },
                create_block=create_block,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.data["sync"]["status"], "noop")
            self.assertEqual(result.data["sync"]["governance_decision"], "skip")
            self.assertEqual(result.data["sync"]["governance_reason"], "already_applied")
            self.assertEqual(result.data["sync"]["added_symbols"], [])
            self.assertEqual(result.data["sync"]["removed_symbols"], [])
            self.assertEqual(result.data["sync"]["unchanged_symbols"], ["000001.SZ", "600519.SH"])
            create_block.assert_not_called()
            sync_members.assert_not_called()

    def test_reuses_mutation_key_for_same_sync_request_without_runtime_writes(self) -> None:
        create_block = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="created", data={}))
        sync_members = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="synced", data={}))
        with TemporaryDirectory() as temp_dir:
            first = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["000001.SZ"],
                mode="replace",
                create_if_missing=False,
                dry_run=True,
                show=True,
                mutation_key="sync-001",
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": []},
                create_block=create_block,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )
            second = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["000001.SZ"],
                mode="replace",
                create_if_missing=False,
                dry_run=True,
                show=True,
                mutation_key="sync-001",
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": []},
                create_block=create_block,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertTrue(first.ok)
            self.assertTrue(second.ok)
            self.assertEqual(second.data["sync"]["status"], "noop")
            self.assertEqual(second.data["sync"]["governance_reason"], "mutation_key_replay")
            create_block.assert_not_called()
            sync_members.assert_not_called()

    def test_preserves_underlying_block_mutation_metadata_for_live_sync(self) -> None:
        sync_members = Mock(
            return_value=Result(
                ok=True,
                code=ErrorCode.OK,
                message="synced",
                data={
                    "block_mutation": {
                        "operation": "send_user_block",
                        "status": "applied",
                        "governance_decision": "execute",
                    }
                },
            )
        )
        with TemporaryDirectory() as temp_dir:
            result = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["000001.SZ"],
                mode="replace",
                create_if_missing=False,
                dry_run=False,
                show=True,
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": []},
                create_block=None,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.data["sync"]["status"], "applied")
            self.assertEqual(result.data["block_mutation"]["operation"], "send_user_block")
            self.assertEqual(result.data["block_mutation"]["status"], "applied")
            self.assertNotIn("block_mutation_stages", result.data)

    def test_preserves_multiple_block_mutation_stages_when_create_then_sync_executes(self) -> None:
        create_block = Mock(
            return_value=Result(
                ok=True,
                code=ErrorCode.OK,
                message="created",
                data={"block_mutation": {"operation": "create_sector", "status": "applied"}},
            )
        )
        sync_members = Mock(
            return_value=Result(
                ok=True,
                code=ErrorCode.OK,
                message="synced",
                data={"block_mutation": {"operation": "send_user_block", "status": "applied"}},
            )
        )
        with TemporaryDirectory() as temp_dir:
            result = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["000001.SZ"],
                mode="replace",
                create_if_missing=True,
                dry_run=False,
                show=True,
                observed_state=lambda: {"block_code": "ZXG", "exists": False, "stocks": []},
                create_block=create_block,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertTrue(result.ok)
            self.assertTrue(result.data["sync"]["created_block"])
            self.assertEqual(result.data["block_mutation"]["operation"], "send_user_block")
            self.assertEqual(
                [item["operation"] for item in result.data["block_mutation_stages"]],
                ["create_sector", "send_user_block"],
            )

    def test_rejects_empty_symbol_input_before_any_runtime_write(self) -> None:
        create_block = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="created", data={}))
        sync_members = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="synced", data={}))
        with TemporaryDirectory() as temp_dir:
            result = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=[],
                mode="replace",
                create_if_missing=False,
                dry_run=False,
                show=True,
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": []},
                create_block=create_block,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
            self.assertEqual(result.data["sync"]["governance_reason"], "empty_symbols")
            create_block.assert_not_called()
            sync_members.assert_not_called()

    def test_returns_stable_failure_when_state_probe_fails(self) -> None:
        create_block = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="created", data={}))
        sync_members = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="synced", data={}))
        probe_failure = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="probe failed",
            data={},
            next_action="repair runtime",
        )
        with TemporaryDirectory() as temp_dir:
            result = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["000001.SZ"],
                mode="replace",
                create_if_missing=False,
                dry_run=False,
                show=True,
                observed_state=lambda: probe_failure,
                create_block=create_block,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, ErrorCode.EXECUTION_FAILED)
            self.assertEqual(result.data["sync"]["governance_reason"], "state_probe_failed")
            self.assertEqual(result.next_action, "repair runtime")
            create_block.assert_not_called()
            sync_members.assert_not_called()

    def test_returns_failed_result_when_create_succeeds_but_sync_members_fails(self) -> None:
        create_block = Mock(
            return_value=Result(
                ok=True,
                code=ErrorCode.OK,
                message="created",
                data={"block_mutation": {"operation": "create_sector", "status": "applied"}},
            )
        )
        sync_members = Mock(
            return_value=Result(
                ok=False,
                code=ErrorCode.EXECUTION_FAILED,
                message="send failed",
                data={"block_mutation": {"operation": "send_user_block", "status": "failed"}},
                next_action="retry later",
            )
        )
        with TemporaryDirectory() as temp_dir:
            result = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["000001.SZ"],
                mode="replace",
                create_if_missing=True,
                dry_run=False,
                show=True,
                observed_state=lambda: {"block_code": "ZXG", "exists": False, "stocks": []},
                create_block=create_block,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, ErrorCode.EXECUTION_FAILED)
            self.assertEqual(result.data["sync"]["status"], "failed")
            self.assertEqual(result.data["sync"]["governance_decision"], "execute")
            self.assertEqual(result.data["sync"]["governance_reason"], "missing_block")
            self.assertEqual(result.data["block_mutation"]["operation"], "send_user_block")
            self.assertEqual(
                [item["operation"] for item in result.data["block_mutation_stages"]],
                ["create_sector", "send_user_block"],
            )
            self.assertEqual(result.next_action, "retry later")

    def test_write_policy_merge_dry_run_maps_to_merge_plan_without_runtime_writes(self) -> None:
        create_block = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="created", data={}))
        sync_members = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="synced", data={}))
        with TemporaryDirectory() as temp_dir:
            result = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["600519.SH"],
                write_policy="merge_dry_run",
                create_if_missing=False,
                show=True,
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": ["000001.SZ"]},
                create_block=create_block,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.data["sync"]["write_policy"], "merge_dry_run")
            self.assertEqual(result.data["sync"]["mode"], "merge")
            self.assertTrue(result.data["sync"]["dry_run"])
            self.assertEqual(result.data["sync"]["desired_symbols"], ["000001.SZ", "600519.SH"])
            create_block.assert_not_called()
            sync_members.assert_not_called()

    def test_write_policy_rejects_conflicting_explicit_mode(self) -> None:
        sync_members = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="synced", data={}))
        with TemporaryDirectory() as temp_dir:
            result = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["600519.SH"],
                mode="replace",
                write_policy="merge",
                create_if_missing=False,
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": []},
                create_block=None,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
            self.assertEqual(result.data["sync"]["governance_reason"], "invalid_write_policy")
            self.assertEqual(result.data["sync"]["write_policy"], "merge")
            self.assertEqual(result.data["sync"]["mode"], "merge")
            sync_members.assert_not_called()

    def test_mutation_key_replay_includes_machine_readable_replay_metadata(self) -> None:
        sync_members = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="synced", data={}))
        with TemporaryDirectory() as temp_dir:
            first = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["000001.SZ"],
                write_policy="replace_dry_run",
                create_if_missing=False,
                mutation_key="sync-002",
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": []},
                create_block=None,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )
            second = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["000001.SZ"],
                write_policy="replace_dry_run",
                create_if_missing=False,
                mutation_key="sync-002",
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": []},
                create_block=None,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertTrue(first.ok)
            self.assertTrue(second.ok)
            replay = second.data["mutation_key_replay"]
            self.assertEqual(replay["mutation_key"], "sync-002")
            self.assertTrue(replay["replayed"])
            self.assertEqual(replay["prior_request"]["write_policy"], "replace_dry_run")
            self.assertEqual(second.data["sync"]["governance_reason"], "mutation_key_replay")

    def test_mutation_key_conflict_includes_prior_and_current_policy_requests(self) -> None:
        sync_members = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="synced", data={}))
        with TemporaryDirectory() as temp_dir:
            sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["000001.SZ"],
                write_policy="replace_dry_run",
                create_if_missing=False,
                mutation_key="sync-003",
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": []},
                create_block=None,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )
            conflict = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["600519.SH"],
                write_policy="merge_dry_run",
                create_if_missing=False,
                mutation_key="sync-003",
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": []},
                create_block=None,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )

            self.assertFalse(conflict.ok)
            self.assertEqual(conflict.data["sync"]["governance_reason"], "mutation_key_conflict")
            metadata = conflict.data["mutation_key_conflict"]
            self.assertEqual(metadata["mutation_key"], "sync-003")
            self.assertEqual(metadata["prior_request"]["write_policy"], "replace_dry_run")
            self.assertEqual(metadata["current_request"]["write_policy"], "merge_dry_run")
            self.assertEqual(metadata["current_request"]["mode"], "merge")

    def test_audit_artifact_includes_write_policy_metadata(self) -> None:
        sync_members = Mock(return_value=Result(ok=True, code=ErrorCode.OK, message="synced", data={}))
        with TemporaryDirectory() as temp_dir:
            result = sync_watchlist_to_block(
                block_code="ZXG",
                symbols=["600519.SH"],
                write_policy="merge_dry_run",
                create_if_missing=False,
                observed_state=lambda: {"block_code": "ZXG", "exists": True, "stocks": ["000001.SZ"]},
                create_block=None,
                sync_members=sync_members,
                audit_dir=temp_dir,
            )
            audit_path = Path(result.data["artifacts"]["audit_log_path"])
            payload = json.loads(audit_path.read_text(encoding="utf-8"))

            self.assertEqual(payload["normalized_request"]["write_policy"], "merge_dry_run")
            self.assertEqual(payload["sync"]["write_policy"], "merge_dry_run")
            self.assertEqual(payload["sync"]["mode"], "merge")
            self.assertTrue(payload["sync"]["dry_run"])
