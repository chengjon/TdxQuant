# tdx-desktop-trading-audit Specification

## Purpose
TBD - created by archiving change add-trade-audit-governance. Update Purpose after archive.
## Requirements
### Requirement: Stable desktop trading SHALL persist an immutable trade-audit artifact for finalized workflows
The system SHALL write one immutable JSON trade-audit artifact for every stable desktop trade workflow result that is finalized through the standard artifact-persistence path.

#### Scenario: Confirmed stable trade writes an audit artifact
- **WHEN** a stable desktop trade workflow finishes through `TdxTradeManager` and persists finalized artifacts
- **THEN** the workflow MUST write one immutable trade-audit JSON artifact for that finalized result
- **AND** the result artifacts MUST expose the written audit artifact path

#### Scenario: Finalized replayed or rejected result still writes an audit artifact
- **WHEN** a stable desktop trade workflow returns a finalized replayed or rejected result through the same persistence path
- **THEN** the workflow MUST still write one immutable trade-audit JSON artifact
- **AND** the audit summary MUST distinguish that outcome from a confirmed live trade

### Requirement: Stable desktop trading audit SHALL expose a normalized trade-audit summary
The system SHALL attach a normalized `trade_audit` summary to finalized stable trade results so callers can correlate the immutable audit artifact with existing persisted trade artifacts.

#### Scenario: Finalized result exposes normalized audit summary
- **WHEN** a stable desktop trade workflow writes a trade-audit artifact
- **THEN** the result `data` MUST include `trade_audit`
- **AND** that summary MUST include a stable schema version, audit identifier, outcome status, broker, and workflow method

#### Scenario: Persisted state and event artifacts include the same audit summary
- **WHEN** a stable desktop trade workflow writes a trade-audit artifact
- **THEN** the written last-order state payload MUST include the same normalized `trade_audit` summary
- **AND** the appended order-event row MUST include the same normalized `trade_audit` summary

### Requirement: Read-only or non-finalized stable trade workflows SHALL not write trade-audit artifacts
The system SHALL keep read-only and non-finalized stable trade workflows free of trade-audit side effects.

#### Scenario: Read-only workflow does not write trade-audit artifact
- **WHEN** a caller executes a read-only stable trade workflow such as health, preflight, or dialog readiness
- **THEN** the workflow MUST NOT write a trade-audit artifact

#### Scenario: Pre-confirm boundary workflow does not write trade-audit artifact
- **WHEN** a caller executes the stable submit-ready workflow or a confirm-current attempt that never advances confirmation
- **THEN** the workflow MUST NOT write a trade-audit artifact

