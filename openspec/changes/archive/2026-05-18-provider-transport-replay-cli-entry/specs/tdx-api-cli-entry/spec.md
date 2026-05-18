# tdx-api-cli-entry Delta

## ADDED Requirements

### Requirement: CLI SHALL expose provider replay service operations separately from live bridge commands

The CLI SHALL expose provider replay service operations under a dedicated command group so callers do not confuse fixture-backed replay transport with live bridge/provider commands.

#### Scenario: Caller parses provider replay service commands

- **WHEN** a caller builds the CLI parser
- **THEN** `provider-replay serve` and `provider-replay config-check` MUST parse as provider replay commands with a required config path

