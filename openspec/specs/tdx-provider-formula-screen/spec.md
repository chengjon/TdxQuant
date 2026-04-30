# tdx-provider-formula-screen Specification

## Purpose
TBD - created by archiving change add-provider-formula-screen-contract. Update Purpose after archive.
## Requirements
### Requirement: Provider formula screen SHALL expose a stable stock-screen contract
The system SHALL expose a provider-facing `formula.screen` capability for batch stock-screen execution so upstream callers can consume a stable normalized stock-screen payload instead of TongDaXin raw formula output shapes.

#### Scenario: Formula screen returns normalized stock-screen payload
- **WHEN** a caller invokes the provider-facing formula screen capability
- **THEN** the response `data` MUST include stable `input`, `summary`, `matched_symbols`, `unmatched_symbols`, and `rows` sections
- **AND** the payload MUST remain machine-readable without requiring callers to parse free-form text or TongDaXin-specific ad hoc key traversal

### Requirement: Provider formula screen SHALL preserve per-symbol match context
The system SHALL preserve enough per-symbol context for callers to understand why a stock matched or did not match without losing the ability to build a simple stock list.

#### Scenario: Formula screen row includes match details
- **WHEN** a formula screen response includes a symbol row
- **THEN** each row MUST include the symbol, matched status, field names, matched dates, latest match date, and normalized formula series details
- **AND** the top-level payload MUST still provide direct matched and unmatched symbol lists for simple watchlist style consumption

### Requirement: Provider formula screen SHALL normalize stock-picking truth semantics
The system SHALL convert raw stock-picking formula point values into stable match semantics so callers do not need to re-implement TongDaXin-specific truth parsing.

#### Scenario: Raw stock-picking values are normalized into matched status
- **WHEN** a formula screen response contains raw stock-picking values such as `1`, `1.0`, `'1'`, or equivalent truthy selection outputs
- **THEN** the provider MUST mark the corresponding point as matched
- **AND** the per-symbol matched status MUST reflect whether any normalized matched point exists for that symbol

