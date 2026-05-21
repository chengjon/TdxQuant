## Purpose

定义查询 API 的标准命令行入口结构，使项目同时保留 flat bridge 调用和嵌套 `api` manager 调用，并让日常使用优先走稳定的 `TdxApiManager` 路径。
## Requirements
### Requirement: Query API CLI SHALL provide a nested api command group
The system SHALL provide a nested `api` command group for query-oriented TdxQuant access in addition to the existing flat CLI commands.

#### Scenario: Caller invokes nested api divid-factors command
- **WHEN** a caller invokes the nested `api divid-factors` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.meta.divid_factors(...)`

#### Scenario: Caller invokes nested api ipo-info command
- **WHEN** a caller invokes the nested `api ipo-info` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.meta.ipo_info(...)`

#### Scenario: Caller invokes nested api block-sync command
- **WHEN** a caller invokes `api block-sync`
- **THEN** the CLI MUST dispatch the call through the manager-backed block sync capability

### Requirement: Query API CLI SHALL preserve existing flat command compatibility
The system SHALL keep existing flat query commands functional while introducing the new nested `api` command group.

#### Scenario: Existing formula command remains available during migration
- **WHEN** a caller invokes an existing flat formula-related command during the expansion phase
- **THEN** that command MUST remain usable while the nested `api` group is being expanded

#### Scenario: Existing user-block command remains available during migration
- **WHEN** a caller invokes `tdx-send-user-block` during the expansion phase
- **THEN** that command MUST remain usable while the nested `api` group is being expanded

#### Scenario: Existing flat kline command remains available during migration
- **WHEN** a caller invokes `tdx-data-kline` during the expansion phase
- **THEN** that command MUST remain usable while the nested `api` group is being expanded

#### Scenario: Existing flat send-user-block command remains available during migration
- **WHEN** a caller invokes `tdx-send-user-block` during the expansion phase after block lifecycle expansion
- **THEN** that command MUST remain usable alongside the new custom-sector lifecycle commands

#### Scenario: Caller invokes flat block-sync command during migration
- **WHEN** a caller invokes `tdx-block-sync`
- **THEN** the CLI MUST dispatch the call to the dedicated block sync wrapper while preserving existing block write commands

### Requirement: Query API CLI SHALL support profile-driven daily usage
The system SHALL allow the nested `api` command group to accept a profile selection and standard output path controls for daily usage while emitting structured machine-readable output through the provider-facing synchronous result envelope.

#### Scenario: Caller selects an api profile
- **WHEN** a caller invokes a nested `api` query command with `--profile`
- **THEN** the command MUST resolve the named API profile and apply it through the manager layer

#### Scenario: Caller requests structured output from api command
- **WHEN** a caller invokes a nested `api` query command with an output destination
- **THEN** the command MUST write the structured result using the provider-facing synchronous result envelope

### Requirement: Query API CLI SHALL expose flat bridge commands for runtime public query actions
The system SHALL expose flat bridge commands for runtime public query actions so that bridge-oriented callers can use the same capabilities without going through the manager layer.

#### Scenario: Caller invokes flat trading-dates bridge command
- **WHEN** a caller invokes `tdx-get-trading-dates`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_trading_dates`

#### Scenario: Caller invokes flat refresh-kline bridge command
- **WHEN** a caller invokes `tdx-refresh-kline`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `refresh_kline`

#### Scenario: Caller invokes flat download-file bridge command
- **WHEN** a caller invokes `tdx-download-file`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `download_file`

#### Scenario: Caller invokes flat custom-sector lifecycle bridge command
- **WHEN** a caller invokes `tdx-get-user-sector`, `tdx-create-sector`, `tdx-delete-sector`, `tdx-rename-sector`, or `tdx-clear-sector`
- **THEN** the CLI MUST dispatch the call to the corresponding bridge wrapper for that custom-sector lifecycle action

### Requirement: Query API CLI SHALL expose flat bridge commands for custom-sector lifecycle actions
The system SHALL expose flat bridge commands for custom-sector lifecycle actions so that bridge-oriented callers can use the same capabilities without going through the manager layer.

#### Scenario: Caller invokes flat get-user-sector bridge command
- **WHEN** a caller invokes `tdx-get-user-sector`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_user_sector`

