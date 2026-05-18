import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd

from tdxquant.api.bridge import (
    TdxRuntimeSubscriptionSession,
    run_tdx_clear_sector,
    run_tdx_block_sync,
    run_tdx_create_sector,
    run_tdx_delete_sector,
    run_tdx_data_kline,
    run_tdx_data_snapshot,
    run_tdx_formula_screen,
    run_tdx_provider_capabilities,
    run_tdx_provider_doctor,
    run_tdx_provider_health,
    run_tdx_rename_sector,
    run_tdx_send_user_block,
    run_tdx_stock_list,
    run_tdx_subscription_list,
    run_tdx_subscription_subscribe,
    run_tdx_subscription_unsubscribe,
)
from tdxquant.api.runtime import RuntimeApi
from tdxquant.models import ErrorCode, Result
from tdxquant.tdx_api_bridge import run_tdx_data_sector_list, run_tdx_bridge_health, serialize_value


class TdxApiBridgeSerializationTests(unittest.TestCase):
    def test_serialize_dataframe(self) -> None:
        frame = pd.DataFrame({"close": [10.5, 11.0]}, index=pd.Index(["2025-01-01", "2025-01-02"], name="time"))
        payload = serialize_value(frame)
        self.assertEqual(payload["type"], "dataframe")
        self.assertEqual(payload["index_name"], "time")
        self.assertEqual(len(payload["records"]), 2)
        self.assertEqual(payload["records"][0]["close"], 10.5)

    def test_serialize_series(self) -> None:
        series = pd.Series([1, 2], index=pd.Index(["a", "b"], name="symbol"), name="value")
        payload = serialize_value(series)
        self.assertEqual(payload["type"], "series")
        self.assertEqual(payload["index_name"], "symbol")
        self.assertEqual(payload["records"][1]["value"], 2)


