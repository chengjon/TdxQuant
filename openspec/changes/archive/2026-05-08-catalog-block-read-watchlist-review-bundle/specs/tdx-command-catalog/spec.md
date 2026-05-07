## ADDED Requirements

### Requirement: Command catalog SHALL expose block read watchlist review bundles once the preset-backed entries are stable
The system SHALL expose stable catalog bundles for preset-backed block read watchlist review workflows once the underlying `read-zxg-watchlist` and `read-zxg-full` entries are available.

#### Scenario: Caller lists block read watchlist review bundles
- **WHEN** a caller lists catalog bundles after the stable `read-zxg-review` bundle is available
- **THEN** the catalog MUST include a bundle named `read-zxg-review`

#### Scenario: Caller plans a block read watchlist review bundle
- **WHEN** a caller executes `catalog plan --bundle read-zxg-review`
- **THEN** the system MUST resolve a two-step bundle that dispatches `read-zxg-watchlist` first and `read-zxg-full` second without executing either task workflow

#### Scenario: Caller overrides block code for a block read watchlist review bundle
- **WHEN** a caller executes `catalog plan` or `catalog run` for `read-zxg-review` with `--block-code <value>`
- **THEN** the system MUST propagate that `block_code` override to both `read-zxg-watchlist` and `read-zxg-full`

#### Scenario: Caller runs a block read watchlist review bundle
- **WHEN** a caller executes `catalog run --bundle read-zxg-review`
- **THEN** the system MUST dispatch the two preset-backed task entries sequentially through the existing bundle execution path
- **AND** if the first `read-zxg-watchlist` step fails, the system MUST stop the bundle before dispatching `read-zxg-full`
