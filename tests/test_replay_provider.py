import json
from pathlib import Path
from unittest.mock import patch

from tdxquant.api.manager import TdxApiManager
from tdxquant.provider_discovery import list_provider_capabilities
from tdxquant.replay_fixtures import load_provider_replay_fixture
from tdxquant.replay_provider import execute_sync_replay, materialize_subscription_watch_replay
from tdxquant.subscription_watch_run import build_subscription_watch_run_paths


def test_execute_sync_replay_uses_default_runtime_capabilities_fixture() -> None:
    result = execute_sync_replay("runtime.capabilities")

    assert result.ok is True
    assert result.message == "listed provider capabilities"
    capabilities = {item["name"]: item for item in result.data["capabilities"]}
    assert result.data["summary"]["total"] >= 5
    assert "block.read_watchlist_snapshot" in capabilities
    assert capabilities["market.snapshot"]["query_metadata"]["supports_replay"] is True
    assert result.data["replay_source"]["fixture"] == "runtime-capabilities-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_execute_sync_replay_uses_default_block_read_watchlist_fixture() -> None:
    result = execute_sync_replay("block.read_watchlist_snapshot")

    assert result.ok is True
    assert result.data["snapshot"]["block_code"] == "ZXG"
    assert result.data["snapshot"]["symbols"] == ["600519.SH", "000001.SZ"]
    assert result.data["replay_source"]["fixture"] == "block-read-watchlist-success"


def test_block_read_watchlist_discovery_metadata_is_exposed() -> None:
    capability = next(
        item for item in list_provider_capabilities() if item["name"] == "block.read_watchlist_snapshot"
    )

    assert capability["query_metadata"] == {
        "query_shapes": [
            {
                "query_kind": "block.read_watchlist_snapshot",
                "selectors": ["block_code"],
                "query_params": [],
            }
        ],
        "supports_empty_results": True,
        "supports_requested_fields": False,
        "supports_replay": True,
    }


def test_execute_sync_replay_uses_default_block_sync_fixture() -> None:
    result = execute_sync_replay("block.sync_watchlist")

    assert result.ok is True
    assert result.data["sync"]["mode"] == "replace"
    assert result.data["sync"]["status"] == "applied"
    assert result.data["replay_source"]["fixture"] == "block-sync-replace-applied"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_execute_sync_replay_uses_default_market_snapshot_fixture() -> None:
    result = execute_sync_replay("market.snapshot")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "market.snapshot"
    assert result.data["replay_source"]["fixture"] == "market-snapshot-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_execute_sync_replay_uses_default_market_stock_info_fixture() -> None:
    result = execute_sync_replay("market.stock_info")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "market.stock_info"
    assert result.data["query_meta"]["requested_fields"] == ["symbol", "name", "market"]
    assert result.data["rows"][0]["symbol"] == "688260.SH"
    assert result.data["replay_source"]["fixture"] == "market-stock-info-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_manager_market_stock_info_replay_uses_fixture_without_live_call() -> None:
    manager = TdxApiManager(provider_mode="replay")

    with patch("tdxquant.api.manager.MarketApi.stock_info", side_effect=AssertionError("live stock-info called")):
        result = manager.market.stock_info("688260.SH", fields=["symbol", "name", "market"])

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "market.stock_info"
    assert result.data["replay_source"]["fixture"] == "market-stock-info-success"


def test_execute_sync_replay_uses_default_market_more_info_fixture() -> None:
    result = execute_sync_replay("market.more_info")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "market.more_info"
    assert result.data["query_meta"]["requested_fields"] == ["symbol", "industry", "area"]
    assert result.data["rows"][0]["symbol"] == "688260.SH"
    assert result.data["replay_source"]["fixture"] == "market-more-info-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_manager_market_more_info_replay_uses_fixture_without_live_call() -> None:
    manager = TdxApiManager(provider_mode="replay")

    with patch("tdxquant.api.manager.MarketApi.more_info", side_effect=AssertionError("live more-info called")):
        result = manager.market.more_info("688260.SH", fields=["symbol", "industry", "area"])

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "market.more_info"
    assert result.data["replay_source"]["fixture"] == "market-more-info-success"