#### Scenario: Caller invokes flat create-sector bridge command
- **WHEN** a caller invokes `tdx-create-sector`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `create_sector`

#### Scenario: Caller invokes flat delete-sector bridge command
- **WHEN** a caller invokes `tdx-delete-sector`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `delete_sector`

#### Scenario: Caller invokes flat rename-sector bridge command
- **WHEN** a caller invokes `tdx-rename-sector`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `rename_sector`

#### Scenario: Caller invokes flat clear-sector bridge command
- **WHEN** a caller invokes `tdx-clear-sector`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `clear_sector`

### Requirement: Query API CLI SHALL expose flat bridge commands for reference data queries
The system SHALL expose flat bridge commands for dividend-factor and IPO reference data so that bridge-oriented callers can use the same capabilities without going through the manager layer.

#### Scenario: Caller invokes flat divid-factors bridge command
- **WHEN** a caller invokes `tdx-data-divid-factors`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_divid_factors`

#### Scenario: Caller invokes flat ipo-info bridge command
- **WHEN** a caller invokes `tdx-data-ipo-info`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_ipo_info`

### Requirement: Query API CLI SHALL provide nested api commands for professional financial queries
The system SHALL expose professional financial data through nested `api` subcommands that dispatch through `TdxApiManager.financial`.

#### Scenario: Caller invokes nested api financial-data command
- **WHEN** a caller invokes `api financial-data`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.financial.financial_data(...)`

#### Scenario: Caller invokes nested api financial-data-by-date command
- **WHEN** a caller invokes `api financial-data-by-date`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.financial.financial_data_by_date(...)`

### Requirement: Query API CLI SHALL expose flat bridge commands for professional financial queries
The system SHALL keep flat bridge-oriented CLI access available for professional financial queries alongside the nested `api` manager path.

#### Scenario: Caller invokes flat financial-data bridge command
- **WHEN** a caller invokes `tdx-data-financial`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_financial_data`

#### Scenario: Caller invokes flat financial-data-by-date bridge command
- **WHEN** a caller invokes `tdx-data-financial-by-date`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_financial_data_by_date`

### Requirement: Query API CLI SHALL require explicit professional financial field selection
The system SHALL require callers to pass professional financial fields explicitly on CLI entrypoints instead of silently filling them from an API profile.

#### Scenario: Nested api financial-data command receives explicit fields
- **WHEN** a caller invokes `api financial-data` or `api financial-data-by-date`
- **THEN** the CLI MUST collect an explicit professional financial field list from the command arguments and pass it through unchanged

#### Scenario: Professional financial CLI command omits fields
- **WHEN** a caller invokes a professional financial CLI command without any field arguments
- **THEN** the CLI MUST reject the request before dispatching it to the manager or bridge layer

### Requirement: Query API CLI SHALL provide nested api commands for stock transaction queries
The system SHALL expose stock transaction data through nested `api` subcommands that dispatch through `TdxApiManager.transaction`.

#### Scenario: Caller invokes nested api stock-transaction-data command
- **WHEN** a caller invokes `api stock-transaction-data`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.stock_transaction_data(...)`

#### Scenario: Caller invokes nested api stock-transaction-data-by-date command
- **WHEN** a caller invokes `api stock-transaction-data-by-date`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.stock_transaction_data_by_date(...)`

### Requirement: Query API CLI SHALL expose flat bridge commands for stock transaction queries
The system SHALL keep flat bridge-oriented CLI access available for stock transaction queries alongside the nested `api` manager path.

#### Scenario: Caller invokes flat stock-transaction bridge command
- **WHEN** a caller invokes `tdx-data-stock-transaction`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_gpjy_value`

#### Scenario: Caller invokes flat stock-transaction-by-date bridge command
- **WHEN** a caller invokes `tdx-data-stock-transaction-by-date`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_gpjy_value_by_date`

