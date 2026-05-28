from __future__ import annotations

import json
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tdxquant.provider_transport_replay import (
    ProviderTransportReplayConfig,
    ProviderTransportReplayHTTPServer,
    build_provider_transport_replay_status,
    check_provider_replay_lifecycle_statefile,
    load_provider_transport_replay_config,
    probe_provider_transport_replay_health,
    probe_provider_transport_replay_watch_events,
    probe_provider_transport_replay_watch_stream,
    probe_provider_transport_replay_watch_status,
)
from tdxquant.replay_fixtures import list_provider_replay_fixtures, load_provider_replay_fixture


class ProviderTransportReplayStatusTests(unittest.TestCase):
    def test_status_reports_replay_only_foreground_lifecycle_boundary(self) -> None:
        config = ProviderTransportReplayConfig(
            provider_id="provider-replay-a",
            bind_host="127.0.0.1",
            port=0,
            token="secret-token",
            master_allowlist=["127.0.0.1"],
            replay_fixture="market-snapshot-default",
        )

        status = build_provider_transport_replay_status(config)

        self.assertEqual(status["provider_id"], "provider-replay-a")
        self.assertEqual(status["transport_mode"], "replay_only")
        self.assertEqual(status["bind"]["host"], "127.0.0.1")
        self.assertEqual(status["bind"]["port"], 0)
        self.assertEqual(status["replay_source"]["fixture"], "market-snapshot-default")
        self.assertEqual(status["runtime"]["runtime_observed"], False)
        self.assertEqual(status["runtime"]["live_runtime_required"], False)
        self.assertEqual(status["runtime"]["live_market_session_supported"], False)
        self.assertEqual(status["runtime"]["health_probe"]["enabled"], False)
        self.assertEqual(status["runtime"]["health_probe"]["status"], "not_requested")
        self.assertEqual(status["runtime"]["watch_status_probe"]["enabled"], False)
        self.assertEqual(status["runtime"]["watch_status_probe"]["status"], "not_requested")
        self.assertEqual(status["runtime"]["watch_events_probe"]["enabled"], False)
        self.assertEqual(status["runtime"]["watch_events_probe"]["status"], "not_requested")
        self.assertEqual(status["runtime"]["watch_stream_probe"]["enabled"], False)
        self.assertEqual(status["runtime"]["watch_stream_probe"]["status"], "not_requested")
        self.assertEqual(status["runtime"]["probe_summary"]["status"], "not_requested")
        self.assertEqual(status["runtime"]["probe_summary"]["request_coverage_status"], "none")
        self.assertEqual(status["runtime"]["probe_summary"]["total_count"], 4)
        self.assertEqual(status["runtime"]["probe_summary"]["requested_count"], 0)
        self.assertEqual(status["runtime"]["probe_summary"]["has_requested_probe"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["healthy_count"], 0)
        self.assertEqual(status["runtime"]["probe_summary"]["has_healthy_probe"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["has_not_requested_probe"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["all_probes_requested"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["failed_count"], 0)
        self.assertEqual(status["runtime"]["probe_summary"]["has_failed_probe"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["has_unhealthy_probe"], False)
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_requested_probe"])
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_healthy_probe"])
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_failed_probe"])
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_unhealthy_probe"])
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_problem_probe"])
        self.assertEqual(status["runtime"]["probe_summary"]["has_problem_probe"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["primary_not_requested_probe"], "health_probe")
        self.assertEqual(status["runtime"]["probe_summary"]["unhealthy_count"], 0)
        self.assertEqual(status["runtime"]["probe_summary"]["not_requested_count"], 4)
        self.assertEqual(
            status["runtime"]["probe_summary"]["request_summary"],
            {
                "status": status["runtime"]["probe_summary"]["request_coverage_status"],
                "total_count": status["runtime"]["probe_summary"]["total_count"],
                "requested_count": status["runtime"]["probe_summary"]["requested_count"],
                "not_requested_count": status["runtime"]["probe_summary"]["not_requested_count"],
                "healthy_count": status["runtime"]["probe_summary"]["healthy_count"],
                "failed_count": status["runtime"]["probe_summary"]["failed_count"],
                "unhealthy_count": status["runtime"]["probe_summary"]["unhealthy_count"],
                "primary_requested_probe": status["runtime"]["probe_summary"]["primary_requested_probe"],
                "primary_not_requested_probe": status["runtime"]["probe_summary"][
                    "primary_not_requested_probe"
                ],
            },
        )
        self.assertEqual(
            status["runtime"]["probe_summary"]["health_summary"],
            {
                "status": status["runtime"]["probe_summary"]["status"],
                "healthy_count": status["runtime"]["probe_summary"]["healthy_count"],
                "failed_count": status["runtime"]["probe_summary"]["failed_count"],
                "unhealthy_count": status["runtime"]["probe_summary"]["unhealthy_count"],
                "has_healthy_probe": status["runtime"]["probe_summary"]["has_healthy_probe"],
                "has_failed_probe": status["runtime"]["probe_summary"]["has_failed_probe"],
                "has_unhealthy_probe": status["runtime"]["probe_summary"]["has_unhealthy_probe"],
                "status_key_count": status["runtime"]["probe_summary"]["status_key_count"],
                "primary_healthy_probe": status["runtime"]["probe_summary"]["primary_healthy_probe"],
                "primary_failed_probe": status["runtime"]["probe_summary"]["primary_failed_probe"],
                "primary_unhealthy_probe": status["runtime"]["probe_summary"]["primary_unhealthy_probe"],
            },
        )
        self.assertEqual(
            status["runtime"]["probe_summary"]["outcome_summary"],
            {
                "status": "not_requested",
                "request_coverage_status": "none",
                "total_count": 4,
                "requested_count": 0,
                "healthy_count": 0,
                "failed_count": 0,
                "unhealthy_count": 0,
                "not_requested_count": 4,
                "all_probes_requested": False,
                "has_failed_probe": False,
                "has_unhealthy_probe": False,
                "primary_problem_probe": None,
                "primary_error_sample_probe": None,
                "primary_error_sample_status": None,
            },
        )
        self.assertEqual(
            status["runtime"]["probe_summary"]["advisory_summary"],
            {
                "status": "not_requested",
                "request_coverage_status": "none",
                "total_count": 4,
                "requested_count": 0,
                "healthy_count": 0,
                "failed_count": 0,
                "unhealthy_count": 0,
                "has_requested_probe": False,
                "has_healthy_probe": False,
                "has_failed_probe": False,
                "has_unhealthy_probe": False,
                "has_problem_probe": False,
                "primary_problem_probe": None,
                "primary_error_sample_probe": None,
                "boundary": "read_only_probe_summary",
            },
        )
        self.assertEqual(status["runtime"]["probe_summary"]["status_counts"], {"not_requested": 4})
        self.assertEqual(
            status["runtime"]["probe_summary"]["status_key_count"],
            len(status["runtime"]["probe_summary"]["status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["requested_status_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["requested_status_key_count"],
            len(status["runtime"]["probe_summary"]["requested_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["failed_status_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["failed_status_key_count"],
            len(status["runtime"]["probe_summary"]["failed_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["requested_reachability_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["requested_reachability_key_count"],
            len(status["runtime"]["probe_summary"]["requested_reachability_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["healthy_reachability_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["healthy_reachability_key_count"],
            len(status["runtime"]["probe_summary"]["healthy_reachability_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["failed_reachability_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["failed_reachability_key_count"],
            len(status["runtime"]["probe_summary"]["failed_reachability_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["requested_http_status_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["requested_http_status_key_count"],
            len(status["runtime"]["probe_summary"]["requested_http_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["healthy_http_status_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["healthy_http_status_key_count"],
            len(status["runtime"]["probe_summary"]["healthy_http_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["failed_http_status_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["failed_http_status_key_count"],
            len(status["runtime"]["probe_summary"]["failed_http_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["error_code_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_code_key_count"],
            len(status["runtime"]["probe_summary"]["error_code_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["failed_error_code_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["failed_error_code_key_count"],
            len(status["runtime"]["probe_summary"]["failed_error_code_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["error_samples"], [])
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_error_sample_probe"])
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_error_sample_status"])
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_error_sample_error_code"])
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_error_sample_http_status"])
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_error_sample_reachability"])
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_count"], 0)
        self.assertEqual(status["runtime"]["probe_summary"]["has_error_sample"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_status_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_sample_status_key_count"],
            len(status["runtime"]["probe_summary"]["error_sample_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_probe_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_sample_probe_key_count"],
            len(status["runtime"]["probe_summary"]["error_sample_probe_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_http_status_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_sample_http_status_key_count"],
            len(status["runtime"]["probe_summary"]["error_sample_http_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_reachability_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_sample_reachability_key_count"],
            len(status["runtime"]["probe_summary"]["error_sample_reachability_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_visible_count"], 0)
        self.assertEqual(status["runtime"]["probe_summary"]["has_visible_error_sample"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_hidden_count"], 0)
        self.assertEqual(status["runtime"]["probe_summary"]["has_hidden_error_sample"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_limit"], 3)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_truncated"], False)
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_sample_summary"],
            {
                "count": 0,
                "visible_count": 0,
                "hidden_count": 0,
                "limit": 3,
                "truncated": False,
                "primary_probe": None,
                "primary_status": None,
                "primary_error_code": None,
                "primary_http_status": None,
                "primary_reachability": None,
            },
        )
        self.assertEqual(status["runtime"]["probe_summary"]["requested"], [])
        self.assertEqual(status["runtime"]["probe_summary"]["healthy"], [])
        self.assertEqual(status["runtime"]["probe_summary"]["unhealthy"], [])
        self.assertEqual(status["runtime"]["probe_summary"]["failed"], [])
        self.assertEqual(
            status["runtime"]["probe_summary"]["not_requested"],
            ["health_probe", "watch_status_probe", "watch_events_probe", "watch_stream_probe"],
        )
        self.assertEqual(
            status["runtime"]["probe_summary"]["boundary"],
            "read_only_probe_rollup; does_not_start_socket_or_manage_daemon_lifecycle",
        )
        self.assertEqual(status["lifecycle"]["mode"], "foreground_process")
        self.assertEqual(status["lifecycle"]["start_stop_managed"], False)
        self.assertEqual(status["lifecycle"]["daemon_managed"], False)
        self.assertEqual(status["lifecycle"]["restart_policy"], "not_managed")
        self.assertEqual(
            status["lifecycle"]["ownership_summary"],
            {
                "ownership_status": "not_managed",
                "owned_process": False,
                "state_file_present": False,
                "state_file_stale": False,
                "control_allowed": False,
                "status_source": "configured_boundary",
                "boundary": "no_lifecycle_ownership; read_only_status",
            },
        )
        self.assertEqual(
            status["lifecycle"]["control_summary"],
            {
                "control_status": "unsupported",
                "control_allowed": False,
                "available_operations": [],
                "blocked_operations": ["start", "stop", "restart", "backoff"],
                "blocking_reason": "lifecycle_control_not_implemented",
                "ownership_required": True,
                "operator_action_required": True,
                "boundary": "read_only_lifecycle_status; no_control_operations",
            },
        )
        self.assertEqual(
            status["lifecycle"]["operation_summary"],
            {
                "operation_count": 4,
                "available_count": 0,
                "blocked_count": 4,
                "operations": [
                    {
                        "operation": "start",
                        "status": "blocked",
                        "blocking_reason": "lifecycle_control_not_implemented",
                        "ownership_required": False,
                        "operator_action_required": True,
                        "implemented": False,
                    },
                    {
                        "operation": "stop",
                        "status": "blocked",
                        "blocking_reason": "lifecycle_control_not_implemented",
                        "ownership_required": True,
                        "operator_action_required": True,
                        "implemented": False,
                    },
                    {
                        "operation": "restart",
                        "status": "blocked",
                        "blocking_reason": "lifecycle_control_not_implemented",
                        "ownership_required": True,
                        "operator_action_required": True,
                        "implemented": False,
                    },
                    {
                        "operation": "backoff",
                        "status": "blocked",
                        "blocking_reason": "lifecycle_control_not_implemented",
                        "ownership_required": True,
                        "operator_action_required": True,
                        "implemented": False,
                    },
                ],
            },
        )
        self.assertEqual(
            status["lifecycle"]["backoff_summary"],
            {
                "backoff_status": "not_configured",
                "enabled": False,
                "policy": "not_managed",
                "retry_count": 0,
                "delay_window_seconds": None,
                "last_failure_reason": None,
                "next_retry_status": "not_scheduled",
                "next_retry_pending": False,
                "blocked": True,
                "blocking_reason": "lifecycle_control_not_implemented",
                "boundary": "read_only_backoff_status; no_supervised_restart",
            },
        )
        self.assertEqual(
            status["lifecycle"]["supervision_summary"],
            {
                "supervision_status": "not_supervised",
                "supervisor_configured": False,
                "supervisor_type": "none",
                "managed_process_count": 0,
                "active_process_count": 0,
                "desired_state": "unmanaged",
                "observed_state": "not_observed",
                "process_identity_status": "not_tracked",
                "state_file_status": "not_configured",
                "pid_status": "not_tracked",
                "control_allowed": False,
                "blocked": True,
                "blocking_reason": "lifecycle_control_not_implemented",
                "boundary": "read_only_supervision_status; no_supervisor_loop",
            },
        )
        self.assertEqual(
            status["lifecycle"]["statefile_summary"],
            {
                "statefile_status": "not_configured",
                "configured": False,
                "path_provided": False,
                "read_attempted": False,
                "write_attempted": False,
                "present": None,
                "stale": None,
                "ownership_source": "not_available",
                "control_allowed": False,
                "blocked": True,
                "blocking_reason": "lifecycle_control_not_implemented",
                "boundary": "read_only_statefile_config_boundary; no_statefile_io",
            },
        )
        self.assertEqual(status["capabilities"]["read_only"], True)
        self.assertEqual(status["capabilities"]["writes_supported"], False)
        self.assertIn("/provider/v1/replay/watch/events/stream", status["capabilities"]["endpoints"])
        self.assertIn("no daemon start/stop lifecycle management", status["boundaries"])

    def test_configured_lifecycle_statefile_is_reported_without_filesystem_io(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = f"{temp_dir}/provider-replay.json"
            lifecycle_state_file = f"{temp_dir}/provider-replay.state.json"
            with open(config_path, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "provider_id": "provider-replay-a",
                        "bind_host": "127.0.0.1",
                        "port": 0,
                        "token": "secret-token",
                        "master_allowlist": ["127.0.0.1"],
                        "replay_fixture": "market-snapshot-default",
                        "lifecycle_state_file": lifecycle_state_file,
                    },
                    fh,
                )

            config = load_provider_transport_replay_config(config_path)
            status = build_provider_transport_replay_status(config)

            self.assertEqual(config.lifecycle_state_file, lifecycle_state_file)
            self.assertEqual(
                status["lifecycle"]["statefile_summary"],
                {
                    "statefile_status": "configured_not_inspected",
                    "configured": True,
                    "path_provided": True,
                    "read_attempted": False,
                    "write_attempted": False,
                    "present": None,
                    "stale": None,
                    "ownership_source": "not_available",
                    "control_allowed": False,
                    "blocked": True,
                    "blocking_reason": "lifecycle_control_not_implemented",
                    "boundary": "read_only_statefile_config_boundary; no_statefile_io",
                },
            )
            self.assertFalse(Path(lifecycle_state_file).exists())

    def test_lifecycle_statefile_check_reports_valid_stale_state(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "provider-replay.state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "schema_version": "tdx.provider_replay.lifecycle_state.v1",
                        "provider_id": "provider-replay-a",
                        "pid": 12345,
                        "state": "running",
                        "updated_at": "2000-01-01T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            config = ProviderTransportReplayConfig(
                provider_id="provider-replay-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=[],
                replay_fixture="market-snapshot-default",
                lifecycle_state_file=str(state_path),
            )

            result = check_provider_replay_lifecycle_statefile(config, stale_after_seconds=60)

        self.assertEqual(result["check_status"], "valid")
        self.assertEqual(result["configured"], True)
        self.assertEqual(result["read_attempted"], True)
        self.assertEqual(result["write_attempted"], False)
        self.assertEqual(result["exists"], True)
        self.assertEqual(result["schema_version"], "tdx.provider_replay.lifecycle_state.v1")
        self.assertEqual(result["schema_valid"], True)
        self.assertEqual(result["provider_id"], "provider-replay-a")
        self.assertEqual(result["provider_id_matches"], True)
        self.assertEqual(result["pid"], 12345)
        self.assertEqual(result["state"], "running")
        self.assertEqual(result["updated_at"], "2000-01-01T00:00:00Z")
        self.assertEqual(result["stale_after_seconds"], 60)
        self.assertEqual(result["stale"], True)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["error_count"], 0)
        self.assertEqual(result["control_allowed"], False)
        self.assertEqual(result["boundary"], "read_only_statefile_check; no_lifecycle_control")

    def test_lifecycle_statefile_check_reports_missing_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "missing.state.json"
            config = ProviderTransportReplayConfig(
                provider_id="provider-replay-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=[],
                replay_fixture="market-snapshot-default",
                lifecycle_state_file=str(state_path),
            )

            result = check_provider_replay_lifecycle_statefile(config, stale_after_seconds=60)

        self.assertEqual(result["check_status"], "missing")
        self.assertEqual(result["configured"], True)
        self.assertEqual(result["read_attempted"], True)
        self.assertEqual(result["write_attempted"], False)
        self.assertEqual(result["exists"], False)
        self.assertEqual(result["schema_valid"], None)
        self.assertEqual(result["control_allowed"], False)

    def test_lifecycle_statefile_check_reports_not_configured_without_read(self) -> None:
        config = ProviderTransportReplayConfig(
            provider_id="provider-replay-a",
            bind_host="127.0.0.1",
            port=0,
            token="secret-token",
            master_allowlist=[],
            replay_fixture="market-snapshot-default",
        )

        result = check_provider_replay_lifecycle_statefile(config, stale_after_seconds=60)

        self.assertEqual(result["check_status"], "not_configured")
        self.assertEqual(result["configured"], False)
        self.assertEqual(result["read_attempted"], False)
        self.assertEqual(result["write_attempted"], False)
        self.assertIsNone(result["exists"])
        self.assertEqual(result["control_allowed"], False)

    def test_status_can_include_explicit_replay_health_probe(self) -> None:
        server = ProviderTransportReplayHTTPServer(
            ProviderTransportReplayConfig(
                provider_id="provider-replay-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
            )
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            probe_config = ProviderTransportReplayConfig(
                provider_id="provider-replay-a",
                bind_host="127.0.0.1",
                port=server.server_address[1],
                token="secret-token",
                master_allowlist=["127.0.0.1"],
            )
            probe = probe_provider_transport_replay_health(probe_config, timeout_seconds=1.5)
            status = build_provider_transport_replay_status(probe_config, health_probe=probe)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(probe["status"], "healthy")
        self.assertEqual(probe["http_status"], 200)
        self.assertEqual(probe["reachable"], True)
        self.assertEqual(probe["timeout_seconds"], 1.5)
        self.assertNotIn("secret-token", json.dumps(status))
        self.assertEqual(status["runtime"]["runtime_observed"], True)
        self.assertEqual(status["runtime"]["health_probe"]["status"], "healthy")
        self.assertEqual(status["runtime"]["health_probe"]["service"], "provider-transport-replay")
        self.assertEqual(status["runtime"]["probe_summary"]["status"], "healthy")
        self.assertEqual(status["runtime"]["probe_summary"]["request_coverage_status"], "partial")
        self.assertEqual(status["runtime"]["probe_summary"]["total_count"], 4)
        self.assertEqual(status["runtime"]["probe_summary"]["requested_count"], 1)
        self.assertEqual(status["runtime"]["probe_summary"]["healthy_count"], 1)
        self.assertEqual(status["runtime"]["probe_summary"]["failed_count"], 0)
        self.assertEqual(status["runtime"]["probe_summary"]["primary_requested_probe"], "health_probe")
        self.assertEqual(status["runtime"]["probe_summary"]["primary_healthy_probe"], "health_probe")
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_failed_probe"])
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_unhealthy_probe"])
        self.assertEqual(status["runtime"]["probe_summary"]["primary_not_requested_probe"], "watch_status_probe")
        self.assertEqual(status["runtime"]["probe_summary"]["unhealthy_count"], 0)
        self.assertEqual(status["runtime"]["probe_summary"]["not_requested_count"], 3)
        self.assertEqual(status["runtime"]["probe_summary"]["status_counts"], {"healthy": 1, "not_requested": 3})
        self.assertEqual(
            status["runtime"]["probe_summary"]["status_key_count"],
            len(status["runtime"]["probe_summary"]["status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["requested_status_counts"], {"healthy": 1})
        self.assertEqual(
            status["runtime"]["probe_summary"]["requested_status_key_count"],
            len(status["runtime"]["probe_summary"]["requested_status_counts"]),
        )
        self.assertEqual(
            status["runtime"]["probe_summary"]["failed_status_key_count"],
            len(status["runtime"]["probe_summary"]["failed_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["requested_reachability_counts"], {"reachable": 1})
        self.assertEqual(
            status["runtime"]["probe_summary"]["requested_reachability_key_count"],
            len(status["runtime"]["probe_summary"]["requested_reachability_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["healthy_reachability_counts"], {"reachable": 1})
        self.assertEqual(
            status["runtime"]["probe_summary"]["healthy_reachability_key_count"],
            len(status["runtime"]["probe_summary"]["healthy_reachability_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["failed_reachability_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["failed_reachability_key_count"],
            len(status["runtime"]["probe_summary"]["failed_reachability_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["requested_http_status_counts"], {"200": 1})
        self.assertEqual(
            status["runtime"]["probe_summary"]["requested_http_status_key_count"],
            len(status["runtime"]["probe_summary"]["requested_http_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["healthy_http_status_counts"], {"200": 1})
        self.assertEqual(
            status["runtime"]["probe_summary"]["healthy_http_status_key_count"],
            len(status["runtime"]["probe_summary"]["healthy_http_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["failed_http_status_counts"], {})
        self.assertEqual(
            status["runtime"]["probe_summary"]["failed_http_status_key_count"],
            len(status["runtime"]["probe_summary"]["failed_http_status_counts"]),
        )
        self.assertEqual(status["runtime"]["probe_summary"]["requested"], ["health_probe"])
        self.assertEqual(status["runtime"]["probe_summary"]["healthy"], ["health_probe"])
        self.assertEqual(status["runtime"]["probe_summary"]["unhealthy"], [])
        self.assertEqual(status["runtime"]["probe_summary"]["failed"], [])
        self.assertEqual(status["lifecycle"]["start_stop_managed"], False)
        self.assertEqual(status["lifecycle"]["daemon_managed"], False)

    def test_status_summarizes_degraded_replay_probe(self) -> None:
        config = ProviderTransportReplayConfig(
            provider_id="provider-replay-a",
            bind_host="127.0.0.1",
            port=0,
            token="secret-token",
            master_allowlist=["127.0.0.1"],
        )

        status = build_provider_transport_replay_status(
            config,
            health_probe={
                "status": "unhealthy",
                "reachable": False,
                "http_status": 503,
                "error_code": "connection_failed",
                "error": {"code": "connection_failed", "message": "connection refused"},
            },
        )

        self.assertNotIn("secret-token", json.dumps(status))
        self.assertEqual(status["runtime"]["runtime_observed"], True)
        self.assertEqual(status["runtime"]["health_probe"]["enabled"], True)
        self.assertEqual(status["runtime"]["health_probe"]["status"], "unhealthy")
        self.assertEqual(status["runtime"]["probe_summary"]["status"], "degraded")
        self.assertEqual(status["runtime"]["probe_summary"]["total_count"], 4)
        self.assertEqual(status["runtime"]["probe_summary"]["requested_count"], 1)
        self.assertEqual(status["runtime"]["probe_summary"]["healthy_count"], 0)
        self.assertEqual(status["runtime"]["probe_summary"]["has_healthy_probe"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["failed_count"], 1)
        self.assertEqual(status["runtime"]["probe_summary"]["unhealthy_count"], 1)
        self.assertEqual(status["runtime"]["probe_summary"]["primary_requested_probe"], "health_probe")
        self.assertEqual(status["runtime"]["probe_summary"]["has_requested_probe"], True)
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_healthy_probe"])
        self.assertEqual(status["runtime"]["probe_summary"]["not_requested_count"], 3)
        self.assertEqual(status["runtime"]["probe_summary"]["has_not_requested_probe"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["all_probes_requested"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["has_failed_probe"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["has_unhealthy_probe"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["has_problem_probe"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["health_summary"]["has_healthy_probe"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["health_summary"]["has_failed_probe"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["health_summary"]["has_unhealthy_probe"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["status_counts"], {"not_requested": 3, "unhealthy": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["requested_status_counts"], {"unhealthy": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["failed_status_counts"], {"unhealthy": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["requested_reachability_counts"], {"unreachable": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["healthy_reachability_counts"], {})
        self.assertEqual(status["runtime"]["probe_summary"]["failed_reachability_counts"], {"unreachable": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["requested_http_status_counts"], {"503": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["healthy_http_status_counts"], {})
        self.assertEqual(status["runtime"]["probe_summary"]["failed_http_status_counts"], {"503": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["failed"], ["health_probe"])
        self.assertEqual(status["runtime"]["probe_summary"]["primary_failed_probe"], "health_probe")
        self.assertEqual(status["runtime"]["probe_summary"]["primary_unhealthy_probe"], "health_probe")
        self.assertEqual(status["runtime"]["probe_summary"]["primary_problem_probe"], "health_probe")
        self.assertEqual(
            status["runtime"]["probe_summary"]["advisory_summary"],
            {
                "status": "degraded",
                "request_coverage_status": "partial",
                "total_count": 4,
                "requested_count": 1,
                "healthy_count": 0,
                "failed_count": 1,
                "unhealthy_count": 1,
                "has_requested_probe": True,
                "has_healthy_probe": False,
                "has_failed_probe": True,
                "has_unhealthy_probe": True,
                "has_problem_probe": True,
                "primary_problem_probe": "health_probe",
                "primary_error_sample_probe": "health_probe",
                "boundary": "read_only_probe_summary",
            },
        )
        self.assertEqual(status["runtime"]["probe_summary"]["error_code_counts"], {"connection_failed": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["failed_error_code_counts"], {"connection_failed": 1})
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_samples"],
            [
                {
                    "probe": "health_probe",
                    "status": "unhealthy",
                    "error_code": "connection_failed",
                    "http_status": 503,
                }
            ],
        )
        self.assertEqual(status["runtime"]["probe_summary"]["primary_error_sample_probe"], "health_probe")
        self.assertEqual(status["runtime"]["probe_summary"]["primary_error_sample_status"], "unhealthy")
        self.assertEqual(status["runtime"]["probe_summary"]["primary_error_sample_error_code"], "connection_failed")
        self.assertEqual(status["runtime"]["probe_summary"]["primary_error_sample_http_status"], 503)
        self.assertEqual(status["runtime"]["probe_summary"]["primary_error_sample_reachability"], "unreachable")
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_count"], 1)
        self.assertEqual(status["runtime"]["probe_summary"]["has_error_sample"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_status_counts"], {"unhealthy": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_probe_counts"], {"health_probe": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_http_status_counts"], {"503": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_http_status_key_count"], 1)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_reachability_counts"], {"unreachable": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_reachability_key_count"], 1)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_limit"], 3)
        self.assertEqual(status["runtime"]["probe_summary"]["has_visible_error_sample"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_truncated"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["has_hidden_error_sample"], False)
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_sample_summary"],
            {
                "count": 1,
                "visible_count": 1,
                "hidden_count": 0,
                "limit": 3,
                "truncated": False,
                "primary_probe": "health_probe",
                "primary_status": "unhealthy",
                "primary_error_code": "connection_failed",
                "primary_http_status": 503,
                "primary_reachability": "unreachable",
            },
        )
        self.assertEqual(
            status["runtime"]["probe_summary"]["outcome_summary"],
            {
                "status": "degraded",
                "request_coverage_status": "partial",
                "total_count": 4,
                "requested_count": 1,
                "healthy_count": 0,
                "failed_count": 1,
                "unhealthy_count": 1,
                "not_requested_count": 3,
                "all_probes_requested": False,
                "has_failed_probe": True,
                "has_unhealthy_probe": True,
                "primary_problem_probe": "health_probe",
                "primary_error_sample_probe": "health_probe",
                "primary_error_sample_status": "unhealthy",
            },
        )
        self.assertEqual(status["runtime"]["probe_summary"]["requested"], ["health_probe"])
        self.assertEqual(status["runtime"]["probe_summary"]["healthy"], [])
        self.assertEqual(status["runtime"]["probe_summary"]["unhealthy"], ["health_probe"])
        self.assertEqual(status["runtime"]["probe_summary"]["primary_not_requested_probe"], "watch_status_probe")
        self.assertEqual(
            status["runtime"]["probe_summary"]["not_requested"],
            ["watch_status_probe", "watch_events_probe", "watch_stream_probe"],
        )
        self.assertEqual(status["lifecycle"]["start_stop_managed"], False)
        self.assertEqual(status["lifecycle"]["daemon_managed"], False)

    def test_status_counts_all_probe_error_sample_candidates(self) -> None:
        config = ProviderTransportReplayConfig(
            provider_id="provider-replay-a",
            bind_host="127.0.0.1",
            port=0,
            token="secret-token",
            master_allowlist=["127.0.0.1"],
        )

        status = build_provider_transport_replay_status(
            config,
            health_probe={
                "status": "healthy",
                "reachable": True,
                "http_status": 200,
                "error_code": "health_warning",
            },
            watch_status_probe={
                "status": "unhealthy",
                "reachable": False,
                "error_code": "watch_status_failed",
            },
            watch_events_probe={
                "status": "unhealthy",
                "reachable": False,
                "error_code": "watch_events_failed",
            },
            watch_stream_probe={
                "status": "unhealthy",
                "reachable": False,
                "error_code": "watch_stream_failed",
            },
        )

        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_count"], 4)
        self.assertEqual(status["runtime"]["probe_summary"]["request_coverage_status"], "complete")
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_sample_status_counts"],
            {"healthy": 1, "unhealthy": 3},
        )
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_sample_probe_counts"],
            {
                "health_probe": 1,
                "watch_events_probe": 1,
                "watch_status_probe": 1,
                "watch_stream_probe": 1,
            },
        )
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_http_status_counts"], {"200": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_http_status_key_count"], 1)
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_sample_reachability_counts"],
            {"reachable": 1, "unreachable": 3},
        )
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_reachability_key_count"], 2)
        self.assertEqual(status["runtime"]["probe_summary"]["failed_status_counts"], {"unhealthy": 3})
        self.assertEqual(status["runtime"]["probe_summary"]["healthy_reachability_counts"], {"reachable": 1})
        self.assertEqual(status["runtime"]["probe_summary"]["failed_reachability_counts"], {"unreachable": 3})
        self.assertEqual(
            status["runtime"]["probe_summary"]["primary_requested_probe"],
            status["runtime"]["probe_summary"]["requested"][0],
        )
        self.assertEqual(status["runtime"]["probe_summary"]["primary_error_sample_reachability"], "reachable")
        self.assertEqual(
            status["runtime"]["probe_summary"]["primary_failed_probe"],
            status["runtime"]["probe_summary"]["failed"][0],
        )
        self.assertEqual(
            status["runtime"]["probe_summary"]["primary_healthy_probe"],
            status["runtime"]["probe_summary"]["healthy"][0],
        )
        self.assertEqual(status["runtime"]["probe_summary"]["has_healthy_probe"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["has_requested_probe"], True)
        self.assertIsNone(status["runtime"]["probe_summary"]["primary_not_requested_probe"])
        self.assertEqual(status["runtime"]["probe_summary"]["has_not_requested_probe"], False)
        self.assertEqual(status["runtime"]["probe_summary"]["all_probes_requested"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["has_failed_probe"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["has_unhealthy_probe"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["has_problem_probe"], True)
        self.assertEqual(len(status["runtime"]["probe_summary"]["error_samples"]), 3)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_visible_count"], 3)
        self.assertEqual(status["runtime"]["probe_summary"]["has_visible_error_sample"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_limit"], 3)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_hidden_count"], 1)
        self.assertEqual(status["runtime"]["probe_summary"]["error_sample_truncated"], True)
        self.assertEqual(status["runtime"]["probe_summary"]["has_hidden_error_sample"], True)
        self.assertEqual(
            status["runtime"]["probe_summary"]["error_sample_summary"],
            {
                "count": 4,
                "visible_count": 3,
                "hidden_count": 1,
                "limit": 3,
                "truncated": True,
                "primary_probe": "health_probe",
                "primary_status": "healthy",
                "primary_error_code": "health_warning",
                "primary_http_status": 200,
                "primary_reachability": "reachable",
            },
        )
        self.assertEqual(status["lifecycle"]["start_stop_managed"], False)
        self.assertEqual(status["lifecycle"]["daemon_managed"], False)

    def test_status_can_include_explicit_replay_watch_status_probe(self) -> None:
        server = ProviderTransportReplayHTTPServer(
            ProviderTransportReplayConfig(
                provider_id="provider-replay-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
            )
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            probe_config = ProviderTransportReplayConfig(
                provider_id="provider-replay-a",
                bind_host="127.0.0.1",
                port=server.server_address[1],
                token="secret-token",
                master_allowlist=["127.0.0.1"],
            )
            probe = probe_provider_transport_replay_watch_status(probe_config, timeout_seconds=1.5)
            status = build_provider_transport_replay_status(probe_config, watch_status_probe=probe)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(probe["status"], "healthy")
        self.assertEqual(probe["endpoint"], "/provider/v1/replay/watch/status")
        self.assertEqual(probe["http_status"], 200)
        self.assertEqual(probe["reachable"], True)
        self.assertEqual(probe["timeout_seconds"], 1.5)
        self.assertNotIn("secret-token", json.dumps(status))
        self.assertEqual(status["runtime"]["runtime_observed"], True)
        self.assertEqual(status["runtime"]["watch_status_probe"]["status"], "healthy")
        self.assertEqual(status["runtime"]["watch_status_probe"]["endpoint"], "/provider/v1/replay/watch/status")
        self.assertEqual(status["lifecycle"]["start_stop_managed"], False)
        self.assertEqual(status["lifecycle"]["daemon_managed"], False)

    def test_status_can_include_explicit_replay_watch_events_probe(self) -> None:
        server = ProviderTransportReplayHTTPServer(
            ProviderTransportReplayConfig(
                provider_id="provider-replay-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
            )
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            probe_config = ProviderTransportReplayConfig(
                provider_id="provider-replay-a",
                bind_host="127.0.0.1",
                port=server.server_address[1],
                token="secret-token",
                master_allowlist=["127.0.0.1"],
            )
            probe = probe_provider_transport_replay_watch_events(probe_config, timeout_seconds=1.5)
            status = build_provider_transport_replay_status(probe_config, watch_events_probe=probe)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(probe["status"], "healthy")
        self.assertEqual(probe["endpoint"], "/provider/v1/replay/watch/events")
        self.assertEqual(probe["http_status"], 200)
        self.assertEqual(probe["reachable"], True)
        self.assertGreaterEqual(probe["event_count"], 0)
        self.assertNotIn("secret-token", json.dumps(status))
        self.assertEqual(status["runtime"]["runtime_observed"], True)
        self.assertEqual(status["runtime"]["watch_events_probe"]["status"], "healthy")
        self.assertEqual(status["runtime"]["watch_events_probe"]["endpoint"], "/provider/v1/replay/watch/events")
        self.assertEqual(status["lifecycle"]["start_stop_managed"], False)
        self.assertEqual(status["lifecycle"]["daemon_managed"], False)

    def test_status_can_include_explicit_replay_watch_stream_probe(self) -> None:
        server = ProviderTransportReplayHTTPServer(
            ProviderTransportReplayConfig(
                provider_id="provider-replay-a",
                bind_host="127.0.0.1",
                port=0,
                token="secret-token",
                master_allowlist=["127.0.0.1"],
            )
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            probe_config = ProviderTransportReplayConfig(
                provider_id="provider-replay-a",
                bind_host="127.0.0.1",
                port=server.server_address[1],
                token="secret-token",
                master_allowlist=["127.0.0.1"],
            )
            probe = probe_provider_transport_replay_watch_stream(probe_config, timeout_seconds=1.5)
            status = build_provider_transport_replay_status(probe_config, watch_stream_probe=probe)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(probe["status"], "healthy")
        self.assertEqual(probe["endpoint"], "/provider/v1/replay/watch/events/stream")
        self.assertEqual(probe["http_status"], 200)
        self.assertEqual(probe["reachable"], True)
        self.assertGreaterEqual(probe["frame_count"], 1)
        self.assertNotIn("secret-token", json.dumps(status))
        self.assertEqual(status["runtime"]["runtime_observed"], True)
        self.assertEqual(status["runtime"]["watch_stream_probe"]["status"], "healthy")
        self.assertEqual(status["runtime"]["watch_stream_probe"]["endpoint"], "/provider/v1/replay/watch/events/stream")
        self.assertEqual(status["lifecycle"]["start_stop_managed"], False)
        self.assertEqual(status["lifecycle"]["daemon_managed"], False)


class ProviderTransportReplayHTTPTests(unittest.TestCase):
    def _start_server(
        self,
        *,
        master_allowlist: list[str] | None = None,
    ) -> tuple[ProviderTransportReplayHTTPServer, str, threading.Thread]:
        config = ProviderTransportReplayConfig(
            provider_id="provider-replay-a",
            bind_host="127.0.0.1",
            port=0,
            token="secret-token",
            master_allowlist=master_allowlist if master_allowlist is not None else ["127.0.0.1"],
        )
        server = ProviderTransportReplayHTTPServer(config)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, f"http://127.0.0.1:{server.server_address[1]}", thread

    def _request_json(
        self,
        url: str,
        *,
        token: str | None = "secret-token",
    ) -> dict[str, object]:
        headers: dict[str, str] = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(url, headers=headers, method="GET")
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def _request_text(
        self,
        url: str,
        *,
        token: str | None = "secret-token",
    ) -> tuple[str, str]:
        headers: dict[str, str] = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(url, headers=headers, method="GET")
        with urlopen(request, timeout=5) as response:
            return response.headers.get_content_type(), response.read().decode("utf-8")

    @staticmethod
    def _parse_sse_payloads(raw: str) -> list[dict[str, object]]:
        payloads: list[dict[str, object]] = []
        for block in raw.strip().split("\n\n"):
            for line in block.splitlines():
                if line.startswith("data: "):
                    payloads.append(json.loads(line.removeprefix("data: ")))
        return payloads

    def test_health_requires_bearer_token(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            with self.assertRaises(HTTPError) as ctx:
                self._request_json(f"{base_url}/provider/v1/replay/health", token=None)
            payload = json.loads(ctx.exception.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(ctx.exception.code, 401)
        self.assertEqual(payload["error"]["code"], "UNAUTHORIZED")

    def test_health_rejects_disallowed_source_ip(self) -> None:
        server, base_url, thread = self._start_server(master_allowlist=["10.0.0.10"])
        try:
            with self.assertRaises(HTTPError) as ctx:
                self._request_json(f"{base_url}/provider/v1/replay/health")
            payload = json.loads(ctx.exception.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(ctx.exception.code, 403)
        self.assertEqual(payload["error"]["code"], "FORBIDDEN_SOURCE")

    def test_health_and_fixture_catalog_report_replay_only_transport(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            health = self._request_json(f"{base_url}/provider/v1/replay/health")
            catalog = self._request_json(f"{base_url}/provider/v1/replay/fixtures")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertTrue(health["ok"])
        self.assertEqual(health["meta"]["provider_mode"], "replay")
        self.assertEqual(health["result"]["status"], "ok")
        self.assertEqual(health["result"]["service"], "provider-transport-replay")

        names = {item["name"] for item in catalog["result"]["fixtures"]}
        self.assertIn("runtime-capabilities-success", names)
        delayed = next(item for item in catalog["result"]["fixtures"] if item["name"] == "subscription-watch-event-stream-delayed-playback")
        self.assertEqual(delayed["transport"], "sse")
        self.assertEqual(delayed["playback_mode"], "delayed")

    def test_sync_replay_result_endpoint_preserves_provider_contract(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            payload = self._request_json(f"{base_url}/provider/v1/replay/result?capability=runtime.capabilities")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        provider_result = payload["result"]["provider_result"]
        self.assertTrue(payload["ok"])
        self.assertEqual(provider_result["capability"], "runtime.capabilities")
        self.assertEqual(provider_result["runtime"]["mode"], "replay")
        self.assertEqual(provider_result["runtime"]["replay_source"]["mode"], "replay")
        self.assertIn("capabilities", provider_result["data"])

    def test_watch_status_and_events_are_served_from_replay_fixtures(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            status = self._request_json(f"{base_url}/provider/v1/replay/watch/status")
            events = self._request_json(f"{base_url}/provider/v1/replay/watch/events?tail=1")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(status["result"]["control"]["state"], "completed")
        self.assertFalse(status["result"]["control"]["active"])
        self.assertEqual(status["result"]["watch_status"]["state"], "completed")
        self.assertEqual(status["result"]["replay_source"]["mode"], "replay")

        self.assertEqual(events["result"]["run_id"], "20260501T080000000000Z")
        self.assertEqual(len(events["result"]["events"]), 1)
        self.assertEqual(events["result"]["events"][0]["sequence"], 2)
        self.assertEqual(events["result"]["events"][0]["symbol"], "000001.SZ")

    def test_watch_stream_serves_immediate_sse_frames_from_replay_fixtures(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            content_type, raw = self._request_text(f"{base_url}/provider/v1/replay/watch/events/stream")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(content_type, "text/event-stream")
        payloads = self._parse_sse_payloads(raw)
        frame_types = [item["frame_type"] for item in payloads]
        self.assertIn("status", frame_types)
        self.assertIn("quote", frame_types)
        self.assertEqual(payloads[0]["provider_mode"], "replay")
        self.assertEqual(payloads[0]["playback"]["mode"], "immediate")

    def test_watch_stream_delayed_playback_adds_deterministic_offsets(self) -> None:
        server, base_url, thread = self._start_server()
        try:
            _content_type, raw = self._request_text(
                f"{base_url}/provider/v1/replay/watch/events/stream?playback=delayed&delay_ms=250"
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        payloads = self._parse_sse_payloads(raw)
        quote_frames = [item for item in payloads if item["frame_type"] == "quote"]
        self.assertGreaterEqual(len(quote_frames), 2)
        self.assertEqual(quote_frames[0]["playback"]["mode"], "delayed")
        self.assertEqual(quote_frames[0]["playback"]["delay_ms"], 250)
        self.assertEqual(quote_frames[0]["playback"]["planned_emit_after_ms"], 250)
        self.assertEqual(quote_frames[1]["playback"]["planned_emit_after_ms"], 500)


class ProviderTransportReplayFixtureTests(unittest.TestCase):
    def test_delayed_playback_fixture_is_cataloged_and_loadable(self) -> None:
        fixtures = list_provider_replay_fixtures()
        delayed = next(item for item in fixtures if item["name"] == "subscription-watch-event-stream-delayed-playback")

        payload = load_provider_replay_fixture("subscription-watch-event-stream-delayed-playback")

        self.assertEqual(delayed["transport"], "sse")
        self.assertEqual(delayed["playback_mode"], "delayed")
        self.assertIsInstance(payload, list)
        quote_frames = [item for item in payload if item["frame_type"] == "quote"]
        self.assertGreaterEqual(len(quote_frames), 2)
        self.assertEqual(quote_frames[0]["playback"]["planned_emit_after_ms"], 250)
