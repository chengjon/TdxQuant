## Context

PingAn `dialog_readiness` already checks confirm dialog lookup, result dialog lookup, and result confirm-button lookup. The lifecycle gate status records these checks as read-only evidence and explicitly leaves exception popup handling and retry policy as remaining gates.

## Goals / Non-Goals

**Goals:**

- Add a read-only `exception_popup_lookup` check when result dialog readiness is requested.
- Detect exception/error-like result dialogs from passive text payload evidence.
- Include the check in `desktop_lifecycle_gate_status` without writing trade state or audit artifacts.
- Preserve D-07/D-08 partial status semantics in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not close exception popups.
- Do not click result buttons.
- Do not implement retry, backoff, recovery, or live acceptance.
- Do not mark D-07 or D-08 `[已实现]`.

## Decisions

- Reuse the existing result dialog lookup path. This avoids a second desktop traversal and keeps exception popup evidence scoped to a currently visible result dialog.
- Classify the popup using text payload evidence from `_extract_dialog_text_payload_from_sources`. The signal is intentionally passive and heuristic: it reports whether exception-like keywords are present.
- Keep `exception_popup_handling` in remaining lifecycle gates. A lookup/classification signal is evidence, not actual handling.

## Risks / Trade-offs

- [Risk] Keyword classification could be incomplete. -> Expose matched keywords and raw text payload in the check detail, and avoid claiming handling.
- [Risk] A visible result dialog might be normal success/rejection, not exception. -> Report the check as `warning` or `failed` depending on `require_visible` only when no result dialog exists; otherwise distinguish `exception_detected` in detail.
- [Risk] Consumers could treat lookup evidence as recovery. -> Boundary text and FUNCTION_TREE notes state that retry/recovery/live acceptance remain out of scope.

