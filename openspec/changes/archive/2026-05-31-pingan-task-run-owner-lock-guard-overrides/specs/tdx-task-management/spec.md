## ADDED Requirements

### Requirement: Task preset execution SHALL preserve lifecycle owner-lock guard options for trade tasks

Task preset execution SHALL preserve preset-provided lifecycle owner-lock guard options and expose them to the resolved task trade command namespace.

#### Scenario: Preset-provided guard options are preserved

- **WHEN** a task preset for `trade-buy`, `trade-sell`, or `trade-submit-once` includes lifecycle owner-lock guard options
- **THEN** the resolved namespace MUST retain those values when the caller does not provide explicit CLI overrides.

#### Scenario: Missing stale timeout uses the stable default

- **WHEN** the resolved task namespace has no lifecycle stale timeout
- **THEN** owner-lock guard forwarding MUST use the stable `300.0` second default instead of failing.

### Requirement: Task preset owner-lock guard forwarding SHALL remain bounded

Task preset owner-lock guard forwarding SHALL remain argument forwarding to existing task trade workflows.

#### Scenario: Preset guard forwarding remains bounded

- **WHEN** task preset execution forwards lifecycle owner-lock guard options
- **THEN** it MUST NOT acquire or release owner locks
- **AND** it MUST NOT write lifecycle statefile/lock artifacts directly
- **AND** it MUST NOT start, stop, restart, kill, supervise, or back off PingAn processes.