### Requirement: Query API CLI SHALL require explicit stock transaction field selection and preserve zero-date semantics
The system SHALL require callers to pass stock transaction fields explicitly and SHALL preserve the official `year=0, mmdd=0` latest-record semantics for dated calls.

#### Scenario: CLI stock transaction command omits fields
- **WHEN** a caller invokes a stock transaction CLI command without any field arguments
- **THEN** the CLI MUST reject the request before dispatching it to the manager or bridge layer

#### Scenario: CLI dated stock transaction command uses zero-date latest-record query
- **WHEN** a caller invokes a dated stock transaction CLI command with `--year 0 --mmdd 0`
- **THEN** the CLI MUST pass those zero values through unchanged

### Requirement: Query API CLI SHALL provide nested api commands for sector transaction queries
The system SHALL expose sector transaction data through nested `api` subcommands that dispatch through `TdxApiManager.transaction`.

#### Scenario: Caller invokes nested api sector-transaction-data command
- **WHEN** a caller invokes `api sector-transaction-data`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.sector_transaction_data(...)`

#### Scenario: Caller invokes nested api sector-transaction-data-by-date command
- **WHEN** a caller invokes `api sector-transaction-data-by-date`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.sector_transaction_data_by_date(...)`

### Requirement: Query API CLI SHALL expose flat bridge commands for sector transaction queries
The system SHALL keep flat bridge-oriented CLI access available for sector transaction queries alongside the nested `api` manager path.

#### Scenario: Caller invokes flat sector-transaction bridge command
- **WHEN** a caller invokes `tdx-data-sector-transaction`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_bkjy_value`

#### Scenario: Caller invokes flat sector-transaction-by-date bridge command
- **WHEN** a caller invokes `tdx-data-sector-transaction-by-date`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_bkjy_value_by_date`

### Requirement: Query API CLI SHALL require explicit sector transaction field selection and preserve zero-date semantics
The system SHALL require callers to pass sector transaction fields explicitly and SHALL preserve the official `year=0, mmdd=0` latest-record semantics for dated calls.

#### Scenario: CLI sector transaction command omits fields
- **WHEN** a caller invokes a sector transaction CLI command without any field arguments
- **THEN** the CLI MUST reject the request before dispatching it to the manager or bridge layer

#### Scenario: CLI dated sector transaction command uses zero-date latest-record query
- **WHEN** a caller invokes a dated sector transaction CLI command with `--year 0 --mmdd 0`
- **THEN** the CLI MUST pass those zero values through unchanged

### Requirement: Query API CLI SHALL provide nested api commands for market transaction queries
The system SHALL expose market transaction data through nested `api` subcommands that dispatch through `TdxApiManager.transaction`.

#### Scenario: Caller invokes nested api market-transaction-data command
- **WHEN** a caller invokes `api market-transaction-data`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.market_transaction_data(...)`

#### Scenario: Caller invokes nested api market-transaction-data-by-date command
- **WHEN** a caller invokes `api market-transaction-data-by-date`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.market_transaction_data_by_date(...)`

### Requirement: Query API CLI SHALL expose flat bridge commands for market transaction queries
The system SHALL keep flat bridge-oriented CLI access available for market transaction queries alongside the nested `api` manager path.

#### Scenario: Caller invokes flat market-transaction bridge command
- **WHEN** a caller invokes `tdx-data-market-transaction`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_scjy_value`

#### Scenario: Caller invokes flat market-transaction-by-date bridge command
- **WHEN** a caller invokes `tdx-data-market-transaction-by-date`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_scjy_value_by_date`

### Requirement: Query API CLI SHALL require explicit market transaction field selection and preserve zero-date semantics
The system SHALL require callers to pass market transaction fields explicitly, SHALL not require any stock code list, and SHALL preserve the official `year=0, mmdd=0` latest-record semantics for dated calls.

