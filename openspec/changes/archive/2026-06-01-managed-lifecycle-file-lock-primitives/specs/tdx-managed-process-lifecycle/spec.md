## ADDED Requirements

### Requirement: Managed process lifecycle SHALL expose local file lock primitives
The managed process lifecycle module SHALL provide shared local file lock primitives for lifecycle state/control files. The primitives MUST support non-blocking acquisition, a blocked outcome when the lock is already held, release of acquired locks, and stable diagnostics that identify the path, strategy, acquisition state, reason code, and managed lifecycle provenance.

#### Scenario: File lock is acquired and released
- **WHEN** a caller acquires an unlocked lifecycle lock path through the managed lifecycle primitive and then releases it
- **THEN** the acquire result MUST report the normalized lock path, `lock_acquired=true`, an acquired reason code, and managed lifecycle provenance including the `file_lock` primitive
- **AND** the release result MUST report `lock_released=true` for the same normalized lock path

#### Scenario: File lock acquisition is blocked
- **WHEN** a caller attempts to acquire a lifecycle lock path that is already held by another active handle
- **THEN** the acquire result MUST report the normalized lock path, `lock_acquired=false`, a lock-held reason code, and managed lifecycle provenance including the `file_lock` primitive