class TdxApiBridgePlatformGuardTests(unittest.TestCase):
    def test_tdx_bridge_health_unsupported_or_ok(self) -> None:
        result = run_tdx_bridge_health(window_key="通达信金融终端")
        self.assertIn(result.code.value, {"unsupported_platform", "ok", "execution_failed"})

    def test_tdx_data_sector_list_unsupported_or_ok(self) -> None:
        result = run_tdx_data_sector_list()
        self.assertIn(result.code.value, {"unsupported_platform", "ok", "execution_failed"})

    def test_provider_capabilities_returns_registry_shape(self) -> None:
        result = run_tdx_provider_capabilities()
        self.assertTrue(result.ok)
        self.assertEqual(result.code.value, "ok")
        self.assertIn("capabilities", result.data)
        self.assertIn("summary", result.data)
        self.assertGreater(result.data["summary"]["total"], 0)
        capability_names = {item["name"] for item in result.data["capabilities"]}
        self.assertIn("formula.screen", capability_names)
        self.assertIn("block.sync_watchlist", capability_names)
        first = result.data["capabilities"][0]
        self.assertIn("name", first)
        self.assertIn("capability_version", first)
        self.assertIn("stability", first)
        self.assertIn("side_effect_level", first)
        self.assertIn("entrypoints", first)

    def test_provider_capabilities_exposes_query_metadata_for_hardened_queries(self) -> None:
        result = run_tdx_provider_capabilities()
        self.assertTrue(result.ok)
        capabilities = {item["name"]: item for item in result.data["capabilities"]}

        snapshot = capabilities["market.snapshot"]
        self.assertEqual(
            snapshot["query_metadata"],
            {
                "query_shapes": [
                    {
                        "query_kind": "market.snapshot",
                        "selectors": ["symbol"],
                        "query_params": [],
                    }
                ],
                "supports_requested_fields": True,
                "supports_empty_results": True,
                "supports_replay": True,
            },
        )

        stock_list = capabilities["meta.stock_list"]
        self.assertEqual(
            stock_list["query_metadata"],
            {
                "query_shapes": [
                    {
                        "query_kind": "meta.stock_list",
                        "selectors": ["market"],
                        "query_params": ["list_type"],
                    }
                ],
                "supports_requested_fields": False,
                "supports_empty_results": True,
                "supports_replay": True,
            },
        )

        kline = capabilities["market.kline"]
        self.assertEqual(
            kline["query_metadata"],
            {
                "query_shapes": [
                    {
                        "query_kind": "market.kline",
                        "selectors": ["symbols", "date_range"],
                        "query_params": ["period", "count", "dividend_type", "fill_data"],
                    }
                ],
                "supports_requested_fields": True,
                "supports_empty_results": True,
                "supports_replay": True,
            },
        )

    def test_run_tdx_data_snapshot_normalizes_raw_result_into_rows_and_query_meta(self) -> None:
        raw = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"result": {"symbol": "688260.SH", "Now": 10.5, "Volume": 1000}},
        )
        with patch("tdxquant.api.bridge._run_tq_call", return_value=raw):
            result = run_tdx_data_snapshot(stock_code="688260.SH", field_list=["Now", "Volume"])

        self.assertTrue(result.ok)
        self.assertEqual(result.data["rows"], [{"symbol": "688260.SH", "Now": 10.5, "Volume": 1000}])
        self.assertEqual(
            result.data["query_meta"],
            {
                "query_kind": "market.snapshot",
                "row_count": 1,
                "requested_fields": ["Now", "Volume"],
                "returned_fields": ["symbol", "Now", "Volume"],
                "symbol": "688260.SH",
                "query_params": {},
            },
        )

    def test_run_tdx_data_kline_normalizes_dataframe_payload(self) -> None:
        raw = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "result": {
                    "type": "dataframe",
                    "index_name": "time",
                    "records": [{"time": "2024-01-02", "close": 10.2}],
                }
            },
        )
        with patch("tdxquant.api.bridge._run_tq_call", return_value=raw):
            result = run_tdx_data_kline(
                stock_list=["688260.SH", "600519.SH"],
                period="1d",
                start_time="20240101",
                end_time="20241231",
                count=10,
                dividend_type="back",
                field_list=["close"],
                fill_data=False,
            )

        self.assertEqual(result.data["rows"], [{"time": "2024-01-02", "close": 10.2}])
        self.assertEqual(result.data["query_meta"]["query_kind"], "market.kline")
        self.assertEqual(result.data["query_meta"]["symbols"], ["688260.SH", "600519.SH"])
        self.assertEqual(result.data["query_meta"]["date_range"], {"start": "20240101", "end": "20241231"})
        self.assertEqual(result.data["query_meta"]["requested_fields"], ["close"])
        self.assertEqual(result.data["query_meta"]["returned_fields"], ["time", "close"])
        self.assertEqual(
            result.data["query_meta"]["query_params"],
            {"period": "1d", "count": 10, "dividend_type": "back", "fill_data": False},
        )

    def test_run_tdx_stock_list_normalizes_query_params_and_empty_rows(self) -> None:
        raw = Result(ok=True, code=ErrorCode.OK, message="ok", data={"result": []})
        with patch("tdxquant.api.bridge._run_tq_call", return_value=raw):
            result = run_tdx_stock_list(market="16", list_type=1)

        self.assertEqual(result.data["rows"], [])
        self.assertEqual(
            result.data["query_meta"],
            {
                "query_kind": "meta.stock_list",
                "row_count": 0,
                "requested_fields": [],
                "returned_fields": [],
                "market": "16",
                "query_params": {"list_type": 1},
            },
        )

    def test_provider_health_returns_structured_diagnostic_payload(self) -> None:
        result = run_tdx_provider_health(window_key="通达信金融终端")
        self.assertTrue(result.ok)
        self.assertEqual(result.code.value, "ok")
        self.assertIn(result.data["overall_status"], {"ok", "degraded", "unavailable"})
        self.assertIn("checks", result.data)
        self.assertIn("platform", result.data["checks"])
        self.assertIn("query_runtime", result.data["checks"])
        self.assertIn("subscription_runtime", result.data["checks"])
        self.assertIn("desktop_window", result.data["checks"])
        self.assertIn("hid", result.data["checks"])

    def test_provider_doctor_returns_findings_and_actions(self) -> None:
        result = run_tdx_provider_doctor(window_key="通达信金融终端")
        self.assertTrue(result.ok)
        self.assertEqual(result.code.value, "ok")
        self.assertIn(result.data["overall_status"], {"ok", "degraded", "unavailable"})
        self.assertIn("findings", result.data)
        self.assertIn("recommended_actions", result.data)
        self.assertIsInstance(result.data["findings"], list)
        self.assertIsInstance(result.data["recommended_actions"], list)

    def test_formula_screen_normalizes_batch_formula_result(self) -> None:
        raw_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={
                "result": {
                    "000001.SZ": {
                        "UP3": [
                            {"Date": "20260203", "Value": "0"},
                            {"Date": "20260204", "Value": "1"},
                        ]
                    },
                    "600519.SH": {
                        "UP3": [
                            {"Date": "20260203", "Value": "0"},
                        ]
                    },
                }
            },
        )
        with patch("tdxquant.api.bridge.run_tdx_formula_process_mul_xg", return_value=raw_result) as mocked:
            result = run_tdx_formula_screen(
                formula_name="UPN",
                stock_list=["000001.SZ", "600519.SH"],
                formula_arg="3",
                return_count=2,
                return_date=True,
                stock_period="1d",
                start_time="",
                end_time="",
                count=5,
                dividend_type=1,
                strategy_path="strategy.py",
            )
        mocked.assert_called_once_with(
            formula_name="UPN",
            formula_arg="3",
            return_count=2,
            return_date=True,
            stock_list=["000001.SZ", "600519.SH"],
            stock_period="1d",
            start_time="",
            end_time="",
            count=5,
            dividend_type=1,
            strategy_path="strategy.py",
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.data["matched_symbols"], ["000001.SZ"])
        self.assertEqual(result.data["unmatched_symbols"], ["600519.SH"])
        self.assertEqual(result.data["summary"]["matched_symbol_count"], 1)
        self.assertEqual(result.data["rows"][0]["symbol"], "000001.SZ")
        self.assertTrue(result.data["rows"][0]["matched"])
        self.assertEqual(result.data["rows"][0]["matched_dates"], ["20260204"])

    def test_block_mutation_wrapper_writes_audit_artifact_on_success(self) -> None:
        raw_result = Result(ok=True, code=ErrorCode.OK, message="created", data={"runtime": "ok"})
        with (
            TemporaryDirectory() as temp_dir,
            patch("tdxquant.api.bridge._run_tq_call", return_value=raw_result) as mocked,
            patch("tdxquant.api.bridge._probe_custom_sector_state", return_value={"block_code": "CSBK", "exists": False}),
        ):
            result = run_tdx_create_sector(
                block_code="CSBK",
                block_name="测试板块",
                mutation_key="mk-001",
                audit_dir=temp_dir,
                strategy_path="strategy.py",
            )

            mocked.assert_called_once()
            summary = result.data["block_mutation"]
            audit_log_path = Path(result.data["artifacts"]["audit_log_path"])
            self.assertEqual(summary["operation"], "create_sector")
            self.assertEqual(summary["status"], "applied")
            self.assertEqual(summary["mutation_key"], "mk-001")
            self.assertEqual(summary["block_code"], "CSBK")
            self.assertEqual(summary["block_name"], "测试板块")
            self.assertTrue(audit_log_path.exists())
            audit_payload = json.loads(audit_log_path.read_text(encoding="utf-8"))
            self.assertEqual(audit_payload["operation"], "create_sector")
            self.assertEqual(audit_payload["status"], "applied")
            self.assertEqual(audit_payload["mutation_key"], "mk-001")
            self.assertEqual(audit_payload["request"]["block_code"], "CSBK")
            self.assertEqual(audit_payload["request"]["block_name"], "测试板块")
            self.assertEqual(result._provider_artifacts[0]["kind"], "block_mutation_audit")
            self.assertEqual(result._provider_artifacts[0]["path"], str(audit_log_path))

    def test_block_mutation_bridge_defers_create_sector_runtime_write_until_governance_execute(self) -> None:
        governed_result = Result(ok=True, code=ErrorCode.OK, message="governed", data={})
        with (
            patch("tdxquant.api.bridge._run_tq_call") as mocked_run,
            patch("tdxquant.api.bridge.apply_block_mutation_safety", return_value=governed_result) as mocked_govern,
        ):
            result = run_tdx_create_sector(
                block_code="CSBK",
                block_name="测试板块",
                mutation_key="mk-001",
                audit_dir="runtime/block-mutations",
                strategy_path="strategy.py",
            )

        self.assertIs(result, governed_result)
        mocked_run.assert_not_called()
        mocked_govern.assert_called_once()
        _, kwargs = mocked_govern.call_args
        self.assertEqual(kwargs["operation"], "create_sector")
        self.assertEqual(kwargs["block_code"], "CSBK")
        self.assertEqual(kwargs["block_name"], "测试板块")
        self.assertEqual(kwargs["mutation_key"], "mk-001")
        self.assertEqual(kwargs["audit_dir"], "runtime/block-mutations")
        self.assertTrue(callable(kwargs["execute_write"]))
        self.assertTrue(callable(kwargs["observed_state"]))

    def test_block_mutation_bridges_defer_runtime_write_until_governance_execute(self) -> None:
        governed_result = Result(ok=True, code=ErrorCode.OK, message="governed", data={})
        cases = [
            ("delete_sector", run_tdx_delete_sector, {"block_code": "CSBK", "mutation_key": "mk-002", "audit_dir": "runtime/block-mutations", "strategy_path": "strategy.py"}),
            ("rename_sector", run_tdx_rename_sector, {"block_code": "CSBK", "block_name": "测试板块重命名", "mutation_key": "mk-003", "audit_dir": "runtime/block-mutations", "strategy_path": "strategy.py"}),
            ("clear_sector", run_tdx_clear_sector, {"block_code": "CSBK", "mutation_key": "mk-004", "audit_dir": "runtime/block-mutations", "strategy_path": "strategy.py"}),
            ("send_user_block", run_tdx_send_user_block, {"block_code": "ZXG", "stocks": ["000001.SZ"], "show": True, "mutation_key": "mk-005", "audit_dir": "runtime/block-mutations", "strategy_path": "strategy.py"}),
        ]

        for operation, bridge_fn, kwargs in cases:
            with self.subTest(operation=operation):
                with (
                    patch("tdxquant.api.bridge._run_tq_call") as mocked_run,
                    patch("tdxquant.api.bridge.apply_block_mutation_safety", return_value=governed_result) as mocked_govern,
                ):
                    result = bridge_fn(**kwargs)

                self.assertIs(result, governed_result)
                mocked_run.assert_not_called()
                mocked_govern.assert_called_once()
                self.assertTrue(callable(mocked_govern.call_args.kwargs["execute_write"]))
                self.assertTrue(callable(mocked_govern.call_args.kwargs["observed_state"]))
                self.assertEqual(mocked_govern.call_args.kwargs["operation"], operation)

    def test_block_mutation_wrapper_writes_audit_artifact_on_failure(self) -> None:
        raw_result = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="write failed",
            data={},
            warnings=["runtime-warning"],
            next_action="retry later",
        )
        with (
            TemporaryDirectory() as temp_dir,
            patch("tdxquant.api.bridge._run_tq_call", return_value=raw_result),
            patch(
                "tdxquant.api.bridge._probe_custom_sector_state",
                return_value={"block_code": "ZXG", "exists": True, "stocks": ["000001.SZ"]},
            ),
        ):
            result = run_tdx_send_user_block(
                block_code="ZXG",
                stocks=["000001.SZ", "600519.SH"],
                show=True,
                mutation_key="mk-send-1",
                audit_dir=temp_dir,
                strategy_path="strategy.py",
            )
            summary = result.data["block_mutation"]
            audit_log_path = Path(result.data["artifacts"]["audit_log_path"])
            self.assertEqual(summary["operation"], "send_user_block")
            self.assertEqual(summary["status"], "failed")
            self.assertEqual(summary["requested_stock_count"], 2)
            self.assertTrue(summary["show"])
            self.assertTrue(audit_log_path.exists())
            audit_payload = json.loads(audit_log_path.read_text(encoding="utf-8"))
            self.assertEqual(audit_payload["status"], "failed")
            self.assertEqual(audit_payload["request"]["stocks"], ["000001.SZ", "600519.SH"])
            self.assertEqual(audit_payload["result"]["code"], ErrorCode.EXECUTION_FAILED.value)
            self.assertEqual(audit_payload["result"]["next_action"], "retry later")

    def test_block_sync_bridge_forwards_sync_contract_to_orchestrator(self) -> None:
        planned_result = Result(ok=True, code=ErrorCode.OK, message="planned", data={"sync": {"status": "applied"}})
        with patch("tdxquant.api.bridge.sync_watchlist_to_block", return_value=planned_result) as mocked_sync:
            result = run_tdx_block_sync(
                block_code="ZXG",
                symbols=["000001.SZ", "600519.SH"],
                mode="merge",
                create_if_missing=True,
                dry_run=True,
                show=False,
                write_policy="merge_dry_run",
                mutation_key="sync-001",
                audit_dir="runtime/block-sync",
                strategy_path="strategy.py",
            )

        self.assertIs(result, planned_result)
        mocked_sync.assert_called_once()
        kwargs = mocked_sync.call_args.kwargs
        self.assertEqual(kwargs["block_code"], "ZXG")
        self.assertEqual(kwargs["symbols"], ["000001.SZ", "600519.SH"])
        self.assertEqual(kwargs["mode"], "merge")
        self.assertEqual(kwargs["write_policy"], "merge_dry_run")
        self.assertTrue(kwargs["create_if_missing"])
        self.assertTrue(kwargs["dry_run"])
        self.assertFalse(kwargs["show"])
        self.assertEqual(kwargs["mutation_key"], "sync-001")
        self.assertEqual(kwargs["audit_dir"], "runtime/block-sync")
        self.assertTrue(callable(kwargs["observed_state"]))
        self.assertTrue(callable(kwargs["create_block"]))
        self.assertTrue(callable(kwargs["sync_members"]))


