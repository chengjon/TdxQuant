## ADDED Requirements

### Requirement: Task trade CLI SHALL expose lifecycle owner-lock execution guard options

Stable task trade CLI commands SHALL expose the same optional lifecycle owner-lock execution guard arguments as stable trade execution commands.

#### Scenario: Task trade-buy accepts guard options

- **WHEN** a caller parses `task trade-buy --require-lifecycle-owner-lock`
- **THEN** the parsed arguments MUST include lifecycle statefile path, lifecycle owner token, stale timeout, and require flag fields.

#### Scenario: Task trade-sell accepts guard options

- **WHEN** a caller parses `task trade-sell --require-lifecycle-owner-lock`
- **THEN** the parsed arguments MUST include lifecycle statefile path, lifecycle owner token, stale timeout, and require flag fields.

#### Scenario: Task trade-submit-once accepts guard options

- **WHEN** a caller parses `task trade-submit-once --require-lifecycle-owner-lock`
- **THEN** the parsed arguments MUST include lifecycle statefile path, lifecycle owner token, stale timeout, and require flag fields while preserving explicit `--side` parsing.

### Requirement: Task trade CLI dispatch SHALL forward lifecycle owner-lock execution guard options

Task trade CLI dispatch SHALL forward parsed lifecycle owner-lock guard arguments to `TdxTaskManager` without executing lifecycle control itself.

#### Scenario: Task trade dispatch forwards guard arguments

- **WHEN** task trade CLI dispatch handles `trade-buy`, `trade-sell`, or `trade-submit-once`
- **THEN** it MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to the corresponding task manager method.