def test_execute_sync_replay_uses_default_market_cb_info_fixture() -> None:
    result = execute_sync_replay("market.cb_info")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "market.cb_info"
    assert result.data["query_meta"]["requested_fields"] == ["symbol", "name", "issue_date"]
    assert result.data["rows"][0]["symbol"] == "113015.SZ"
    assert result.data["replay_source"]["fixture"] == "market-cb-info-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_manager_market_cb_info_replay_uses_fixture_without_live_call() -> None:
    manager = TdxApiManager(provider_mode="replay")

    with patch("tdxquant.api.manager.MarketApi.cb_info", side_effect=AssertionError("live cb-info called")):
        result = manager.market.cb_info("113015.SZ", fields=["symbol", "name", "issue_date"])

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "market.cb_info"
    assert result.data["replay_source"]["fixture"] == "market-cb-info-success"


def test_execute_sync_replay_uses_default_meta_gb_info_fixture() -> None:
    result = execute_sync_replay("meta.gb_info")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "meta.gb_info"
    assert result.data["query_meta"]["date_list"] == ["20250101", "20241231"]
    assert result.data["query_meta"]["count"] == 2
    assert result.data["rows"][0]["symbol"] == "000001.SZ"
    assert result.data["replay_source"]["fixture"] == "meta-gb-info-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_manager_meta_gb_info_replay_uses_fixture_without_live_call() -> None:
    manager = TdxApiManager(provider_mode="replay")

    with patch("tdxquant.api.manager.MetaApi.gb_info", side_effect=AssertionError("live gb-info called")):
        result = manager.meta.gb_info("000001.SZ", date_list=["20250101", "20241231"], count=2)

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "meta.gb_info"
    assert result.data["replay_source"]["fixture"] == "meta-gb-info-success"


def test_execute_sync_replay_uses_default_meta_ipo_info_fixture() -> None:
    result = execute_sync_replay("meta.ipo_info")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "meta.ipo_info"
    assert result.data["query_meta"]["ipo_type"] == 2
    assert result.data["query_meta"]["ipo_date"] == 1
    assert result.data["rows"][0]["code"] == "301001.SZ"
    assert result.data["replay_source"]["fixture"] == "meta-ipo-info-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_manager_meta_ipo_info_replay_uses_fixture_without_live_call() -> None:
    manager = TdxApiManager(provider_mode="replay")

    with patch("tdxquant.api.manager.MetaApi.ipo_info", side_effect=AssertionError("live ipo-info called")):
        result = manager.meta.ipo_info(ipo_type=2, ipo_date=1)

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "meta.ipo_info"
    assert result.data["replay_source"]["fixture"] == "meta-ipo-info-success"


def test_execute_sync_replay_uses_default_meta_gp_one_fixture() -> None:
    result = execute_sync_replay("meta.gp_one_data")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "meta.gp_one_data"
    assert result.data["query_meta"]["symbols"] == ["000001.SZ", "600519.SH"]
    assert result.data["query_meta"]["requested_fields"] == ["Now", "Volume"]
    assert result.data["rows"][0]["symbol"] == "000001.SZ"
    assert result.data["replay_source"]["fixture"] == "meta-gp-one-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_manager_meta_gp_one_replay_uses_fixture_without_live_call() -> None:
    manager = TdxApiManager(provider_mode="replay")

    with patch("tdxquant.api.manager.MetaApi.gp_one_data", side_effect=AssertionError("live gp-one called")):
        result = manager.meta.gp_one_data(stock_list=["000001.SZ", "600519.SH"], fields=["Now", "Volume"])

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "meta.gp_one_data"
    assert result.data["replay_source"]["fixture"] == "meta-gp-one-success"


def test_execute_sync_replay_uses_default_meta_divid_factors_fixture() -> None:
    result = execute_sync_replay("meta.divid_factors")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "meta.divid_factors"
    assert result.data["query_meta"]["symbol"] == "688318.SH"
    assert result.data["query_meta"]["start_time"] == "20200101"
    assert result.data["query_meta"]["end_time"] == "20241231"
    assert result.data["rows"][0]["symbol"] == "688318.SH"
    assert result.data["replay_source"]["fixture"] == "meta-divid-factors-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_manager_meta_divid_factors_replay_uses_fixture_without_live_call() -> None:
    manager = TdxApiManager(provider_mode="replay")

    with patch("tdxquant.api.manager.MetaApi.divid_factors", side_effect=AssertionError("live divid-factors called")):
        result = manager.meta.divid_factors(stock_code="688318.SH", start_time="20200101", end_time="20241231")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "meta.divid_factors"
    assert result.data["replay_source"]["fixture"] == "meta-divid-factors-success"