#### Scenario: CLI market transaction command omits fields
- **WHEN** a caller invokes a market transaction CLI command without any field arguments
- **THEN** the CLI MUST reject the request before dispatching it to the manager or bridge layer

#### Scenario: CLI market transaction command does not require stock codes
- **WHEN** a caller invokes a market transaction CLI command with explicit field arguments and no stock code arguments
- **THEN** the CLI MUST accept the command and dispatch it without constructing a stock list

#### Scenario: CLI dated market transaction command uses zero-date latest-record query
- **WHEN** a caller invokes a dated market transaction CLI command with `--year 0 --mmdd 0`
- **THEN** the CLI MUST pass those zero values through unchanged

### Requirement: Query API CLI SHALL provide a nested api command for client warn sending
The system SHALL expose client warn sending through a nested `api` subcommand that dispatches through `TdxApiManager.runtime`.

#### Scenario: Caller invokes nested api send-warn command
- **WHEN** a caller invokes `api send-warn`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.runtime.send_warn(...)`

### Requirement: Query API CLI SHALL expose a flat bridge command for client warn sending
The system SHALL keep flat bridge-oriented CLI access available for client warn sending alongside the nested `api` manager path.

#### Scenario: Caller invokes flat send-warn bridge command
- **WHEN** a caller invokes `tdx-send-warn`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `send_warn`

### Requirement: Query API CLI SHALL keep warn batch payloads explicit
The system SHALL require callers to pass warn batch payload lists explicitly and SHALL preserve the official `count` semantics for warn sending.

#### Scenario: CLI send-warn command requires stock and time payload lists
- **WHEN** a caller invokes `api send-warn` or `tdx-send-warn`
- **THEN** the CLI MUST require explicit repeated inputs for stock codes and warn times before dispatch

#### Scenario: CLI send-warn command preserves explicit count
- **WHEN** a caller invokes a send-warn CLI command with `--count 3`
- **THEN** the CLI MUST pass that `count` value through unchanged

### Requirement: Query API CLI SHALL align JSON-oriented outputs with the provider result contract
The system SHALL use the same provider-facing synchronous result envelope for nested `api` outputs and flat bridge JSON-oriented outputs so that upstream systems can consume one stable machine contract.

#### Scenario: Nested api command writes provider-facing JSON envelope
- **WHEN** a caller requests structured JSON-oriented output from a nested `api` command
- **THEN** the CLI MUST serialize the result using the provider-facing synchronous result envelope

#### Scenario: Flat bridge command writes provider-facing JSON envelope
- **WHEN** a caller requests structured JSON-oriented output from a flat bridge query command
- **THEN** the CLI MUST serialize the result using the same provider-facing synchronous result envelope used by nested `api` commands

### Requirement: Query API CLI SHALL preserve JSON failure structure alongside exit-code semantics
The system SHALL preserve machine-readable JSON failure output for JSON-oriented CLI calls while also using stable process exit code semantics.

#### Scenario: Successful JSON-oriented CLI call exits cleanly
- **WHEN** a JSON-oriented nested `api` or flat bridge query command succeeds
- **THEN** the CLI process MUST exit with code `0`

#### Scenario: Failed JSON-oriented CLI call preserves structured failure output
- **WHEN** a JSON-oriented nested `api` or flat bridge query command fails
- **THEN** the CLI process MUST exit with a non-zero code
- **AND** the CLI MUST still emit the provider-facing synchronous result envelope describing the failure

### Requirement: Query API CLI SHALL provide nested api commands for provider discovery diagnostics
The system SHALL expose provider capability discovery and diagnostics through nested `api` commands that dispatch through `TdxApiManager.runtime`.

#### Scenario: Caller invokes nested api capabilities command
- **WHEN** a caller invokes `api capabilities`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.runtime.capabilities(...)`

