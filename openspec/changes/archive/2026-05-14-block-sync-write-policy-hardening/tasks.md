## 1. Policy Contract

- [x] 1.1 Add focused failing tests for write policy mapping and conflict validation.
- [x] 1.2 Implement explicit write policy resolution while preserving `mode`/`dry_run` compatibility.

## 2. Replay And Conflict Feedback

- [x] 2.1 Add focused failing tests for mutation-key replay metadata.
- [x] 2.2 Add focused failing tests for mutation-key conflict metadata.
- [x] 2.3 Harden replay/conflict responses with machine-readable prior/current request metadata.

## 3. Audit And Registry

- [x] 3.1 Add tests for policy metadata in result/audit artifacts.
- [x] 3.2 Update audit payloads and `FUNCTION_TREE.md` status/boundary evidence.

## 4. Verification

- [x] 4.1 Run focused block sync tests.
- [x] 4.2 Run strict OpenSpec validation.
- [x] 4.3 Run `git diff --check`.
