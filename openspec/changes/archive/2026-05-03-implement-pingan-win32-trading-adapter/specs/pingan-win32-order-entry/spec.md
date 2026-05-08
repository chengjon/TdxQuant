## ADDED Requirements

### Requirement: System MUST inspect the Ping An Securities window tree before trading
The system SHALL provide a read-only inspection capability that enumerates the Ping An Securities main window and its child controls before any order entry workflow is enabled.

#### Scenario: Operator runs inspect on an open client
- **WHEN** the Ping An Securities client is open and the operator runs the inspection command
- **THEN** the system SHALL return the matched main window and a structured list of child controls including handle, class name, text, parent handle, and bounds

### Requirement: System MUST detect buy-page controls before placing an order
The system SHALL identify the stock code field, optional price field, quantity field, and buy button for the standard buy page before executing a buy request.

#### Scenario: All required controls are found
- **WHEN** the client is logged in and displaying the standard buy order page
- **THEN** the system SHALL return a successful detection result containing the matched handles for the code field, quantity field, and buy button

#### Scenario: Required controls are missing
- **WHEN** the client is not on the standard buy order page or the control tree does not match known rules
- **THEN** the system SHALL return a structured detection failure and SHALL NOT attempt order entry

### Requirement: Buy requests MUST validate operator input before sending Win32 messages
The system SHALL validate the request payload before calling `WM_SETTEXT` or `BM_CLICK`.

#### Scenario: Quantity is not a board-lot multiple
- **WHEN** a buy request contains a quantity that is not a valid lot size for the configured market rules
- **THEN** the system SHALL reject the request before any control text is modified

#### Scenario: Required buy fields are valid
- **WHEN** a buy request contains a valid stock code, quantity, and any required price value
- **THEN** the system SHALL continue to Win32 message execution using the detected controls

### Requirement: Buy execution MUST support a non-click verification mode
The system SHALL support a verification mode that fills detected controls without sending the final buy-button click.

#### Scenario: Operator runs dry-run buy verification
- **WHEN** the operator invokes buy with dry-run enabled
- **THEN** the system SHALL write the detected code, price, and quantity fields but SHALL NOT send `BM_CLICK` to the buy button

### Requirement: Buy execution MUST return structured execution results
The system SHALL return a structured result that records precondition status, matched controls, executed actions, warnings, and any failure reason.

#### Scenario: Buy request is executed
- **WHEN** the system completes a non-dry-run buy request
- **THEN** the result SHALL indicate which fields were written, whether the buy button click was sent, and any follow-up action required from the operator
