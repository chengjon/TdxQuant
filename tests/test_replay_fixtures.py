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
        self.assertIn("block-send-user-block-applied", names)
        self.assertIn("block-send-user-block-noop", names)
        self.assertIn("block-send-user-block-rejected", names)
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

    def test_unknown_fixture_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            load_provider_replay_fixture("missing-fixture")


if __name__ == "__main__":
    unittest.main()
