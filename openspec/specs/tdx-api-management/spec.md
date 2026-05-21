## Purpose

定义 TdxQuant 查询能力的 manager 层约束，使调用方可以通过 `TdxApiManager` 使用稳定的 Python 入口、profile 解析、管理元数据和清晰的域边界，而不需要直接拼接底层 bridge 调用。
## Requirements
### Requirement: Query API management SHALL provide a unified manager entrypoint
The system SHALL provide a `TdxApiManager` entrypoint for query-oriented TdxQuant capabilities so that callers do not need to invoke bridge functions directly for daily API workflows.

#### Scenario: Code caller uses manager to access meta reference data
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke dividend-factor and IPO reference data queries through `manager.meta.<method>()`

### Requirement: Query API management SHALL keep domain modules profile-agnostic
The system SHALL keep `market`, `meta`, `formula`, `block`, and `runtime` domain modules independent from profile file loading and top-level profile merge logic.

#### Scenario: Meta reference data method receives standardized parameters
- **WHEN** a meta reference data method is invoked by the manager
- **THEN** the domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

### Requirement: Query API management SHALL support API profiles with explicit override precedence
The system SHALL load query API profiles from `runtime/api-profiles.json` using an absolute path and SHALL apply explicit call-time overrides after loading the selected profile.

#### Scenario: Profile file is resolved without relying on current working directory
- **WHEN** the caller invokes manager logic from any working directory
- **THEN** the profile file path MUST be resolved from project-relative code location rather than from process current working directory

#### Scenario: Explicit arguments override profile defaults
- **WHEN** a selected profile provides default values and the caller also passes explicit parameter values
- **THEN** the explicit parameter values MUST take precedence over the profile defaults

### Requirement: Query API management SHALL attach standardized management metadata
The system SHALL return manager-driven synchronous query and formula style results inside the provider-facing result envelope and SHALL attach standardized management metadata, including effective profile identity, timing fields, capability identity, and schema/version metadata.

#### Scenario: Manager-driven query returns profile metadata in the provider result envelope
- **WHEN** a manager-driven query or formula style call completes
- **THEN** the result MUST include the effective API profile information used for the call within the provider-facing result envelope

#### Scenario: Manager-driven query returns timing fields in the provider result envelope
- **WHEN** a manager-driven query or formula style call completes
- **THEN** the result MUST include `started_at`, `finished_at`, and `elapsed_ms` fields for the manager-managed execution flow

#### Scenario: Manager-driven query returns capability identity and version metadata
- **WHEN** a manager-driven query or formula style call completes
- **THEN** the result MUST include `capability`, `capability_version`, and `schema_version` fields in addition to the manager metadata already attached by the manager layer

### Requirement: Query API management SHALL expose refresh cache as a direct manager action
The system SHALL expose `refresh_cache` as a direct manager action instead of placing it in the read-only `meta` domain or conflating it with `refresh_kline`.

#### Scenario: Caller refreshes market cache through manager
- **WHEN** a caller invokes the manager refresh-cache action with market and force parameters
- **THEN** the manager MUST delegate to the existing bridge refresh-cache capability and return standardized management metadata

#### Scenario: Refresh cache remains separate from runtime kline refresh
- **WHEN** a caller needs to refresh historical K-line data for specific securities and periods
- **THEN** the caller MUST use `manager.runtime.refresh_kline(...)` rather than `manager.refresh_cache(...)`

### Requirement: Query API management SHALL keep block writes outside the read-only meta domain
The system SHALL represent user-block write actions through a dedicated `block` domain rather than placing them inside the read-only `meta` domain.

#### Scenario: Caller updates a user block through manager
- **WHEN** a caller requests a user-block update through the manager
- **THEN** the manager MUST expose that action through `manager.block` rather than through `manager.meta`

#### Scenario: Meta domain remains read-oriented
- **WHEN** a caller accesses `manager.meta`
- **THEN** that domain MUST remain focused on read-oriented metadata capabilities rather than user-block write actions

#### Scenario: Caller manages custom-sector lifecycle through block domain
- **WHEN** a caller needs to list, create, rename, clear, or delete a custom sector
- **THEN** the manager MUST expose those actions through `manager.block` rather than through `manager.meta`

#### Scenario: Caller synchronizes a watchlist into a custom sector through block domain
- **WHEN** a caller needs to push a normalized watchlist into a custom sector with `replace` or `merge` semantics
- **THEN** the manager MUST expose that action through `manager.block.sync_watchlist(...)`

### Requirement: Query API management SHALL keep formula preparation and execution as explicit manager-visible actions
The system SHALL expose formula data preparation and formula execution capabilities through explicit manager-visible methods instead of collapsing them into an opaque single-step manager behavior.

