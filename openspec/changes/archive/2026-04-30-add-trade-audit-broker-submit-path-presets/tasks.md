## 1. Runtime Registry

- [x] 1.1 Add broker-scoped trade-audit report presets for `audit-daily-pingan-submit-path-exceptions` and `audit-period-pingan-submit-path-exceptions`.
- [x] 1.2 Add command-catalog entries mapped to the new broker-scoped report presets.
- [x] 1.3 Add at least one broker-scoped diagnostics bundle and one confirm follow-up bundle built from existing entries.

## 2. Tests and Docs

- [x] 2.1 Extend runtime/context tests to lock the new broker-scoped preset, catalog, and bundle names plus the fixed `broker=pingan` defaults.
- [x] 2.2 Extend CLI preset coverage to prove `report run` forwards the broker-scoped submit-path defaults through the existing audit workflow.
- [x] 2.3 Update trade-audit and command-catalog docs to reflect the new broker-scoped submit-path entrypoints.

## 3. Validation

- [x] 3.1 Run focused and full `tests/test_api_manager.py` plus `tests/test_api_cli.py`.
- [x] 3.2 Run `openspec validate add-trade-audit-broker-submit-path-presets --type change --strict`.
