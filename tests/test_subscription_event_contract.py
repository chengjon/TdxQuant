import unittest

from tdxquant.subscription_event import (
    SUBSCRIPTION_EVENT_CAPABILITY,
    SUBSCRIPTION_EVENT_SCHEMA_VERSION,
    extract_subscription_source_ts,
    extract_subscription_symbol,
    normalize_subscription_event_rows,
)


class SubscriptionEventContractTests(unittest.TestCase):
    def test_normalize_symbol_keyed_payload_splits_into_multiple_rows(self) -> None:
        rows = normalize_subscription_event_rows(
            {
                "600519.SH": {"Now": 123.45, "UpdateTime": "2026-04-28T09:30:01+08:00"},
                "000001.SZ": {"Now": 10.01, "UpdateTime": "2026-04-28T09:30:02+08:00"},
            },
            session_id="session-1",
            provider_instance_id="provider-1",
            subscription_id="sub-1",
            run_id="run-1",
            start_sequence=7,
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["schema_version"], SUBSCRIPTION_EVENT_SCHEMA_VERSION)
        self.assertEqual(rows[0]["capability"], SUBSCRIPTION_EVENT_CAPABILITY)
        self.assertEqual(rows[0]["run_id"], "run-1")
        self.assertEqual(rows[0]["sequence"], 7)
        self.assertEqual(rows[1]["sequence"], 8)
        self.assertEqual(rows[0]["symbol"], "600519.SH")
        self.assertEqual(rows[1]["symbol"], "000001.SZ")
        self.assertEqual(rows[0]["source_ts"], "2026-04-28T09:30:01+08:00")
        self.assertEqual(rows[0]["event_type"], "quote_update")
        self.assertEqual(rows[0]["reconnect_metadata"], {})
        self.assertIn("payload", rows[0])

    def test_normalize_payload_with_explicit_symbol_field(self) -> None:
        rows = normalize_subscription_event_rows(
            {
                "symbol": "688318.SH",
                "Now": 88.8,
                "UpdateTime": "2026-04-28T09:31:00+08:00",
            },
            session_id="session-1",
            provider_instance_id="provider-1",
            subscription_id="sub-1",
            run_id="run-1",
            start_sequence=1,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["symbol"], "688318.SH")
        self.assertEqual(rows[0]["source_ts"], "2026-04-28T09:31:00+08:00")
        self.assertEqual(rows[0]["payload"]["Now"], 88.8)

    def test_extract_helpers_allow_unstructured_payload_fallback(self) -> None:
        self.assertEqual(extract_subscription_symbol({"code": "000001.SZ"}), "000001.SZ")
        self.assertEqual(
            extract_subscription_source_ts({"timestamp": "2026-04-28T09:32:00+08:00"}),
            "2026-04-28T09:32:00+08:00",
        )
        rows = normalize_subscription_event_rows(
            "raw-event",
            session_id="session-1",
            provider_instance_id="provider-1",
            subscription_id="sub-1",
            run_id="run-1",
            start_sequence=3,
        )
        self.assertEqual(rows[0]["symbol"], None)
        self.assertEqual(rows[0]["payload"], "raw-event")
