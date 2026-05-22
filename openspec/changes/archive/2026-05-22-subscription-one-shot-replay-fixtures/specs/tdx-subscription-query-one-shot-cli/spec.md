## ADDED Requirements

### Requirement: Subscription one-shot replay SHALL preserve one-shot boundaries
Subscription one-shot replay SHALL exercise only the one-shot subscribe, unsubscribe, and list contracts and SHALL NOT claim long-running subscription governance.

#### Scenario: Replay one-shot response identifies one-shot scope
- **WHEN** a caller receives a replay response for one-shot subscription subscribe, unsubscribe, or list
- **THEN** the response MUST include metadata identifying `scope` as `one_shot`
- **AND** the response MUST NOT include foreground watch run, background worker, or SSE stream lifecycle metadata
