## ADDED Requirements

### Requirement: PingAn guarded trade owner-lock guard evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite guarded trade-buy owner-lock guard forwarding as partial D-07 safety evidence only.

#### Scenario: Guarded owner-lock evidence is registered without status change

- **WHEN** D-07 evidence cites guarded trade-buy owner-lock guard forwarding
- **THEN** D-07 SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce guarded owner-lock guard forwarding
- **AND** the boundary SHALL state that guarded trade-buy only forwards an opt-in local guard and does not acquire/release locks, write lifecycle statefile/lock artifacts directly, control PingAn processes, prove broker readiness, or provide live/manual acceptance.
