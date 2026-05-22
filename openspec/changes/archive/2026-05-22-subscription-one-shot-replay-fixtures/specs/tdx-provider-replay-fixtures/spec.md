## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include one-shot subscription samples
The provider replay fixture bundle SHALL include representative synchronous samples for one-shot subscription subscribe, unsubscribe, and list operations.

#### Scenario: Consumer enumerates one-shot subscription fixtures
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `subscription-subscribe-success`
- **AND** the catalog MUST include `subscription-unsubscribe-success`
- **AND** the catalog MUST include `subscription-list-success`
- **AND** those descriptors MUST identify capabilities `subscription.subscribe_hq`, `subscription.unsubscribe_hq`, and `subscription.get_subscribe_hq_stock_list`

#### Scenario: Consumer loads one-shot subscription fixtures
- **WHEN** a caller loads the one-shot subscription fixtures
- **THEN** each fixture MUST preserve the provider result envelope
- **AND** each fixture MUST preserve operation metadata identifying one-shot scope
- **AND** the fixtures MUST NOT imply foreground watch, background worker, or SSE stream behavior
