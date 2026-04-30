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
        self.assertIn("runtime-capabilities-success", names)
        self.assertIn("runtime-doctor-degraded", names)
        self.assertIn("block-send-user-block-applied", names)
        self.assertIn("subscription-event-batch", names)
        first = fixtures[0]
        self.assertIn("name", first)
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
        self.assertEqual(payload["capability"], "formula.screen")
        self.assertEqual(payload["data"]["matched_symbols"], ["000001.SZ"])
        self.assertEqual(payload["data"]["summary"]["matched_symbol_count"], 1)

    def test_load_jsonl_fixture_returns_rows(self) -> None:
        rows = load_provider_replay_fixture("subscription-event-batch")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["event_type"], "quote_update")
        self.assertEqual(rows[0]["symbol"], "600519.SH")
        self.assertEqual(rows[1]["sequence"], 2)

    def test_load_block_mutation_fixture_returns_provider_artifact_descriptor(self) -> None:
        payload = load_provider_replay_fixture("block-send-user-block-applied")
        self.assertTrue(payload["success"])
        self.assertEqual(payload["capability"], "block.send_user_block")
        self.assertEqual(payload["data"]["block_mutation"]["mutation_key"], "watchlist-sync-20260428-01")
        self.assertEqual(payload["artifacts"][0]["kind"], "block_mutation_audit")

    def test_unknown_fixture_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            load_provider_replay_fixture("missing-fixture")


if __name__ == "__main__":
    unittest.main()
