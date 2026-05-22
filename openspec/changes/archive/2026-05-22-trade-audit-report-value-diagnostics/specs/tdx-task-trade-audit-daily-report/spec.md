## ADDED Requirements

### Requirement: Daily trade audit report SHALL expose requested-value diagnostics
The daily trade audit report SHALL include a read-only requested-value diagnostic derived only from existing audit result payload fields.

#### Scenario: Caller requests a daily report with priced audit entries
- **WHEN** a caller generates a trade audit daily report from audit entries that contain numeric `price` and `quantity`
- **THEN** the result includes `value_diagnostics`
- **AND** the diagnostic reports priced and unpriced entry counts
- **AND** the diagnostic reports requested order value by status and method

#### Scenario: Daily requested value remains a diagnostic boundary
- **WHEN** the daily report includes `value_diagnostics`
- **THEN** the diagnostic states that requested order value is calculated from `price * quantity`
- **AND** the diagnostic does not claim filled value, execution quality, fees, account balances, or PnL
