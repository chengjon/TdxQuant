import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tdxquant.api import TdxTaskManager
from tdxquant.trade_audit_index import build_trade_audit_index_cache, query_trade_audit_cross_ledger


def _write_audit(
    path: Path,
    *,
    audit_id: str,
    recorded_at: str,
    status: str | None = "confirmed",
    broker: str | None = "pingan",
    code: str = "000001",
    contract_no: str = "B202605140001",
    submission_key: str = "submit-001",
    method: str | None = "buy_submit_once",
) -> None:
    trade_audit = {
        "audit_id": audit_id,
        "recorded_at": recorded_at,
        "contract_no": contract_no,
        "submission_key": submission_key,
    }
    if status is not None:
        trade_audit["status"] = status
    if broker is not None:
        trade_audit["broker"] = broker
    if method is not None:
        trade_audit["method"] = method
    path.write_text(
        json.dumps(
            {
                "schema_version": "2026-04-29",
                "trade_audit": trade_audit,
                "result": {"data": {"code": code}},
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


class TradeAuditIndexTests(unittest.TestCase):
    def test_build_trade_audit_index_cache_skips_corrupt_audit_files(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir()
            _write_audit(
                audit_dir / "valid.json",
                audit_id="audit-001",
                recorded_at="2026-05-14T01:00:00+00:00",
            )
            corrupt_path = audit_dir / "corrupt.json"
            corrupt_path.write_text("{not json", encoding="utf-8")
            cache_path = Path(temp_dir) / "audit-index-cache.json"

            payload = build_trade_audit_index_cache(audit_dir=audit_dir, cache_path=cache_path)
            written = json.loads(cache_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], "tdx.trade_audit.index.v1")
        self.assertEqual(payload["summary"]["scanned_files"], 2)
        self.assertEqual(payload["summary"]["indexed_entries"], 1)
        self.assertEqual(payload["entries"][0]["audit_id"], "audit-001")
        self.assertEqual(payload["entries"][0]["code"], "000001")
        self.assertIn("corrupt.json", payload["warnings"][0])
        self.assertEqual(written["entries"][0]["audit_path"], payload["entries"][0]["audit_path"])

    def test_cross_ledger_query_joins_exact_keys_and_warns_for_damaged_jsonl(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir()
            _write_audit(
                audit_dir / "audit.json",
                audit_id="audit-join-001",
                recorded_at="2026-05-14T02:00:00+00:00",
                status="confirmed",
                code="000001",
                contract_no="B202605140101",
                submission_key="submit-join-001",
            )
            submission_ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            submission_ledger_path.write_text(
                json.dumps(
                    {
                        "timestamp": "2026-05-14T02:01:00+00:00",
                        "submission_key": "submit-join-001",
                        "result": {"trade_audit": {"audit_id": "audit-join-001"}},
                    },
                    ensure_ascii=False,
                )
                + "\n{bad json\n",
                encoding="utf-8",
            )
            task_ledger_path = Path(temp_dir) / "task-ledger.jsonl"
            task_ledger_path.write_text(
                json.dumps(
                    {
                        "timestamp": "2026-05-14T02:02:00+00:00",
                        "code": "000001",
                        "contract_no": "B202605140101",
                        "task_name": "guarded_trade_buy",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            result = query_trade_audit_cross_ledger(
                audit_dir=audit_dir,
                submission_ledger_path=submission_ledger_path,
                task_ledger_jsonl_path=task_ledger_path,
                submission_key="submit-join-001",
                status="confirmed",
            )

        self.assertEqual(result["summary"]["filtered_entries"], 1)
        self.assertEqual(result["rows"][0]["audit"]["audit_id"], "audit-join-001")
        self.assertEqual(result["rows"][0]["join_keys"]["submission_key"], "submit-join-001")
        self.assertEqual(len(result["rows"][0]["submission_matches"]), 1)
        self.assertEqual(len(result["rows"][0]["task_matches"]), 1)
        self.assertIn("submission-ledger.jsonl:2", "\n".join(result["warnings"]))

    def test_cross_ledger_query_returns_broker_method_status_aggregation(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir()
            _write_audit(
                audit_dir / "audit-1.json",
                audit_id="audit-agg-001",
                recorded_at="2026-05-14T04:00:00+00:00",
                status="confirmed",
                broker="pingan",
                method="buy_submit_once",
            )
            _write_audit(
                audit_dir / "audit-2.json",
                audit_id="audit-agg-002",
                recorded_at="2026-05-14T04:01:00+00:00",
                status="rejected",
                broker="pingan",
                method="buy_submit_once",
            )
            _write_audit(
                audit_dir / "audit-3.json",
                audit_id="audit-agg-003",
                recorded_at="2026-05-14T04:02:00+00:00",
                status="confirmed",
                broker="sim",
                method="confirm_current",
            )

            result = query_trade_audit_cross_ledger(audit_dir=audit_dir)

        self.assertEqual(result["aggregation"]["by_status"], {"confirmed": 2, "rejected": 1})
        self.assertEqual(result["aggregation"]["by_method"], {"buy_submit_once": 2, "confirm_current": 1})
        self.assertEqual(result["aggregation"]["by_broker"], {"pingan": 2, "sim": 1})
        self.assertIn(
            {"broker": "pingan", "method": "buy_submit_once", "status": "confirmed", "count": 1},
            result["aggregation"]["by_broker_method_status"],
        )

    def test_cross_ledger_query_aggregation_uses_filtered_entries_before_limit(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir()
            for index, status in enumerate(["confirmed", "confirmed", "rejected"], start=1):
                _write_audit(
                    audit_dir / f"audit-{index}.json",
                    audit_id=f"audit-limit-{index}",
                    recorded_at=f"2026-05-14T05:0{index}:00+00:00",
                    status=status,
                )

            result = query_trade_audit_cross_ledger(audit_dir=audit_dir, limit=1)

        self.assertEqual(result["summary"]["returned_rows"], 1)
        self.assertEqual(result["summary"]["filtered_entries"], 3)
        self.assertEqual(result["aggregation"]["by_status"], {"confirmed": 2, "rejected": 1})

    def test_cross_ledger_query_aggregation_counts_missing_dimensions_as_unknown(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir()
            _write_audit(
                audit_dir / "audit-unknown.json",
                audit_id="audit-unknown-001",
                recorded_at="2026-05-14T06:00:00+00:00",
                status=None,
                broker=None,
                method=None,
            )

            result = query_trade_audit_cross_ledger(audit_dir=audit_dir)

        self.assertEqual(result["summary"]["returned_rows"], 1)
        self.assertEqual(result["aggregation"]["by_status"], {"unknown": 1})
        self.assertEqual(result["aggregation"]["by_method"], {"unknown": 1})
        self.assertEqual(result["aggregation"]["by_broker"], {"unknown": 1})

    def test_task_manager_cross_ledger_query_returns_task_metadata_and_artifacts(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_dir = Path(temp_dir) / "trade-audits"
            audit_dir.mkdir()
            _write_audit(
                audit_dir / "audit.json",
                audit_id="audit-task-001",
                recorded_at="2026-05-14T03:00:00+00:00",
                code="000002",
                contract_no="B202605140201",
                submission_key="submit-task-001",
            )
            submission_ledger_path = Path(temp_dir) / "submission-ledger.jsonl"
            submission_ledger_path.write_text(
                json.dumps({"submission_key": "submit-task-001", "result": {"ok": True}}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            task_ledger_path = Path(temp_dir) / "task-ledger.jsonl"
            task_ledger_path.write_text(
                json.dumps({"code": "000002", "contract_no": "B202605140201"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            cache_path = Path(temp_dir) / "cache.json"
            output_path = Path(temp_dir) / "query.json"
            manager = TdxTaskManager(
                profile="trade_audit_cross_ledger_query",
                strategy_path="strategy.py",
                profile_overrides={"export_dir": temp_dir, "audit_dir": str(audit_dir)},
            )

            result = manager.trade_audit_cross_ledger_query(
                submission_ledger_path=str(submission_ledger_path),
                task_ledger_jsonl_path=str(task_ledger_path),
                cache_output_path=str(cache_path),
                json_output_path=str(output_path),
                code="000002",
            )
            self.assertTrue(cache_path.exists())
            self.assertTrue(output_path.exists())

        self.assertTrue(result.ok)
        self.assertEqual(result.data["task"]["name"], "trade_audit_cross_ledger_query")
        self.assertEqual(result.data["summary"]["returned_rows"], 1)
        self.assertEqual(result.data["rows"][0]["submission_matches"][0]["submission_key"], "submit-task-001")
        self.assertEqual(result.data["artifacts"]["cache_output_path"], str(cache_path))


if __name__ == "__main__":
    unittest.main()
