## 1. Spec

- [x] 1.1 Update `tdx-task-management` for multi-method trade-audit filtering
- [x] 1.2 Update `tdx-report-cli-entry` for multi-method trade-audit CLI entrypoints and submit-path presets
- [x] 1.3 Update `tdx-command-catalog` for submit-path exception entries and bundles

## 2. Tests

- [x] 2.1 Add task-manager tests for multi-method trade-audit filtering and invalid mixed filters
- [x] 2.2 Add CLI tests for multi-method parsing and dispatch
- [x] 2.3 Add runtime registry tests for submit-path presets and bundles

## 3. Implementation

- [x] 3.1 Add multi-method filtering support in `tdxquant/api/task.py`
- [x] 3.2 Add multi-method CLI arguments and dispatch in `tdxquant/cli.py`
- [x] 3.3 Add submit-path exception presets and bundles in runtime registry files

## 4. Docs and Validation

- [x] 4.1 Update audit contract, function map, roadmap, and catalog usage docs
- [x] 4.2 Validate focused and full tests
- [x] 4.3 Validate and archive the OpenSpec change