#### Scenario: Caller prepares formula runtime data
- **WHEN** a caller needs to prepare or inspect formula runtime data
- **THEN** the manager MUST expose explicit formula preparation methods through `manager.formula`

#### Scenario: Caller executes batch formula workflows
- **WHEN** a caller needs batch indicator or stock-picking formula execution
- **THEN** the manager MUST expose explicit batch formula methods through `manager.formula`

### Requirement: Query API management SHALL isolate runtime public query actions from market and meta domains
The system SHALL represent runtime public query actions through a dedicated `runtime` domain instead of placing them inside `market` or `meta`.

#### Scenario: Caller refreshes historical K-line cache through runtime domain
- **WHEN** a caller requests `refresh_kline` through the manager
- **THEN** the manager MUST expose that action through `manager.runtime.refresh_kline(...)`

#### Scenario: Caller requests trading dates or file download through runtime domain
- **WHEN** a caller requests `get_trading_dates` or `download_file` through the manager
- **THEN** the manager MUST expose those actions through `manager.runtime` rather than through `manager.market` or `manager.meta`

### Requirement: Query API management SHALL keep custom-sector resource lifecycle inside the block domain
The system SHALL represent custom-sector listing and lifecycle actions through the `block` domain instead of splitting them across `meta` and `block`.

#### Scenario: Caller reads custom-sector list through manager
- **WHEN** a caller requests the current custom-sector list
- **THEN** the manager MUST expose that action through `manager.block.user_sectors(...)`

#### Scenario: Caller manages custom-sector lifecycle through manager
- **WHEN** a caller creates, renames, deletes, clears, or appends to a custom sector
- **THEN** the manager MUST expose those actions through `manager.block`

### Requirement: Query API management SHALL expose professional financial queries through a dedicated financial domain
The system SHALL expose professional financial data queries through a dedicated `financial` domain on `TdxApiManager` instead of placing them inside `market` or `meta`.

#### Scenario: Caller requests professional financial data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke time-range professional financial queries through `manager.financial.financial_data(...)`

#### Scenario: Caller requests dated professional financial data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke dated professional financial queries through `manager.financial.financial_data_by_date(...)`

### Requirement: Query API management SHALL keep professional financial queries profile-agnostic and field-explicit
The system SHALL keep the `financial` domain independent from profile file loading and SHALL require the manager call site to pass professional financial `field_list` explicitly instead of filling those fields from API profile defaults.

#### Scenario: Financial domain delegates explicit parameters without reading profile files
- **WHEN** a manager-driven professional financial query is invoked
- **THEN** the `financial` domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Professional financial fields are not inferred from API profile defaults
- **WHEN** a caller invokes a manager financial query
- **THEN** the manager MUST use the explicitly provided professional financial field list rather than resolving a default field list from the selected API profile

### Requirement: Query API management SHALL expose stock transaction queries through a dedicated transaction domain
The system SHALL expose stock transaction data queries through a dedicated `transaction` domain on `TdxApiManager` instead of placing them inside `market`.

#### Scenario: Caller requests stock transaction data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke time-range stock transaction queries through `manager.transaction.stock_transaction_data(...)`

#### Scenario: Caller requests dated stock transaction data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke dated stock transaction queries through `manager.transaction.stock_transaction_data_by_date(...)`

### Requirement: Query API management SHALL keep stock transaction queries profile-agnostic and field-explicit
The system SHALL keep the `transaction` domain independent from profile file loading and SHALL require stock transaction `field_list` values to be passed explicitly instead of resolving them from API profile defaults.

#### Scenario: Transaction domain delegates explicit parameters without reading profile files
- **WHEN** a manager-driven stock transaction query is invoked
- **THEN** the `transaction` domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Stock transaction fields are not inferred from API profile defaults
- **WHEN** a caller invokes a manager stock transaction query
- **THEN** the manager MUST use the explicitly provided stock transaction field list rather than resolving a default field list from the selected API profile

### Requirement: Query API management SHALL preserve official latest-record semantics for dated stock transaction data
The system SHALL preserve the official runtime behavior that `year=0` and `mmdd=0` request the latest available stock transaction record.

#### Scenario: Caller requests latest dated stock transaction record
- **WHEN** a caller invokes `manager.transaction.stock_transaction_data_by_date(...)` with `year=0` and `mmdd=0`
- **THEN** the manager MUST pass those zero values through unchanged to the bridge layer

### Requirement: Query API management SHALL expose sector transaction queries through the transaction domain
The system SHALL expose sector transaction data queries through the existing `transaction` domain on `TdxApiManager` instead of placing them inside `market`.

