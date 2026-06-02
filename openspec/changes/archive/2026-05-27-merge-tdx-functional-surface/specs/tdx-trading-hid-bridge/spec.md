## ADDED Requirements

### Requirement: TongDaXin HID trading bridge SHALL remain probe-scoped until business input acceptance is evidenced

The TongDaXin HID trading bridge SHALL be represented as a probe and diagnostic capability unless evidence shows that the TongDaXin trading business layer accepts the automated security-code input chain.

#### Scenario: TongDaXin bridge can fill and trigger controls
- **WHEN** TongDaXin bridge evidence shows code, price, quantity, submit control discovery, field write/read, or post-submit prompt capture
- **THEN** the capability MAY be registered as probing, prerequisite validation, or diagnostic automation
- **AND** it MUST NOT be registered as full order submission solely from those control-level observations

#### Scenario: Security-code business acceptance is missing
- **WHEN** TongDaXin evidence still produces a prompt equivalent to missing security code after automated input
- **THEN** the capability MUST remain unavailable for full live order submission
- **AND** operator-facing documentation MUST name security-code business-layer acceptance as the blocker

#### Scenario: Future evidence resolves the blocker
- **WHEN** future validation proves that TongDaXin accepts automated security-code input and completes the confirmation/result loop
- **THEN** a separate OpenSpec change MUST update the capability boundary before documentation claims full live TongDaXin order submission
