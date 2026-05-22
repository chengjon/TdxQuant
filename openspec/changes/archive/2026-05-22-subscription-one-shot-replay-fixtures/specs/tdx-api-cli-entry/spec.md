## ADDED Requirements

### Requirement: Query API CLI SHALL expose one-shot subscription replay entrypoints
The CLI SHALL allow one-shot subscription API commands to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: One-shot subscription commands use replay manager
- **WHEN** a caller invokes `api subscription-subscribe`, `api subscription-unsubscribe`, or `api subscription-list` with `--provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").runtime.subscription_*`
- **AND** the CLI MUST NOT reject those commands as unsupported replay commands
- **AND** the CLI MUST NOT start a foreground watch, background worker, or SSE stream
