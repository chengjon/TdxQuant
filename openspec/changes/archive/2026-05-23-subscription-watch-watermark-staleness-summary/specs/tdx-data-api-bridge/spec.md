## ADDED Requirements

### Requirement: Bridge watch-status SHALL forward watermark stale threshold

Bridge watch-status surfaces SHALL accept and forward an explicit watermark stale threshold to the background controller.

#### Scenario: Caller requests bridge watch-status with watermark threshold

- **WHEN** a caller requests `watch/status` with `watermark_stale_after_seconds`
- **THEN** bridge HTTP, registry, and CLI watch-status paths MUST forward that threshold to the controller
- **AND** the response MUST remain a read-only status projection