#### Scenario: Caller requests sector transaction data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke time-range sector transaction queries through `manager.transaction.sector_transaction_data(...)`

#### Scenario: Caller requests dated sector transaction data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke dated sector transaction queries through `manager.transaction.sector_transaction_data_by_date(...)`

### Requirement: Query API management SHALL keep sector transaction queries profile-agnostic and field-explicit
The system SHALL keep sector transaction query methods independent from profile file loading and SHALL require sector transaction `field_list` values to be passed explicitly instead of resolving them from API profile defaults.

#### Scenario: Transaction domain delegates sector parameters without reading profile files
- **WHEN** a manager-driven sector transaction query is invoked
- **THEN** the `transaction` domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Sector transaction fields are not inferred from API profile defaults
- **WHEN** a caller invokes a manager sector transaction query
- **THEN** the manager MUST use the explicitly provided sector transaction field list rather than resolving a default field list from the selected API profile

### Requirement: Query API management SHALL preserve official latest-record semantics for dated sector transaction data
The system SHALL preserve the official runtime behavior that `year=0` and `mmdd=0` request the latest available sector transaction record.

#### Scenario: Caller requests latest dated sector transaction record
- **WHEN** a caller invokes `manager.transaction.sector_transaction_data_by_date(...)` with `year=0` and `mmdd=0`
- **THEN** the manager MUST pass those zero values through unchanged to the bridge layer

### Requirement: Query API management SHALL expose market transaction queries through the transaction domain
The system SHALL expose market transaction data queries through the existing `transaction` domain on `TdxApiManager` instead of placing them inside `market`.

#### Scenario: Caller requests market transaction data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke time-range market transaction queries through `manager.transaction.market_transaction_data(...)`

#### Scenario: Caller requests dated market transaction data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke dated market transaction queries through `manager.transaction.market_transaction_data_by_date(...)`

### Requirement: Query API management SHALL keep market transaction queries profile-agnostic and field-explicit
The system SHALL keep market transaction query methods independent from profile file loading and SHALL require market transaction `field_list` values to be passed explicitly instead of resolving them from API profile defaults.

#### Scenario: Transaction domain delegates market parameters without reading profile files
- **WHEN** a manager-driven market transaction query is invoked
- **THEN** the `transaction` domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Market transaction fields are not inferred from API profile defaults
- **WHEN** a caller invokes a manager market transaction query
- **THEN** the manager MUST use the explicitly provided market transaction field list rather than resolving a default field list from the selected API profile

### Requirement: Query API management SHALL preserve official latest-record semantics for dated market transaction data
The system SHALL preserve the official runtime behavior that `year=0` and `mmdd=0` request the latest available market transaction record.

#### Scenario: Caller requests latest dated market transaction record
- **WHEN** a caller invokes `manager.transaction.market_transaction_data_by_date(...)` with `year=0` and `mmdd=0`
- **THEN** the manager MUST pass those zero values through unchanged to the bridge layer

### Requirement: Query API management SHALL expose client warn sending through the runtime domain
The system SHALL expose client warn sending through the existing `runtime` domain on `TdxApiManager` instead of placing it inside `market` or introducing a separate top-level manager action.

#### Scenario: Caller sends warn payload through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke client warn sending through `manager.runtime.send_warn(...)`

### Requirement: Query API management SHALL keep client warn payloads explicit and profile-agnostic
The system SHALL keep `send_warn` payload construction independent from profile file loading and SHALL require the caller to pass warn batch lists explicitly instead of resolving default payload lists from API profile defaults.

#### Scenario: Runtime domain delegates warn payload without reading profile files
- **WHEN** a manager-driven warn send is invoked
- **THEN** the `runtime` domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Warn payload lists are not inferred from API profile defaults
- **WHEN** a caller invokes `manager.runtime.send_warn(...)`
- **THEN** the manager MUST use the explicitly provided warn payload lists rather than resolving default payload lists from the selected API profile

### Requirement: Query API management SHALL preserve official warn count semantics
The system SHALL preserve the official runtime behavior that `count` limits the number of effective entries in each warn payload list.

#### Scenario: Caller sends warn payload with explicit count
- **WHEN** a caller invokes `manager.runtime.send_warn(...)` with an explicit `count`
- **THEN** the manager MUST pass that `count` value through unchanged to the bridge layer

### Requirement: Query API management SHALL expose persistent runtime subscription sessions through the runtime domain
The system SHALL expose a persistent TongDaXin runtime subscription-session factory through `manager.runtime` instead of presenting official subscription governance as one-shot manager calls.

