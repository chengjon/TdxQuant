# tdx-data-api-bridge Specification

## Purpose

定义 TongDaXin 数据接口桥接能力，使 WSL 侧能够通过稳定 JSON 结果访问行情、K 线与股票/板块元数据。
## Requirements
### Requirement: Data bridge SHALL expose TongDaXin market snapshot access
The system SHALL expose a bridge command for fetching TongDaXin market snapshot data without relying on GUI scraping.

#### Scenario: Fetch market snapshot for a symbol
- **WHEN** a caller requests market snapshot data for a valid symbol
- **THEN** the bridge returns structured snapshot fields from the TongDaXin data interface

#### Scenario: Snapshot request includes field filter
- **WHEN** a caller requests market snapshot data with an explicit field filter
- **THEN** the bridge returns only the requested fields when the underlying TongDaXin interface supports field selection

### Requirement: Data bridge SHALL expose TongDaXin K-line access
The system SHALL expose a bridge command for fetching historical K-line data for a valid symbol and period.

#### Scenario: Fetch K-line data
- **WHEN** a caller requests K-line data with a valid symbol, period, and date/count parameters
- **THEN** the bridge returns structured bar data in JSON form

#### Scenario: K-line request is invalid
- **WHEN** a caller requests K-line data with invalid symbol or period parameters
- **THEN** the bridge returns a structured invalid-request error

### Requirement: Data bridge SHALL expose stock and sector metadata
The system SHALL expose bridge commands for stock metadata and sector/board enumeration so that WSL-side scripts can discover TongDaXin symbols and groupings.

#### Scenario: Fetch stock metadata
- **WHEN** a caller requests stock metadata for a valid symbol
- **THEN** the bridge returns structured stock information from the TongDaXin interface

#### Scenario: List sectors
- **WHEN** a caller requests the available TongDaXin sectors or boards
- **THEN** the bridge returns a structured list of sectors

#### Scenario: List stocks in sector
- **WHEN** a caller requests the constituents of a valid sector
- **THEN** the bridge returns the sector constituents in structured JSON form

### Requirement: Bridge watch-status SHALL forward watermark stale threshold

Bridge watch-status surfaces SHALL accept and forward an explicit watermark stale threshold to the background controller.

#### Scenario: Caller requests bridge watch-status with watermark threshold

- **WHEN** a caller requests `watch/status` with `watermark_stale_after_seconds`
- **THEN** bridge HTTP, registry, and CLI watch-status paths MUST forward that threshold to the controller
- **AND** the response MUST remain a read-only status projection
