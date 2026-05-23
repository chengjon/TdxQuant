## ADDED Requirements

### Requirement: Subscription long-run status SHALL evaluate watermark staleness only when explicitly requested

The long-run status summary SHALL support explicit watermark staleness diagnostics without changing reconnect, backoff, restart, or event-stream behavior.

#### Scenario: Caller omits watermark stale threshold

- **WHEN** the persisted watch status contains a watermark timestamp and the caller does not provide `watermark_stale_after_seconds`
- **THEN** the watermark summary MUST keep `staleness=not_evaluated`

#### Scenario: Caller evaluates watermark staleness

- **WHEN** the persisted watch status contains `last_event_ts` and the caller provides a positive watermark stale threshold
- **THEN** the watermark summary MUST include fresh/stale state, age seconds, stale threshold, and evaluated timestamp
- **AND** the summary MUST NOT change reconnect/backoff behavior