#### Scenario: Caller opens a runtime subscription session from the manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to open a persistent subscription session through `manager.runtime.open_subscription_session(...)`

### Requirement: Query API management SHALL keep runtime subscription session operations inside the manager envelope
The system SHALL keep manager-owned runtime subscription operations inside the existing manager metadata and timing model while requiring callers to provide explicit subscription inputs.

#### Scenario: Caller subscribes through a manager-owned runtime session
- **WHEN** a caller invokes `subscribe_hq(...)` on a session created by `manager.runtime.open_subscription_session(...)`
- **THEN** the returned result MUST include `runtime` domain metadata, method timing, and a stable session identifier

#### Scenario: Caller lists or removes subscriptions through the same manager-owned session
- **WHEN** a caller invokes `get_subscribe_hq_stock_list()` or `unsubscribe_hq(...)` on a session created by `manager.runtime.open_subscription_session(...)`
- **THEN** the manager MUST preserve the active strategy path and session identity for those operations without inferring subscription contents from API profile defaults

### Requirement: Query API management SHALL expose provider discovery actions through the runtime domain
The system SHALL expose provider capability discovery, provider health, and provider doctor actions through the existing `runtime` domain on `TdxApiManager` instead of creating an unrelated top-level manager surface.

#### Scenario: Caller requests capability discovery through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke provider capability discovery through `manager.runtime.capabilities(...)`

#### Scenario: Caller requests provider diagnostics through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke provider health and doctor diagnostics through `manager.runtime.health(...)` and `manager.runtime.doctor(...)`

### Requirement: Query API management SHALL attach standardized metadata to provider discovery responses
The system SHALL attach the same manager-driven metadata model to provider discovery style responses that it uses for other synchronous provider-facing capabilities.

#### Scenario: Manager capability discovery returns provider metadata
- **WHEN** a caller invokes `manager.runtime.capabilities(...)`, `manager.runtime.health(...)`, or `manager.runtime.doctor(...)`
- **THEN** the manager MUST attach effective profile metadata, capability identity, capability version, schema version, and timing metadata to the returned provider result envelope

### Requirement: Query API management SHALL expose a stable formula screen action
The system SHALL expose a stable `formula.screen(...)` action through `TdxApiManager.formula` in addition to the existing raw batch formula methods.

#### Scenario: Caller invokes formula screen through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke normalized stock-screen execution through `manager.formula.screen(...)`

#### Scenario: Raw batch formula method remains available
- **WHEN** a caller still needs the existing batch formula raw result shape
- **THEN** the manager MUST continue to expose `manager.formula.process_mul_xg(...)` alongside the new stable `manager.formula.screen(...)` action

### Requirement: Query API management SHALL expose block write mutation safety metadata
The system SHALL make block-domain write actions return standardized mutation summaries and audit artifact metadata through `TdxApiManager.block`.

#### Scenario: Manager block write returns mutation summary and artifact
- **WHEN** a caller invokes `manager.block.create_sector(...)`, `delete_sector(...)`, `rename_sector(...)`, `clear_sector(...)`, or `send_user_block(...)`
- **THEN** the returned provider-facing result MUST include a stable `data.block_mutation` summary
- **AND** the result MUST expose the audit artifact through provider artifacts and local artifact metadata

### Requirement: Query API management SHALL accept explicit block mutation safety options
The system SHALL allow callers to pass mutation safety options explicitly through block-domain write methods instead of inferring them from API profiles.

#### Scenario: Caller passes mutation safety options through manager block write
- **WHEN** a caller invokes a manager block write action with `mutation_key` and/or `audit_dir`
- **THEN** the manager MUST forward those options unchanged to the block-domain implementation and preserve them in the returned mutation contract

### Requirement: Query API management SHALL preserve hardened query metadata across manager-driven query domains
The system SHALL expose the stabilized query metadata contract for `market`, `meta`, `financial`, and `transaction` manager calls in addition to the existing provider result envelope.

#### Scenario: Manager-driven market query returns hardened query metadata
- **WHEN** a caller executes a manager-driven market query
- **THEN** the returned result MUST include the standardized query metadata under `data.query_meta` required by the provider query contract

#### Scenario: Manager-driven meta query returns hardened query metadata
- **WHEN** a caller executes a manager-driven meta query
- **THEN** the returned result MUST include the standardized query metadata under `data.query_meta` required by the provider query contract

#### Scenario: Manager-driven financial or transaction query returns hardened query metadata
- **WHEN** a caller executes a manager-driven financial or transaction query
- **THEN** the returned result MUST include the standardized query metadata under `data.query_meta` required by the provider query contract

