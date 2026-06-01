# Domain Docs

This repository uses a single-context domain layout for Matt Pocock engineering skills.

Primary domain files:

- `CONTEXT.md`: project vocabulary, architecture rules, and current pressure points.
- `FUNCTION_TREE.md`: canonical feature registry and status source.
- `docs/adr/`: architecture decision records.
- `openspec/specs/`: durable capability specifications.
- `openspec/changes/archive/`: archived implementation changes and evidence trail.

Consumer rules:

- Read `CONTEXT.md` before architecture, diagnosis, TDD, or issue-planning work.
- Read `FUNCTION_TREE.md` before changing feature status, evidence, or scope.
- Read relevant ADRs before proposing architecture changes.
- Do not treat historical planning docs as status authority when they conflict with `FUNCTION_TREE.md`.
