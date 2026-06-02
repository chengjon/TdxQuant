## ADDED Requirements

### Requirement: FUNCTION_TREE registry SHALL record external tdx merge decisions

The FUNCTION_TREE registry SHALL record merged external `tdx` evidence and capability decisions without allowing external documentation to become a competing source of feature truth.

#### Scenario: External tdx evidence is accepted
- **WHEN** implementation accepts a feature or validation conclusion from `D:\MyCode3\tdx`
- **THEN** the affected FUNCTION_TREE row MUST cite current checked-in evidence, an active OpenSpec change, an archived OpenSpec change, or an explicit external evidence reference
- **AND** the row boundary MUST state the usable scope of the accepted evidence

#### Scenario: External tdx evidence is rejected or deferred
- **WHEN** implementation rejects or defers an external `tdx` feature claim
- **THEN** the affected FUNCTION_TREE row MUST keep or adopt a boundary that prevents the feature from reading as currently available
- **AND** the rejection or deferral rationale MUST be traceable from the merge change tasks or docs

### Requirement: FUNCTION_TREE registry SHALL keep PingAn and TongDaXin trading status separate

The FUNCTION_TREE registry SHALL avoid collapsing PingAn desktop trading evidence and TongDaXin trading bridge evidence into one generic desktop-trading status.

#### Scenario: PingAn mixed-chain execution is registered
- **WHEN** PingAn real-machine validation is adopted
- **THEN** the registry MUST identify PingAn execution as a mixed UIA/HID/Win32 desktop chain
- **AND** it MUST NOT describe the capability as pure background Win32 automation

#### Scenario: TongDaXin trading probe boundary is registered
- **WHEN** TongDaXin trading bridge evidence is registered
- **THEN** the registry MUST distinguish probe or diagnostic capability from full live order submission
- **AND** it MUST mark full TongDaXin order submission as unavailable unless business-layer security-code acceptance is evidenced
