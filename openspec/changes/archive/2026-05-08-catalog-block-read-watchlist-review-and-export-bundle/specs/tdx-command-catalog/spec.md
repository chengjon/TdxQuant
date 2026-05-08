## ADDED Requirements

### Requirement: Command catalog SHALL expose block read review-and-export bundles once the preset-backed entries are stable
The system SHALL expose stable catalog bundles that compose preset-backed block read watchlist snapshot, diagnostics, and JSON export entries through the existing bundle workflow.

#### Scenario: Caller lists block read review-and-export bundles
- **WHEN** a caller lists catalog bundles after the stable `read-zxg-watchlist`, `read-zxg-full`, and `export-zxg-watchlist` task presets are available
- **THEN** the catalog MUST include a bundle named `read-zxg-review-and-export`

#### Scenario: Caller plans a block read review-and-export bundle
- **WHEN** a caller executes `catalog plan --bundle read-zxg-review-and-export`
- **THEN** the system MUST resolve exactly three steps through the existing preset-backed entry workflow without executing the steps

#### Scenario: Caller applies a top-level block code override to the review-and-export bundle
- **WHEN** a caller executes `catalog plan` or `catalog run` for `read-zxg-review-and-export` with `--block-code <value>`
- **THEN** the system MUST propagate that `block_code` override to `read-zxg-watchlist`, `read-zxg-full`, and `export-zxg-watchlist`

#### Scenario: Caller attempts unsupported export overrides on the review-and-export bundle
- **WHEN** a caller executes `catalog plan` or `catalog run` for `read-zxg-review-and-export` with bundle-level `--export-output` or `--overwrite`
- **THEN** the CLI MUST reject the request instead of treating those options as bundle-level overrides

#### Scenario: Caller runs a block read review-and-export bundle
- **WHEN** a caller executes `catalog run --bundle read-zxg-review-and-export`
- **THEN** the system MUST dispatch all resolved steps sequentially through the existing bundle workflow
- **AND** if `read-zxg-full` fails, the system MUST stop before dispatching `export-zxg-watchlist`
- **AND** if `export-zxg-watchlist` fails, the bundle MUST return a failed result with the export step marked as the failed step
