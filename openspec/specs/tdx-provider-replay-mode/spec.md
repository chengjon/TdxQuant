# tdx-provider-replay-mode Specification

## Purpose
Stable in-process provider replay mode for offline contract validation through the same public entrypoints used by live execution.
## Requirements
### Requirement: Provider replay mode SHALL serve supported capabilities through deterministic fixture-backed execution
The system SHALL provide an in-process replay provider mode for selected provider-facing capabilities so callers can consume stable offline responses through the same public entrypoints used by live mode.

#### Scenario: Replay mode uses default built-in fixture for a supported synchronous capability
- **WHEN** a caller invokes a supported synchronous provider-facing capability in replay mode without explicitly selecting a fixture
- **THEN** the system MUST resolve a stable built-in fixture for that capability
- **AND** the returned result MUST match the provider contract for that capability without touching live Windows runtime code

#### Scenario: Replay mode uses an explicit built-in fixture override
- **WHEN** a caller invokes a supported capability in replay mode with an explicit built-in fixture name
- **THEN** the system MUST load that named fixture instead of the default capability mapping
- **AND** the returned result MUST preserve the current capability-specific contract fields

#### Scenario: Replay mode uses an explicit fixture path override
- **WHEN** a caller invokes a supported capability in replay mode with an explicit JSON or JSONL fixture path
- **THEN** the system MUST load the caller-supplied fixture asset instead of a built-in sample
- **AND** the system MUST reject malformed fixture content before emitting a replay result

### Requirement: Provider replay mode SHALL reject unsupported or unresolved replay execution without live fallback
The system SHALL treat replay mode as a strict offline execution path and MUST never silently route replay-mode calls to live Windows runtime code.

#### Scenario: Replay mode rejects unsupported capability
- **WHEN** a caller invokes a capability that replay mode does not support
- **THEN** the system MUST return a stable failure result describing the unsupported replay capability
- **AND** the system MUST NOT attempt a live provider call

#### Scenario: Replay mode rejects missing fixture resolution
- **WHEN** a caller invokes replay mode and no default, named, or path-based fixture can be resolved for the requested capability
- **THEN** the system MUST return a stable failure result describing the unresolved replay fixture
- **AND** the system MUST NOT attempt a live provider call

### Requirement: Provider replay mode SHALL keep transport replay strict and fixture-backed
The system SHALL treat transport replay execution as a replay-only path backed by explicit fixture data.

#### Scenario: Transport replay never falls back to live runtime
- **WHEN** a transport replay request cannot resolve a required fixture
- **THEN** the system MUST return a stable replay error
- **AND** it MUST NOT invoke live TongDaXin runtime code

#### Scenario: Transport replay identifies replay source metadata
- **WHEN** a replay HTTP response or replay SSE frame is emitted
- **THEN** the payload MUST include replay source metadata sufficient to distinguish built-in fixtures from caller-supplied fixture paths

### Requirement: Provider replay mode SHALL serve stock-info through default fixture-backed execution
Replay mode SHALL treat `market.stock_info` as a supported synchronous provider-facing capability backed by a stable built-in fixture.

#### Scenario: Replay mode resolves default stock-info fixture
- **WHEN** a caller invokes `market.stock_info` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `market-stock-info-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime stock-info code

### Requirement: Provider replay mode SHALL serve more-info through default fixture-backed execution
Replay mode SHALL treat `market.more_info` as a supported synchronous provider-facing capability backed by a stable built-in fixture.

#### Scenario: Replay mode resolves default more-info fixture
- **WHEN** a caller invokes `market.more_info` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `market-more-info-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime more-info code

### Requirement: Provider replay mode SHALL serve cb-info through default fixture-backed execution
Replay mode SHALL treat `market.cb_info` as a supported synchronous provider-facing capability backed by a stable built-in fixture.

#### Scenario: Replay mode resolves default cb-info fixture
- **WHEN** a caller invokes `market.cb_info` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `market-cb-info-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime cb-info code

### Requirement: Provider replay mode SHALL serve gb-info through default fixture-backed execution
Replay mode SHALL treat `meta.gb_info` as a supported synchronous provider-facing capability backed by a stable built-in fixture.

#### Scenario: Replay mode resolves default gb-info fixture
- **WHEN** a caller invokes `meta.gb_info` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `meta-gb-info-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime gb-info code

### Requirement: Provider replay mode SHALL serve ipo-info through default fixture-backed execution
Replay mode SHALL treat `meta.ipo_info` as a supported synchronous provider-facing capability backed by a stable built-in fixture.

#### Scenario: Replay mode resolves default ipo-info fixture
- **WHEN** a caller invokes `meta.ipo_info` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `meta-ipo-info-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime ipo-info code
