# tdx-formula-bridge Specification

## Purpose

定义 TongDaXin 公式桥接能力，覆盖指标公式、选股公式、批量执行，以及公式运行所需的数据准备、读取和结构化返回原语。

## Requirements
### Requirement: Formula bridge SHALL expose TongDaXin indicator formulas
The system SHALL expose a bridge command for executing TongDaXin indicator formulas through the official formula interface rather than GUI automation.

#### Scenario: Execute indicator formula
- **WHEN** a caller requests execution of a valid TongDaXin indicator formula with valid input data
- **THEN** the bridge returns structured formula output values

#### Scenario: Indicator formula request includes precision control
- **WHEN** a caller requests indicator formula execution with output precision settings supported by TongDaXin
- **THEN** the bridge returns output values respecting the requested precision

### Requirement: Formula bridge SHALL expose TongDaXin stock-picking formulas
The system SHALL expose a bridge command for executing TongDaXin stock-picking formulas and returning machine-consumable results.

#### Scenario: Execute stock-picking formula
- **WHEN** a caller requests execution of a valid stock-picking formula
- **THEN** the bridge returns structured boolean or matched-symbol results according to the TongDaXin formula semantics

### Requirement: Formula bridge SHALL expose batch formula processing
The system SHALL expose batch execution entrypoints for indicator and stock-picking formulas when the underlying TongDaXin interface supports batch processing.

#### Scenario: Execute batch indicator formula
- **WHEN** a caller requests batch execution of an indicator formula across multiple symbols
- **THEN** the bridge returns structured results for each requested symbol

#### Scenario: Execute batch stock-picking formula
- **WHEN** a caller requests batch execution of a stock-picking formula across multiple symbols
- **THEN** the bridge returns structured results for each requested symbol

### Requirement: Formula bridge SHALL expose formula data setup primitives
The system SHALL expose commands for preparing, setting, and retrieving formula input data required by the TongDaXin formula runtime.

#### Scenario: Set formula data
- **WHEN** a caller provides valid formula input data and metadata
- **THEN** the bridge stores the data in the TongDaXin formula runtime and confirms the accepted configuration

#### Scenario: Read previously set formula data
- **WHEN** a caller requests previously stored formula input data
- **THEN** the bridge returns the stored data in structured JSON form
