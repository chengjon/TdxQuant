## Context

`FUNCTION_TREE.md` carries feature status, evidence, and boundary text in one registry. The current validator checks row shape, status vocabulary, pending-state wording, OpenSpec evidence references, and the absence of a root `ROADMAP.md`. Local evidence paths are still unchecked, so a stale literal path can survive in the registry even though the evidence no longer exists.

## Goals / Non-Goals

**Goals:**

- Validate explicit, literal local evidence paths in feature row evidence cells.
- Keep the validator deterministic and repository-local.
- Make errors point to the row id and missing path.

**Non-Goals:**

- Do not interpret arbitrary prose, code symbols, module names, command examples, or glob patterns as mandatory paths.
- Do not execute tests, import modules, or prove feature availability.
- Do not validate runtime-generated directories whose evidence intentionally uses wildcards.

## Decisions

- Add a small evidence-path extractor beside the existing OpenSpec evidence extractor. It will inspect backtick-delimited values only, because the registry already uses backticks for concrete files, directories, commands, symbols, and OpenSpec ids.
- Accept only repository-relative literals with known evidence prefixes such as `tests/`, `scripts/`, `runtime/`, `tdxquant/`, `docs/`, `openspec/specs/`, and `openspec/changes/archive/`. This excludes command names, function names, package names, and prose fragments.
- Skip values containing glob metacharacters, shell whitespace, option prefixes, or trailing wildcards. These remain descriptive evidence, not existence assertions.
- Resolve candidates beneath the repository root and reject path traversal. Existing files and directories both satisfy the check.

## Risks / Trade-offs

- A real stale path written without backticks will not be caught. This is intentional to avoid false positives in Chinese prose and mixed evidence cells.
- A generated evidence directory represented as a glob will not be checked. The registry can still cite a stable parent directory when existence should be enforced.
- Prefix allowlisting means new evidence roots must be added deliberately before they become mechanically checked.
