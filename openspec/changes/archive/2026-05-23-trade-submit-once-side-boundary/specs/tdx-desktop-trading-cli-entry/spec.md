## ADDED Requirements

### Requirement: Trade submit-once CLI SHALL expose explicit order side

The stable submit-once CLI entry SHALL make the requested order side explicit while preserving the existing buy default and buy-only flat compatibility command.

#### Scenario: Caller runs submit-once with explicit sell side

- **WHEN** a caller executes `trade submit-once --side sell`
- **THEN** the CLI MUST build the stable submit-once request with sell side
- **AND** it MUST still use the submit-once execution mode
- **AND** it MUST keep existing safety controls such as `submission_key` and `max_price`

#### Scenario: Caller omits submit-once side

- **WHEN** a caller executes `trade submit-once` without `--side`
- **THEN** the CLI MUST preserve the previous buy-side default

#### Scenario: Caller uses the flat buy submit-once compatibility command

- **WHEN** a caller executes `pingan-buy-submit-once`
- **THEN** the command MUST remain buy-only by name
- **AND** the new side selector MUST NOT be required for that legacy command