class _FakeTqSubscriptionRuntime:
    initialize_calls: list[str] = []
    subscribe_calls: list[tuple[list[str], object]] = []
    unsubscribe_calls: list[list[str]] = []
    list_calls: int = 0
    close_calls: int = 0

    @classmethod
    def reset(cls) -> None:
        cls.initialize_calls = []
        cls.subscribe_calls = []
        cls.unsubscribe_calls = []
        cls.list_calls = 0
        cls.close_calls = 0

    @classmethod
    def initialize(cls, strategy_path: str) -> None:
        cls.initialize_calls.append(strategy_path)

    @classmethod
    def subscribe_hq(cls, stock_list: list[str], callback) -> dict[str, str]:
        cls.subscribe_calls.append((list(stock_list), callback))
        return {"Error": "ok", "ErrorId": "0", "run_id": "1"}

    @classmethod
    def unsubscribe_hq(cls, stock_list: list[str]) -> dict[str, str]:
        cls.unsubscribe_calls.append(list(stock_list))
        return {"Error": "ok", "ErrorId": "0", "run_id": "1"}

    @classmethod
    def get_subscribe_hq_stock_list(cls) -> list[str]:
        cls.list_calls += 1
        return ["600519.SH", "688318.SH"]

    @classmethod
    def close(cls) -> None:
        cls.close_calls += 1


