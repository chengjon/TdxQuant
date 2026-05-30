## ADDED Requirements

### Requirement: PingAn live trading implementation SHALL be gated by safety and acceptance evidence

Before PingAn buy/sell/confirm_current/submit_once paths are claimed implemented, the implementation SHALL provide evidence for live-provider capability ownership, explicit safety checks, desktop result/exception handling, audit persistence, and acceptance verification.

#### Scenario: Live trading promotion requires ordered gates

- **WHEN** a later change attempts to promote D-07 or D-08 to `[已实现]`
- **THEN** the change MUST provide provider/broker ownership evidence
- **AND** safety evidence for max price or equivalent guardrails, submission-key/idempotency, and explicit approval semantics
- **AND** desktop lifecycle evidence for dialog readiness, result popups, exception popups, timeout/retry handling, and process/window ownership
- **AND** audit evidence for success/failure/rejection/exception paths
- **AND** automated fake/replay verification plus documented manual/live acceptance evidence where the real environment is required.

#### Scenario: Read-only catalog evidence cannot satisfy live trading safety gates

- **WHEN** evidence only comes from catalog validate, catalog plan, or catalog preview output
- **THEN** the evidence MUST NOT satisfy live trading safety, readiness, or acceptance gates.