#### Scenario: Caller invokes nested api health or doctor command
- **WHEN** a caller invokes `api health` or `api doctor`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.runtime.health(...)` or `TdxApiManager.runtime.doctor(...)`

### Requirement: Query API CLI SHALL expose flat bridge commands for provider discovery diagnostics
The system SHALL expose flat bridge-oriented commands for provider capability discovery and diagnostics so bridge-oriented callers can consume the same formal contract without going through the manager layer.

#### Scenario: Caller invokes flat capability discovery bridge command
- **WHEN** a caller invokes `tdx-capabilities`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for provider capability discovery

#### Scenario: Caller invokes flat health or doctor bridge command
- **WHEN** a caller invokes `tdx-health` or `tdx-doctor`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for provider health or doctor diagnostics

### Requirement: Query API CLI SHALL provide a stable formula screen command
The system SHALL expose the stable formula screen contract through both nested `api` and flat bridge-oriented CLI entrypoints.

#### Scenario: Caller invokes nested api formula-screen command
- **WHEN** a caller invokes `api formula-screen`
- **THEN** the CLI MUST dispatch the call through the stable formula screen manager action rather than through the raw batch formula method

#### Scenario: Caller invokes flat formula-screen bridge command
- **WHEN** a caller invokes `tdx-formula-screen`
- **THEN** the CLI MUST dispatch the call to the dedicated stable formula screen bridge wrapper

### Requirement: Query API CLI SHALL expose block mutation safety options on write commands
The system SHALL expose explicit block mutation safety arguments on both nested `api` and flat bridge-oriented block write commands.

#### Scenario: Caller passes mutation safety options through nested api block write
- **WHEN** a caller invokes `api create-sector`, `delete-sector`, `rename-sector`, `clear-sector`, or `send-user-block` with `--mutation-key` and/or `--audit-dir`
- **THEN** the CLI MUST dispatch those values unchanged through the manager block write action

#### Scenario: Caller passes mutation safety options through flat bridge block write
- **WHEN** a caller invokes `tdx-create-sector`, `tdx-delete-sector`, `tdx-rename-sector`, `tdx-clear-sector`, or `tdx-send-user-block` with `--mutation-key` and/or `--audit-dir`
- **THEN** the CLI MUST dispatch those values unchanged through the corresponding bridge wrapper

### Requirement: Query API CLI SHALL emit the block mutation safety contract on write commands
The system SHALL emit the standardized block mutation summary and audit artifact metadata for supported block write commands.

#### Scenario: Nested api block write returns standardized mutation contract
- **WHEN** a nested `api` block write command completes
- **THEN** the JSON result MUST include the standardized `data.block_mutation` payload and audit artifact metadata

#### Scenario: Flat bridge block write returns standardized mutation contract
- **WHEN** a flat bridge block write command completes
- **THEN** the JSON result MUST include the standardized `data.block_mutation` payload and audit artifact metadata

### Requirement: Query API CLI SHALL emit hardened query metadata for existing query entrypoints
The system SHALL preserve the stabilized query metadata contract on existing nested `api` and flat CLI query entrypoints for `market`, `meta`, `financial`, and `transaction`.

#### Scenario: Nested api query returns hardened query metadata
- **WHEN** a caller invokes a covered nested `api` query command
- **THEN** the CLI JSON result MUST include the standardized query metadata under `data.query_meta` required by the provider query contract

#### Scenario: Flat query command returns hardened query metadata
- **WHEN** a caller invokes a covered flat query command
- **THEN** the CLI JSON result MUST include the standardized query metadata under `data.query_meta` required by the provider query contract

#### Scenario: CLI preserves non-breaking query hardening contract
- **WHEN** a caller upgrades from the pre-hardening query contract to the hardened one
- **THEN** the CLI MUST preserve the existing top-level provider envelope
- **AND** new query metadata MUST be additive under `data.query_meta`

### Requirement: Query API CLI SHALL preserve replay-mode contract parity for covered query commands
The system SHALL keep replay-mode CLI query output contract-equivalent to live CLI query output for the covered query entrypoints.

#### Scenario: Replay-mode nested api query preserves query metadata contract
- **WHEN** a caller invokes a covered nested `api` query command with `--provider-mode replay`
- **THEN** the CLI MUST return the same hardened `data.query_meta` shape as the live query contract for that capability

#### Scenario: Replay-mode flat query preserves query metadata contract
- **WHEN** a caller invokes a covered flat query command with `--provider-mode replay`
- **THEN** the CLI MUST return the same hardened `data.query_meta` shape as the live query contract for that capability

### Requirement: Query API CLI SHALL expose bridge remote-control read commands for subscription-watch control planes
The system SHALL expose remote-control CLI read commands for the worker bridge control plane and keep them as transport-only JSON pass-through entrypoints.

#### Scenario: Caller invokes bridge health
- **WHEN** a caller invokes `tdxquant bridge health`
- **THEN** the CLI MUST dispatch the call through the master-side bridge registry/client
- **AND** stdout MUST print the resulting JSON payload unchanged

#### Scenario: Caller invokes bridge watch-list or watch-artifacts
- **WHEN** a caller invokes `tdxquant bridge watch-list` or `tdxquant bridge watch-artifacts`
- **THEN** the CLI MUST dispatch the call through the master-side bridge registry/client
- **AND** stdout MUST print the resulting JSON payload unchanged

#### Scenario: Caller invokes bridge watch-events or watch-logs with tail
- **WHEN** a caller invokes `tdxquant bridge watch-events --tail <n>` or `tdxquant bridge watch-logs --tail <n>`
- **THEN** the CLI MUST pass the tail parameter through the master-side bridge registry/client route
- **AND** stdout MUST print the resulting JSON payload unchanged

#### Scenario: Bridge remote-control CLI preserves bridge error payload
- **WHEN** the master-side bridge client returns a bridge failure payload with `ok=false`
- **THEN** the CLI MUST print that JSON payload unchanged
- **AND** it MUST return a failing exit code without rewriting the bridge `result` or `error` fields

#### Scenario: Bridge watch-status remains an active-snapshot reader
- **WHEN** a caller invokes `tdxquant bridge watch-status`
- **THEN** the CLI MUST return the current controller-projected active snapshot for that worker
- **AND** it MUST NOT reinterpret the command as a historical `run_id` lookup interface

### Requirement: API CLI SHALL expose subscription one-shot commands
The system SHALL expose query-style one-shot subscription commands under the nested `api` CLI namespace.

#### Scenario: Caller subscribes through API CLI
- **WHEN** a caller executes `api subscription-subscribe --code <stock>`
- **THEN** the CLI MUST dispatch the one-shot runtime subscription subscribe operation

#### Scenario: Caller unsubscribes through API CLI
- **WHEN** a caller executes `api subscription-unsubscribe --code <stock>`
- **THEN** the CLI MUST dispatch the one-shot runtime subscription unsubscribe operation

#### Scenario: Caller lists runtime subscribed stocks through API CLI
- **WHEN** a caller executes `api subscription-list`
- **THEN** the CLI MUST dispatch the one-shot runtime subscribed-stock-list operation

### Requirement: CLI SHALL expose provider replay service operations separately from live bridge commands

The CLI SHALL expose provider replay service operations under a dedicated command group so callers do not confuse fixture-backed replay transport with live bridge/provider commands.

#### Scenario: Caller parses provider replay service commands

- **WHEN** a caller builds the CLI parser
- **THEN** `provider-replay serve` and `provider-replay config-check` MUST parse as provider replay commands with a required config path

### Requirement: Query API CLI SHALL expose stock-info replay entrypoints
The CLI SHALL allow stock-info query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested stock-info command uses replay manager
- **WHEN** a caller invokes `api stock-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.stock_info(...)`
- **AND** the CLI MUST NOT construct or call the live stock-info bridge path

#### Scenario: Flat stock-info command uses replay manager
- **WHEN** a caller invokes `tdx-data-stock-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.stock_info(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened stock-info query metadata

### Requirement: Query API CLI SHALL expose more-info replay entrypoints
The CLI SHALL allow more-info query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested more-info command uses replay manager
- **WHEN** a caller invokes `api more-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.more_info(...)`
- **AND** the CLI MUST NOT construct or call the live more-info bridge path

#### Scenario: Flat more-info command uses replay manager
- **WHEN** a caller invokes `tdx-data-more-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.more_info(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened more-info query metadata

### Requirement: Query API CLI SHALL expose cb-info replay entrypoints
The CLI SHALL allow cb-info query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested cb-info command uses replay manager
- **WHEN** a caller invokes `api cb-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.cb_info(...)`
- **AND** the CLI MUST NOT construct or call the live cb-info bridge path

#### Scenario: Flat cb-info command uses replay manager
- **WHEN** a caller invokes `tdx-data-cb-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.cb_info(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened cb-info query metadata

### Requirement: Query API CLI SHALL expose gb-info replay entrypoints
The CLI SHALL allow gb-info query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested gb-info command uses replay manager
- **WHEN** a caller invokes `api gb-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.gb_info(...)`
- **AND** the CLI MUST NOT construct or call the live gb-info bridge path

#### Scenario: Flat gb-info command uses replay manager
- **WHEN** a caller invokes `tdx-data-gb-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.gb_info(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened gb-info query metadata

### Requirement: Query API CLI SHALL expose ipo-info replay entrypoints
The CLI SHALL allow ipo-info query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested ipo-info command uses replay manager
- **WHEN** a caller invokes `api ipo-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.ipo_info(...)`
- **AND** the CLI MUST NOT construct or call the live ipo-info bridge path

#### Scenario: Flat ipo-info command uses replay manager
- **WHEN** a caller invokes `tdx-data-ipo-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.ipo_info(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened ipo-info query metadata

### Requirement: Query API CLI SHALL expose gp-one replay entrypoints
The CLI SHALL allow gp-one query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested gp-one command uses replay manager
- **WHEN** a caller invokes `api gp-one --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.gp_one_data(...)`
- **AND** the CLI MUST NOT construct or call the live gp-one bridge path

#### Scenario: Flat gp-one command uses replay manager
- **WHEN** a caller invokes `tdx-data-gp-one --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.gp_one_data(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened gp-one query metadata

### Requirement: Query API CLI SHALL expose divid-factors replay entrypoints
The CLI SHALL allow divid-factors query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested divid-factors command uses replay manager
- **WHEN** a caller invokes `api divid-factors --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.divid_factors(...)`
- **AND** the CLI MUST NOT construct or call the live divid-factors bridge path

#### Scenario: Flat divid-factors command uses replay manager
- **WHEN** a caller invokes `tdx-data-divid-factors --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.divid_factors(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened divid-factors query metadata

### Requirement: Query API CLI SHALL expose stock transaction by-date replay entrypoints
The CLI SHALL allow stock transaction by-date query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested stock transaction by-date command uses replay manager
- **WHEN** a caller invokes `api stock-transaction-data-by-date --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.stock_transaction_data_by_date(...)`
- **AND** the CLI MUST NOT construct or call the live stock transaction by-date bridge path

#### Scenario: Flat stock transaction by-date command uses replay manager
- **WHEN** a caller invokes `tdx-data-stock-transaction-by-date --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.stock_transaction_data_by_date(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened stock transaction by-date query metadata

### Requirement: Query API CLI SHALL expose market transaction by-date replay entrypoints
The CLI SHALL allow market transaction by-date query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested market transaction by-date command uses replay manager
- **WHEN** a caller invokes `api market-transaction-data-by-date --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.market_transaction_data_by_date(...)`
- **AND** the CLI MUST NOT construct or call the live market transaction by-date bridge path

#### Scenario: Flat market transaction by-date command uses replay manager
- **WHEN** a caller invokes `tdx-data-market-transaction-by-date --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.market_transaction_data_by_date(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened market transaction by-date query metadata

