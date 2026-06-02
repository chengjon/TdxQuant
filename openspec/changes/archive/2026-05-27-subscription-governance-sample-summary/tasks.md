## Implementation

- [x] Add focused HTTP summary-view test coverage for `governance.sample_summary`.
- [x] Add focused CLI summary-view test coverage for `governance.sample_summary`.
- [x] Implement additive sample metadata rollup in HTTP and CLI summary projections.
- [x] Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.
- [x] Run focused pytest, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change after implementation.

## Verification Notes

- Passed focused pytest:
  - `python -m pytest -q tests\test_bridge_http.py::BridgeRequestHandlerTests::test_watch_status_summary_view_projects_governance_rollup tests\test_api_cli.py::ReportCliDispatchTests::test_handle_bridge_watch_status_summary_view_projects_governance_rollup tests\test_subscription_watch_background.py::test_start_rejects_when_control_lock_is_held_by_other_process`
  - Result: `3 passed`
- Passed `openspec validate subscription-governance-sample-summary --strict`.
- Passed `scripts\validate_function_tree_registry.py --json`: `valid=true`, `row_count=64`, `problem_count=0`.
- Passed scoped `git diff --check` for the changed implementation, test, registry, and OpenSpec files; Git only reported expected Windows LF-to-CRLF warnings.
- A broader two-file pytest run for `tests\test_bridge_http.py tests\test_api_cli.py` was attempted after fixing the Windows `fcntl` import blocker, but was interrupted outside the sample-summary focused cases. The change-specific focused cases above passed.
