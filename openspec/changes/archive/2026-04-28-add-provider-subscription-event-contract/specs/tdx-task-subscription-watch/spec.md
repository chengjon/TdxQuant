## MODIFIED Requirements

### Requirement: Subscription watch task SHALL emit normalized event artifacts
The system SHALL normalize subscription callback payloads into machine-readable event rows and append them to durable task artifacts instead of exposing only raw callback side effects.

#### Scenario: Subscription callback is normalized into stable event rows
- **WHEN** a runtime subscription callback delivers one or more market update payloads
- **THEN** the task MUST append normalized rows to a JSONL artifact
- **AND** each normalized row MUST conform to the provider-level subscription event contract

#### Scenario: Task writes a lightweight flat artifact view
- **WHEN** the subscription watch task appends normalized event rows
- **THEN** the task MUST also maintain a lightweight CSV artifact view for routine inspection
