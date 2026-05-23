## ADDED Requirements

### Requirement: Subscription long-run status SHALL evaluate reconnect staleness only when explicitly requested

The subscription long-run status summary SHALL expose read-only reconnect/degraded duration staleness only when the caller provides an explicit `reconnect_stale_after_seconds` threshold, and SHALL NOT change reconnect, backoff, restart, or lifecycle behavior.

#### Scenario: Caller omits reconnect stale threshold

- **WHEN** the persisted watch status contains reconnect or degraded timestamps
- **AND** the caller does not provide `reconnect_stale_after_seconds`
- **THEN** the reconnect summary MUST keep `staleness=not_evaluated`
- **AND** governance MUST NOT add reconnect stale reasons or actions

#### Scenario: Caller evaluates reconnect staleness

- **WHEN** the watch status is `reconnecting` or `degraded`
- **AND** the caller provides `reconnect_stale_after_seconds`
- **AND** the reconnect or degraded age exceeds that threshold
- **THEN** the reconnect summary MUST report `staleness=stale`, `age_seconds`, `stale_after_seconds`, and `evaluated_at`
- **AND** governance MUST include a `reconnect:stale` reason and review-only reconnect action

#### Scenario: Caller evaluates reconnect staleness outside resilience state

- **WHEN** the watch status is not `reconnecting` or `degraded`
- **AND** the caller provides `reconnect_stale_after_seconds`
- **THEN** the reconnect summary MUST report `staleness=not_applicable`
- **AND** governance MUST NOT add a reconnect stale reason
