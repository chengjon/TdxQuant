# review2md Skill

Evidence-driven document review with file-type and doc-type awareness, results saved as Markdown.

## Usage

```
/review2md <file-path> [--arch|--security|--completeness|--consistency|--feasibility|--code] [--detail]
```

No flag = auto-detect.

## Flags

| Flag | Perspective | When to use |
|------|-------------|-------------|
| *(none)* | auto | Infer from file path + content |
| `--arch` | Architecture | System/module design, service boundaries |
| `--security` | Security | APIs touching user data, auth flows |
| `--completeness` | Completeness | Specs, PRDs, requirement docs |
| `--consistency` | Consistency | Multi-author docs, terminology drift |
| `--feasibility` | Feasibility | Proposals, plans, roadmaps |
| `--code` | Code Review | `.py`/`.ts`/`.js` source files |
| `--detail` | *(format)* | Full structured template with scoring |

## Auto-Detection

File type routing by extension:
- `.md` → doc type detection (plan/arch/spec/workflow/proposal)
- `.py`/`.ts`/`.js` → code review
- `.json`/`.yaml`/`.toml` → config review
- `.sql` → schema/migration review

Doc type detection for `.md` (by path keywords + content):
- `plan`/`roadmap`/`milestone` → plan
- `arch`/`design`/`adr`/`system` → arch
- `spec`/`prd`/`req`/`contract` → spec
- `workflow`/`process`/`runbook` → workflow
- `proposal`/`rfc`/`decision` → proposal
- Otherwise → general

## Core Features

1. **Cross-Reference Evidence** — Verifies all referenced files (Glob), functions/classes (Grep), config values (Read) against the live codebase before flagging issues.

2. **Mandatory Checklist** — Each perspective has a structured checklist (e.g., architecture has 9 items: A1-A9). Every item must be marked PASS/FAIL/N/A.

3. **Evidence Citation** — Every finding includes the specific codebase verification result, not just text analysis.

4. **Progress Indicators** — 5-step inline status during execution:
   ```
   1/5 Reading <full-input-path>
   2/5 Detected: <ext> / <doc-type>, perspective: <auto or flag>
   3/5 Cross-referencing <N> files, <M> symbols against codebase...
   4/5 Running <perspective> checklist (<N> items)...
   5/5 Review saved → <full-output-path>
   ```

## Output

- **Location**: Same directory as source file, with `-review` suffix (e.g., `design.md` → `design-review.md`)
- **Default format**: Concise checklist with Summary / Verified / Issues (HIGH/MED/LOW) / Suggestions / Verdict
- **`--detail` format**: Full structured template with Evidence Verification tables, Checklist Results, Scoring (1-5)

Verdict options: `APPROVE` / `APPROVE_WITH_NOTES` / `NEEDS_REVISION` / `REJECT`

## File Location

```
~/.claude/skills/review2md/SKILL.md
```

Global skill — works across all projects.