def test_execute_sync_replay_uses_default_transaction_stock_transaction_by_date_fixture() -> None:
    result = execute_sync_replay("transaction.stock_transaction_data_by_date")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "transaction.stock_transaction_data_by_date"
    assert result.data["query_meta"]["symbols"] == ["000001.SZ", "000002.SZ"]
    assert result.data["query_meta"]["requested_fields"] == ["price", "volume"]
    assert result.data["query_meta"]["date"] == "20250101"
    assert result.data["rows"][0]["symbol"] == "000001.SZ"
    assert result.data["replay_source"]["fixture"] == "transaction-stock-transaction-data-by-date-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_manager_transaction_stock_transaction_by_date_replay_uses_fixture_without_live_call() -> None:
    manager = TdxApiManager(provider_mode="replay")

    with patch(
        "tdxquant.api.manager.TransactionApi.stock_transaction_data_by_date",
        side_effect=AssertionError("live stock transaction by-date called"),
    ):
        result = manager.transaction.stock_transaction_data_by_date(
            stock_list=["000001.SZ", "000002.SZ"],
            fields=["price", "volume"],
            year=2025,
            mmdd=101,
        )

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "transaction.stock_transaction_data_by_date"
    assert result.data["replay_source"]["fixture"] == "transaction-stock-transaction-data-by-date-success"


def test_execute_sync_replay_uses_default_transaction_market_transaction_by_date_fixture() -> None:
    result = execute_sync_replay("transaction.market_transaction_data_by_date")

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "transaction.market_transaction_data_by_date"
    assert result.data["query_meta"]["requested_fields"] == ["field_a", "field_b"]
    assert result.data["query_meta"]["date"] == "20250101"
    assert result.data["rows"][0]["field_a"] == 3
    assert result.data["replay_source"]["fixture"] == "transaction-market-transaction-data-by-date-success"
    assert result._provider_contract["runtime"]["mode"] == "replay"


def test_manager_transaction_market_transaction_by_date_replay_uses_fixture_without_live_call() -> None:
    manager = TdxApiManager(provider_mode="replay")

    with patch(
        "tdxquant.api.manager.TransactionApi.market_transaction_data_by_date",
        side_effect=AssertionError("live market transaction by-date called"),
    ):
        result = manager.transaction.market_transaction_data_by_date(
            fields=["field_a", "field_b"],
            year=2025,
            mmdd=101,
        )

    assert result.ok is True
    assert result.data["query_meta"]["query_kind"] == "transaction.market_transaction_data_by_date"
    assert result.data["replay_source"]["fixture"] == "transaction-market-transaction-data-by-date-success"


def test_execute_sync_replay_rejects_malformed_custom_fixture_path(tmp_path: Path) -> None:
    fixture_path = tmp_path / "bad-runtime-capabilities.json"
    fixture_path.write_text(json.dumps(["bad"]), encoding="utf-8")

    result = execute_sync_replay(
        "runtime.capabilities",
        replay_fixture_path=str(fixture_path),
    )

    assert result.ok is False
    assert result.code.value == "invalid_request"
    assert "JSON object" in result.message


def test_materialize_subscription_watch_replay_rewrites_run_identity_for_directory_source(tmp_path: Path) -> None:
    source_dir = tmp_path / "source-run"
    source_dir.mkdir()
    source_manifest = load_provider_replay_fixture("subscription-watch-manifest")
    source_status = load_provider_replay_fixture("subscription-watch-status-completed")
    source_summary = load_provider_replay_fixture("subscription-watch-summary-completed")
    source_events = load_provider_replay_fixture("subscription-watch-events")

    (source_dir / "manifest.json").write_text(json.dumps(source_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (source_dir / "status.json").write_text(json.dumps(source_status, ensure_ascii=False, indent=2), encoding="utf-8")
    (source_dir / "summary.json").write_text(json.dumps(source_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (source_dir / "events.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in source_events) + "\n",
        encoding="utf-8",
    )

    paths = build_subscription_watch_run_paths(tmp_path / "materialized", run_id="run-002")
    materialized = materialize_subscription_watch_replay(
        paths=paths,
        replay_fixture_path=str(source_dir),
    )

    assert materialized.manifest["run_id"] == "run-002"
    assert materialized.manifest["provider_mode"] == "replay"
    assert materialized.status["run_id"] == "run-002"
    assert materialized.summary["run_id"] == "run-002"
    assert materialized.events[0]["run_id"] == "run-002"
    assert materialized.status["output_paths"]["run_dir"].endswith("run-002")
    assert materialized.summary["artifacts"]["events_jsonl_path"].endswith("run-002/events.jsonl")
    assert paths.manifest_path.exists()
    assert paths.status_path.exists()
    assert paths.summary_path.exists()
    assert paths.events_jsonl_path.exists()
    assert paths.events_csv_path.exists()
