## Design

`_validate_catalog_registry()` already resolves selected bundles without executing them and identifies task/report bundle coverage by inspecting each resolved step's `source`. This change extends that same loop with a deterministic aggregate count:

- only bundles with both `task` and `report` step sources contribute to `task_report_bundle_step_source_counts`;
- each contributing resolved step increments its direct `source` value;
- output keys are sorted before returning so summary payloads remain stable.

`_build_catalog_summary_view()` copies the aggregate counts into validate summary payloads alongside the existing task/report bundle count, bounded samples, sample limit, and truncation flag. The summary remains an opt-in reduced projection and does not include detailed bundle rows.

## Boundaries

- This is a catalog metadata projection only.
- It does not execute selected bundles or their task/report/trade steps.
- It does not become a full workflow builder, full bundle inventory, or execution-readiness check.
- It does not change `catalog validate` detailed payload semantics except for the additive count field.

## Verification

- Add focused tests for detailed validation and summary validation.
- Run `python -m pytest tests/test_api_cli.py -q`.
- Run `openspec validate --all --strict`.
- Run `git diff --check`.
- Run `python scripts/validate_function_tree_registry.py`.