#### Scenario: Manager layer preserves effective requested-field semantics
- **WHEN** a covered manager query resolves field defaults or normalized explicit field lists before calling the provider
- **THEN** `data.query_meta.requested_fields` MUST reflect that effective provider-bound field list rather than the caller's raw pre-normalization input

### Requirement: Query API management SHALL keep replay-mode query results contract-equivalent to live results
The system SHALL preserve the same hardened query metadata shape when a covered query capability is resolved from replay fixtures instead of live runtime execution.

#### Scenario: Replay-mode manager query preserves query metadata contract
- **WHEN** a caller executes a covered manager query in `provider_mode=replay`
- **THEN** the returned result MUST preserve the same `data.query_meta` fields and selector semantics as the live contract for that capability

### Requirement: Query API management SHALL route stock-info through replay dispatch
The manager stock-info query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager stock-info uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").market.stock_info(...)`
- **THEN** the manager MUST return the `market.stock_info` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for stock-info
- **AND** the manager MUST NOT call the live market stock-info bridge implementation

### Requirement: Query API management SHALL route more-info through replay dispatch
The manager more-info query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager more-info uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").market.more_info(...)`
- **THEN** the manager MUST return the `market.more_info` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for more-info
- **AND** the manager MUST NOT call the live market more-info bridge implementation

### Requirement: Query API management SHALL route cb-info through replay dispatch
The manager cb-info query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager cb-info uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").market.cb_info(...)`
- **THEN** the manager MUST return the `market.cb_info` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for cb-info
- **AND** the manager MUST NOT call the live market cb-info bridge implementation

### Requirement: Query API management SHALL route gb-info through replay dispatch
The manager gb-info query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager gb-info uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").meta.gb_info(...)`
- **THEN** the manager MUST return the `meta.gb_info` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for gb-info
- **AND** the manager MUST NOT call the live meta gb-info bridge implementation

### Requirement: Query API management SHALL route ipo-info through replay dispatch
The manager ipo-info query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager ipo-info uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").meta.ipo_info(...)`
- **THEN** the manager MUST return the `meta.ipo_info` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for ipo-info
- **AND** the manager MUST NOT call the live meta ipo-info bridge implementation

### Requirement: Query API management SHALL route gp-one through replay dispatch
The manager gp-one query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager gp-one uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").meta.gp_one_data(...)`
- **THEN** the manager MUST return the `meta.gp_one_data` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for gp-one
- **AND** the manager MUST NOT call the live meta gp-one bridge implementation

### Requirement: Query API management SHALL route divid-factors through replay dispatch
The manager divid-factors query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager divid-factors uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").meta.divid_factors(...)`
- **THEN** the manager MUST return the `meta.divid_factors` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for divid-factors
- **AND** the manager MUST NOT call the live meta divid-factors bridge implementation

### Requirement: Query API management SHALL route stock transaction by-date through replay dispatch
The manager stock transaction by-date query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager stock transaction by-date uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").transaction.stock_transaction_data_by_date(...)`
- **THEN** the manager MUST return the `transaction.stock_transaction_data_by_date` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for stock transaction by-date
- **AND** the manager MUST NOT call the live transaction stock transaction by-date bridge implementation

### Requirement: Query API management SHALL route market transaction by-date through replay dispatch
The manager market transaction by-date query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager market transaction by-date uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").transaction.market_transaction_data_by_date(...)`
- **THEN** the manager MUST return the `transaction.market_transaction_data_by_date` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for market transaction by-date
- **AND** the manager MUST NOT call the live transaction market transaction by-date bridge implementation

### Requirement: Query API management SHALL route sector transaction by-date through replay dispatch
The manager sector transaction by-date query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager sector transaction by-date uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").transaction.sector_transaction_data_by_date(...)`
- **THEN** the manager MUST return the `transaction.sector_transaction_data_by_date` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for sector transaction by-date
- **AND** the manager MUST NOT call the live transaction sector transaction by-date bridge implementation

### Requirement: Query API management SHALL route sector transaction range through replay dispatch
The manager sector transaction range query SHALL preserve live behavior in live mode while using deterministic fixture-backed execution in replay mode.

#### Scenario: Manager sector transaction range uses replay fixture in replay mode
- **WHEN** a caller invokes `TdxApiManager(provider_mode="replay").transaction.sector_transaction_data(...)`
- **THEN** the manager MUST return the `transaction.sector_transaction_data` replay fixture result
- **AND** the result MUST preserve the hardened `data.query_meta` contract for sector transaction range
- **AND** the manager MUST NOT call the live transaction sector transaction range bridge implementation