class RuntimeSubscriptionSessionTests(unittest.TestCase):
    def test_subscription_session_reuses_initialized_runtime_until_close(self) -> None:
        _FakeTqSubscriptionRuntime.reset()
        callback = object()
        with patch(
            "tdxquant.api.bridge._load_tqcenter",
            return_value=(
                _FakeTqSubscriptionRuntime,
                {"available": True, "module": "tqcenter"},
            ),
        ), patch("tdxquant.api.bridge.IS_WINDOWS", True):
            session = TdxRuntimeSubscriptionSession(strategy_path="strategy.py")
            subscribe_result = session.subscribe_hq(stock_list=["688318.SH"], callback=callback)
            list_result = session.get_subscribe_hq_stock_list()
            unsubscribe_result = session.unsubscribe_hq(stock_list=["688318.SH"])

            self.assertTrue(subscribe_result.ok)
            self.assertTrue(list_result.ok)
            self.assertTrue(unsubscribe_result.ok)
            self.assertEqual(_FakeTqSubscriptionRuntime.initialize_calls, ["strategy.py"])
            self.assertEqual(_FakeTqSubscriptionRuntime.close_calls, 0)
            self.assertEqual(_FakeTqSubscriptionRuntime.subscribe_calls, [(["688318.SH"], callback)])
            self.assertEqual(_FakeTqSubscriptionRuntime.list_calls, 1)
            self.assertEqual(_FakeTqSubscriptionRuntime.unsubscribe_calls, [["688318.SH"]])

            session.close()

        self.assertEqual(_FakeTqSubscriptionRuntime.close_calls, 1)

    def test_subscription_session_rejects_use_after_close(self) -> None:
        _FakeTqSubscriptionRuntime.reset()
        with patch(
            "tdxquant.api.bridge._load_tqcenter",
            return_value=(
                _FakeTqSubscriptionRuntime,
                {"available": True, "module": "tqcenter"},
            ),
        ), patch("tdxquant.api.bridge.IS_WINDOWS", True):
            session = TdxRuntimeSubscriptionSession(strategy_path="strategy.py")
            session.close()

            subscribe_result = session.subscribe_hq(stock_list=["688318.SH"], callback=object())
            list_result = session.get_subscribe_hq_stock_list()
            unsubscribe_result = session.unsubscribe_hq(stock_list=["688318.SH"])

        self.assertEqual(subscribe_result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(list_result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(unsubscribe_result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(_FakeTqSubscriptionRuntime.close_calls, 1)

    def test_subscription_one_shot_wrappers_invoke_runtime_once_and_close(self) -> None:
        _FakeTqSubscriptionRuntime.reset()
        with patch(
            "tdxquant.api.bridge._load_tqcenter",
            return_value=(
                _FakeTqSubscriptionRuntime,
                {"available": True, "module": "tqcenter"},
            ),
        ), patch("tdxquant.api.bridge.IS_WINDOWS", True):
            subscribe_result = run_tdx_subscription_subscribe(["688318.SH"], strategy_path="strategy.py")
            list_result = run_tdx_subscription_list(strategy_path="strategy.py")
            unsubscribe_result = run_tdx_subscription_unsubscribe(["688318.SH"], strategy_path="strategy.py")

        self.assertTrue(subscribe_result.ok)
        self.assertTrue(list_result.ok)
        self.assertTrue(unsubscribe_result.ok)
        self.assertEqual(_FakeTqSubscriptionRuntime.initialize_calls, ["strategy.py", "strategy.py", "strategy.py"])
        self.assertEqual(_FakeTqSubscriptionRuntime.close_calls, 3)
        self.assertEqual(_FakeTqSubscriptionRuntime.subscribe_calls[0][0], ["688318.SH"])
        self.assertTrue(callable(_FakeTqSubscriptionRuntime.subscribe_calls[0][1]))
        self.assertEqual(_FakeTqSubscriptionRuntime.list_calls, 1)
        self.assertEqual(_FakeTqSubscriptionRuntime.unsubscribe_calls, [["688318.SH"]])
        self.assertEqual(subscribe_result.data["subscription_query"]["mode"], "one_shot")
        self.assertEqual(subscribe_result.data["subscription_query"]["action"], "subscribe_hq")
        self.assertFalse(subscribe_result.data["subscription_query"]["foreground_watch_started"])
        self.assertFalse(subscribe_result.data["subscription_query"]["background_worker_started"])
        self.assertFalse(subscribe_result.data["subscription_query"]["event_stream_started"])

    def test_runtime_api_exposes_subscription_one_shot_wrappers(self) -> None:
        expected = Result(ok=True, code=ErrorCode.OK, message="ok")
        runtime = RuntimeApi(strategy_path="strategy.py")

        with patch("tdxquant.api.runtime.run_tdx_subscription_subscribe", return_value=expected) as subscribe:
            self.assertIs(runtime.subscription_subscribe(["688318.SH"]), expected)
        with patch("tdxquant.api.runtime.run_tdx_subscription_unsubscribe", return_value=expected) as unsubscribe:
            self.assertIs(runtime.subscription_unsubscribe(["688318.SH"]), expected)
        with patch("tdxquant.api.runtime.run_tdx_subscription_list", return_value=expected) as list_subscriptions:
            self.assertIs(runtime.subscription_list(), expected)

        subscribe.assert_called_once_with(stock_list=["688318.SH"], strategy_path="strategy.py")
        unsubscribe.assert_called_once_with(stock_list=["688318.SH"], strategy_path="strategy.py")
        list_subscriptions.assert_called_once_with(strategy_path="strategy.py")


if __name__ == "__main__":
    unittest.main()
