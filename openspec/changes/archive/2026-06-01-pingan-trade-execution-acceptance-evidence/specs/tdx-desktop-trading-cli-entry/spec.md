## ADDED Requirements

### Requirement: Trade CLI SHALL expose PingAn acceptance evidence summary

The stable desktop trade CLI SHALL expose a read-only `trade acceptance-evidence` command for PingAn trade execution acceptance evidence.

#### Scenario: CLI parses acceptance evidence command

- **WHEN** an operator runs `trade acceptance-evidence`
- **THEN** the CLI MUST parse the command without requiring order parameters
- **AND** the command MUST dispatch to the read-only PingAn acceptance evidence manager method.

#### Scenario: CLI acceptance evidence command does not execute trades

- **WHEN** `trade acceptance-evidence` is handled
- **THEN** it MUST NOT dispatch buy, sell, submit-once, confirm-current, task, report, catalog bundle, broker health, HID, UIA, or process lifecycle execution.
