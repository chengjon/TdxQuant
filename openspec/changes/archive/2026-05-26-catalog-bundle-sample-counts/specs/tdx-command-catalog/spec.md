## ADDED Requirements

### Requirement: Catalog summary SHALL expose bundle sample counts

Catalog summary views SHALL include read-only `task_report_bundle_sample_count`, `submit_once_bundle_sample_count`, and `pingan_bundle_sample_count` fields derived from their bounded visible sample arrays when those arrays are projected, without exposing full bundle manifests or executing catalog entries, bundle steps, task/report commands, submit-once flows, broker probes, or trade operations.

#### Scenario: Summary view includes task/report bundle sample count

- **WHEN** a caller requests a catalog summary view that includes `task_report_bundle_samples`
- **THEN** the summary result MUST include `task_report_bundle_sample_count` equal to the length of `task_report_bundle_samples`
- **AND** `task_report_bundle_count`, `task_report_bundle_step_count`, `task_report_bundle_sample_limit`, and `task_report_bundle_sample_truncated` MUST remain unchanged
- **AND** the summary MUST NOT execute task/report commands or bundle steps

#### Scenario: Summary view includes submit-once bundle sample count

- **WHEN** a caller requests a catalog summary view that includes `submit_once_bundle_samples`
- **THEN** the summary result MUST include `submit_once_bundle_sample_count` equal to the length of `submit_once_bundle_samples`
- **AND** `submit_once_bundle_count`, `submit_once_bundle_step_count`, `submit_once_bundle_sample_limit`, and `submit_once_bundle_sample_truncated` MUST remain unchanged
- **AND** the summary MUST NOT execute submit-once commands, broker probes, trade operations, or bundle steps

#### Scenario: Summary view includes PingAn bundle sample count

- **WHEN** a caller requests a catalog summary view that includes `pingan_bundle_samples`
- **THEN** the summary result MUST include `pingan_bundle_sample_count` equal to the length of `pingan_bundle_samples`
- **AND** `pingan_bundle_count`, `pingan_bundle_step_count`, `pingan_bundle_sample_limit`, and `pingan_bundle_sample_truncated` MUST remain unchanged
- **AND** the summary MUST NOT execute PingAn commands, broker probes, trade operations, or bundle steps
