import unittest

from tdxquant.replay_fixtures import (
    get_provider_replay_fixture_path,
    list_provider_replay_fixtures,
    load_provider_replay_fixture,
)


class ProviderReplayFixtureTests(unittest.TestCase):
    def test_fixture_manifest_exposes_expected_samples(self) -> None:
        fixtures = list_provider_replay_fixtures()
        names = {item["name"] for item in fixtures}
        self.assertIn("provider-result-success", names)
        self.assertIn("provider-result-failure", names)
        self.assertIn("formula-screen-success", names)
        self.assertIn("formula-screen-failure", names)
        self.assertIn("runtime-capabilities-success", names)
        self.assertIn("runtime-health-degraded", names)
        self.assertIn("runtime-doctor-degraded", names)
        self.assertIn("market-snapshot-success", names)
        self.assertIn("market-stock-info-success", names)
        self.assertIn("market-more-info-success", names)
        self.assertIn("market-cb-info-success", names)
        self.assertIn("market-kline-success", names)
        self.assertIn("meta-stock-list-success", names)
        self.assertIn("meta-sector-stocks-success", names)
        self.assertIn("financial-financial-data-success", names)
        self.assertIn("financial-financial-data-by-date-success", names)
        self.assertIn("transaction-stock-transaction-data-success", names)
        self.assertIn("transaction-market-transaction-data-success", names)
        self.assertIn("market-kline-empty", names)
        self.assertIn("meta-sector-stocks-empty", names)
        self.assertIn("financial-financial-data-failure", names)
        self.assertIn("transaction-stock-transaction-data-failure", names)
        self.assertIn("block-send-user-block-applied", names)
        self.assertIn("block-send-user-block-noop", names)
        self.assertIn("block-send-user-block-rejected", names)
        self.assertIn("block-read-watchlist-success", names)
        self.assertIn("block-read-watchlist-empty", names)
        self.assertIn("block-read-watchlist-missing-block", names)
        self.assertIn("block-read-watchlist-invalid-member", names)
        self.assertIn("block-sync-replace-applied", names)
        self.assertIn("block-sync-merge-noop", names)
        self.assertIn("block-sync-replace-rejected", names)
        self.assertIn("block-sync-replace-plan", names)
        self.assertIn("subscription-event-batch", names)
        self.assertIn("subscription-watch-events", names)
        self.assertIn("subscription-watch-status-completed", names)
        self.assertIn("subscription-watch-summary-completed", names)
        self.assertIn("subscription-watch-manifest", names)
        first = fixtures[0]
        self.assertIn("name", first)
        self.assertIn("subscription-watch-events", names)
        self.assertIn("subscription-watch-status-completed", names)
        self.assertIn("subscription-watch-summary-completed", names)
        self.assertIn("subscription-watch-manifest", names)
        self.assertIn("capability", first)
        self.assertIn("format", first)
        self.assertIn("description", first)
        self.assertIn("relative_path", first)

    def test_get_provider_replay_fixture_path_returns_existing_file(self) -> None:
        path = get_provider_replay_fixture_path("formula-screen-success")
        self.assertTrue(path.is_absolute())
        self.assertTrue(path.exists())

    def test_load_json_fixture_returns_parsed_object(self) -> None:
        payload = load_provider_replay_fixture("formula-screen-success")
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability"], "formula.screen")
        self.assertEqual(payload["data"]["matched_symbols"], ["000001.SZ"])
        self.assertEqual(payload["data"]["summary"]["matched_symbol_count"], 1)

    def test_load_market_snapshot_query_fixture_returns_query_meta(self) -> None:
        payload = load_provider_replay_fixture("market-snapshot-success")
        self.assertTrue(payload["success"])
        self.assertEqual(payload["capability"], "market.snapshot")
        self.assertEqual(payload["data"]["query_meta"]["query_kind"], "market.snapshot")
        self.assertEqual(payload["data"]["query_meta"]["symbol"], "000001.SZ")

    def test_load_market_stock_info_query_fixture_returns_query_meta(self) -> None:
        payload = load_provider_replay_fixture("market-stock-info-success")
        self.assertTrue(payload["success"])
        self.assertEqual(payload["capability"], "market.stock_info")
        self.assertEqual(payload["data"]["rows"][0]["symbol"], "688260.SH")
        self.assertEqual(payload["data"]["query_meta"]["query_kind"], "market.stock_info")
        self.assertEqual(payload["data"]["query_meta"]["symbol"], "688260.SH")
        self.assertEqual(payload["data"]["query_meta"]["requested_fields"], ["symbol", "name", "market"])

    def test_load_market_more_info_query_fixture_returns_query_meta(self) -> None:
        payload = load_provider_replay_fixture("market-more-info-success")
        self.assertTrue(payload["success"])
        self.assertEqual(payload["capability"], "market.more_info")
        self.assertEqual(payload["data"]["rows"][0]["symbol"], "688260.SH")
        self.assertEqual(payload["data"]["query_meta"]["query_kind"], "market.more_info")
        self.assertEqual(payload["data"]["query_meta"]["symbol"], "688260.SH")
        self.assertEqual(payload["data"]["query_meta"]["requested_fields"], ["symbol", "industry", "area"])

    def test_load_market_cb_info_query_fixture_returns_query_meta(self) -> None:
        payload = load_provider_replay_fixture("market-cb-info-success")
        self.assertTrue(payload["success"])
        self.assertEqual(payload["capability"], "market.cb_info")
        self.assertEqual(payload["data"]["rows"][0]["symbol"], "113015.SZ")
        self.assertEqual(payload["data"]["query_meta"]["query_kind"], "market.cb_info")
        self.assertEqual(payload["data"]["query_meta"]["symbol"], "113015.SZ")
        self.assertEqual(payload["data"]["query_meta"]["requested_fields"], ["symbol", "name", "issue_date"])

    def test_load_formula_failure_fixture_returns_hardened_provider_envelope(self) -> None:
        payload = load_provider_replay_fixture("formula-screen-failure")
        self.assertFalse(payload["success"])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["capability"], "formula.screen")
        self.assertIn("next_action", payload["data"])

    def test_load_runtime_health_fixture_returns_hardened_provider_envelope(self) -> None:
        payload = load_provider_replay_fixture("runtime-health-degraded")
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability"], "runtime.health")
        self.assertEqual(payload["data"]["overall_status"], "degraded")
        self.assertIn("recommended_action_items", payload["data"])
        self.assertIn("id", payload["data"]["recommended_action_items"][0])
        self.assertIn("related_checks", payload["data"]["recommended_action_items"][0])

    def test_load_runtime_doctor_fixture_returns_structured_findings(self) -> None:
        payload = load_provider_replay_fixture("runtime-doctor-degraded")
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability"], "runtime.doctor")
        finding = payload["data"]["findings"][0]
        self.assertIn("related_checks", finding)
        self.assertIn("recommended_action_id", finding)

    def test_load_runtime_capabilities_fixture_returns_grading_summary(self) -> None:
        payload = load_provider_replay_fixture("runtime-capabilities-success")
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertIn("by_domain", payload["data"]["summary"])
        self.assertIn("grading", payload["data"])
        self.assertIn("stability_levels", payload["data"]["grading"])
        capability_names = {item["name"] for item in payload["data"]["capabilities"]}
        self.assertIn("block.read_watchlist_snapshot", capability_names)

    def test_load_runtime_capabilities_fixture_includes_query_metadata_for_supported_queries(self) -> None:
        payload = load_provider_replay_fixture("runtime-capabilities-success")
        capabilities = {item["name"]: item for item in payload["data"]["capabilities"]}
        self.assertEqual(
            capabilities["market.snapshot"]["query_metadata"],
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

    def test_load_jsonl_fixture_returns_rows(self) -> None:
        rows = load_provider_replay_fixture("subscription-event-batch")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["capability"], "subscription.watch")
        self.assertEqual(rows[0]["run_id"], "20260501T080000000000Z")
        self.assertEqual(rows[0]["event_type"], "quote_update")
        self.assertEqual(rows[0]["symbol"], "600519.SH")
        self.assertEqual(rows[0]["capability"], "subscription.watch")
        self.assertEqual(rows[0]["run_id"], "20260501T080000000000Z")
        self.assertEqual(rows[1]["sequence"], 2)

    def test_load_subscription_watch_summary_fixture(self) -> None:
        payload = load_provider_replay_fixture("subscription-watch-summary-completed")
        self.assertEqual(payload["capability"], "subscription.watch")
        self.assertEqual(payload["final_state"], "completed")
        self.assertEqual(payload["stop_reason"], "max_events")

    def test_fixture_manifest_exposes_subscription_watch_resilience_samples(self) -> None:
        fixtures = list_provider_replay_fixtures()
        names = {item["name"] for item in fixtures}
        self.assertIn("subscription-watch-status-reconnecting", names)
        self.assertIn("subscription-watch-status-degraded", names)
        self.assertIn("subscription-watch-summary-with-reconnect", names)
        self.assertIn("subscription-watch-event-stream-frames", names)

    def test_load_subscription_watch_reconnecting_status_fixture(self) -> None:
        payload = load_provider_replay_fixture("subscription-watch-status-reconnecting")
        self.assertEqual(payload["capability"], "subscription.watch")
        self.assertEqual(payload["state"], "reconnecting")
        self.assertEqual(payload["reconnect_count"], 1)
        self.assertEqual(payload["consecutive_reconnect_failures"], 1)
        self.assertIsNotNone(payload["next_reconnect_at"])
        self.assertEqual(payload["last_error"]["code"], "SESSION_LOST")

    def test_load_subscription_watch_degraded_status_fixture(self) -> None:
        payload = load_provider_replay_fixture("subscription-watch-status-degraded")
        self.assertEqual(payload["capability"], "subscription.watch")
        self.assertEqual(payload["state"], "degraded")
        self.assertEqual(payload["reconnect_count"], 3)
        self.assertEqual(payload["consecutive_reconnect_failures"], 3)
        self.assertIsNone(payload["next_reconnect_at"])
        self.assertIsNotNone(payload["degraded_since"])

    def test_load_subscription_watch_summary_with_reconnect_fixture(self) -> None:
        payload = load_provider_replay_fixture("subscription-watch-summary-with-reconnect")
        self.assertEqual(payload["capability"], "subscription.watch")
        self.assertEqual(payload["final_state"], "completed")
        self.assertEqual(payload["reconnect_count"], 1)
        self.assertEqual(payload["degraded_duration_ms"], 0.0)
        self.assertIsNone(payload["final_last_error"])

    def test_load_subscription_watch_event_stream_fixture(self) -> None:
        rows = load_provider_replay_fixture("subscription-watch-event-stream-frames")
        self.assertGreaterEqual(len(rows), 5)
        frame_types = {row["frame_type"] for row in rows}
        self.assertIn("quote", frame_types)
        self.assertIn("status", frame_types)
        self.assertIn("heartbeat", frame_types)
        self.assertIn("terminal", frame_types)
        quote = next(row for row in rows if row["frame_type"] == "quote")
        self.assertIn("event", quote)
        self.assertEqual(quote["event"]["capability"], "subscription.watch")
        self.assertEqual(quote["event"]["reconnect_metadata"]["reconnect_count"], 1)

    def test_load_block_mutation_fixture_returns_provider_artifact_descriptor(self) -> None:
        payload = load_provider_replay_fixture("block-send-user-block-applied")
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability"], "block.send_user_block")
        self.assertEqual(payload["data"]["block_mutation"]["mutation_key"], "watchlist-sync-20260428-01")
        self.assertEqual(payload["data"]["block_mutation"]["status"], "applied")
        self.assertEqual(payload["data"]["block_mutation"]["governance_decision"], "execute")
        self.assertEqual(payload["artifacts"][0]["kind"], "block_mutation_audit")

    def test_load_block_mutation_noop_fixture_returns_governance_summary(self) -> None:
        payload = load_provider_replay_fixture("block-send-user-block-noop")
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["block_mutation"]["status"], "noop")
        self.assertEqual(payload["data"]["block_mutation"]["governance_decision"], "skip")
        self.assertEqual(payload["data"]["block_mutation"]["governance_reason"], "already_applied")
        self.assertIn("observed_state", payload["data"]["block_mutation"])

    def test_load_block_mutation_rejected_fixture_returns_governance_summary(self) -> None:
        payload = load_provider_replay_fixture("block-send-user-block-rejected")
        self.assertFalse(payload["success"])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["code"], "invalid_request")
        self.assertEqual(payload["data"]["block_mutation"]["status"], "rejected")
        self.assertEqual(payload["data"]["block_mutation"]["governance_decision"], "reject")
        self.assertEqual(payload["data"]["block_mutation"]["governance_reason"], "missing_block")
        self.assertIn("observed_state", payload["data"]["block_mutation"])

    def test_load_block_read_watchlist_success_fixture_returns_snapshot_contract(self) -> None:
        payload = load_provider_replay_fixture("block-read-watchlist-success")
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability"], "block.read_watchlist_snapshot")
        self.assertEqual(payload["data"]["snapshot"]["block_code"], "ZXG")
        self.assertEqual(payload["data"]["snapshot"]["symbols"], ["600519.SH", "000001.SZ"])
        self.assertEqual(payload["data"]["snapshot"]["source_metadata"]["duplicate_count"], 1)

    def test_load_block_read_watchlist_missing_block_fixture_returns_invalid_request(self) -> None:
        payload = load_provider_replay_fixture("block-read-watchlist-missing-block")
        self.assertFalse(payload["success"])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["capability"], "block.read_watchlist_snapshot")
        self.assertEqual(payload["code"], "invalid_request")
        self.assertEqual(payload["message"], "block_code not found: ZXG")

    def test_load_block_sync_applied_fixture_returns_sync_summary(self) -> None:
        payload = load_provider_replay_fixture("block-sync-replace-applied")
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["capability"], "block.sync_watchlist")
        self.assertEqual(payload["data"]["sync"]["mode"], "replace")
        self.assertEqual(payload["data"]["sync"]["status"], "applied")
        self.assertEqual(payload["data"]["block_mutation"]["operation"], "send_user_block")
        self.assertEqual(payload["artifacts"][0]["kind"], "block_sync_audit")

    def test_load_block_sync_plan_fixture_returns_dry_run_summary(self) -> None:
        payload = load_provider_replay_fixture("block-sync-replace-plan")
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["sync"]["dry_run"], True)
        self.assertEqual(payload["data"]["sync"]["would_create_block"], True)

    def test_unknown_fixture_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            load_provider_replay_fixture("missing-fixture")


if __name__ == "__main__":
    unittest.main()
