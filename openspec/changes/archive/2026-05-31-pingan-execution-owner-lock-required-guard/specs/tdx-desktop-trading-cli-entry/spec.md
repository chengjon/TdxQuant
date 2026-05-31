## ADDED Requirements

### Requirement: Stable trade execution CLI SHALL accept lifecycle owner-lock guard arguments

The stable `trade buy`, `trade sell`, and `trade submit-once` CLI commands SHALL accept optional lifecycle owner-lock guard arguments.

#### Scenario: Caller requires lifecycle owner lock during stable trade execution

- **WHEN** a caller executes `trade buy`, `trade sell`, or `trade submit-once` with `--require-lifecycle-owner-lock`, `--lifecycle-statefile-path`, `--lifecycle-owner-token`, and `--lifecycle-stale-after-seconds`
- **THEN** the CLI MUST parse those arguments
- **AND** the resolved PingAn desktop gateway MUST receive those values unchanged.

#### Scenario: Stable execution CLI guard does not dispatch lifecycle control

- **WHEN** a caller executes a stable trade execution CLI command with `--require-lifecycle-owner-lock`
- **THEN** the CLI MUST still dispatch the normal trade execution path
- **AND** it MUST NOT dispatch lifecycle owner lock acquire or release.
