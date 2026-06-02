#!/usr/bin/env python3
"""Clean up formatting of extracted web_docs files - final pass."""

import re
from pathlib import Path

BASE = Path(__file__).resolve().parent / "docs" / "web_docs"


def clean_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    original = text

    # --- Phase 1: Fix code blocks ---

    def clean_code_block(m):
        content = m.group(1)
        lines = content.split("\n")
        cleaned = []
        for line in lines:
            stripped = line.strip()
            # Remove leading backtick at start of code content line
            # Pattern: ` code or `def ... - backtick followed by space or code
            if stripped.startswith("`") and not stripped.startswith("```"):
                # Remove just the leading backtick
                line = line[:len(line) - len(line.lstrip())] + stripped[1:]
                if line.lstrip().startswith(" "):
                    line = line[:len(line) - len(line.lstrip())] + line.lstrip()
            cleaned.append(line)
        return "```\n" + "\n".join(cleaned) + "\n```"

    text = re.sub(r"```\n(.*?)```", clean_code_block, text, flags=re.DOTALL)

    # --- Phase 2: Remove line numbers between code block end and next heading/content ---

    # Pattern: ``` \n 2\n 3\n ... blank line -> ``` \n blank line
    # Line numbers are bare digits possibly with leading space, between ``` and next content
    text = re.sub(
        r"(```\n)(?:\s*\d+\s*\n)+",
        r"\1",
        text,
    )

    # --- Phase 3: Remove navigation blocks ---

    # Remove ← ... → navigation remnants (may have page names between)
    text = re.sub(r"\n\s*←\s*\n.*?→\s*\n", "\n", text, flags=re.DOTALL)
    text = re.sub(r"\n\s*[←→]\s*\n", "\n", text)

    # --- Phase 4: Table separators ---

    def add_table_sep(m):
        header = m.group(1)
        cols = header.count("|") - 1
        sep = "|" + "|".join([" ------ "] * cols) + "|"
        return header + "\n" + sep

    text = re.sub(
        r"^(\|(?:[^|\n]+\|)+)\n(?!\|[\s\-:]+\|)",
        add_table_sep,
        text,
        flags=re.MULTILINE,
    )

    # --- Phase 5: Final cleanup ---

    # Remove trailing whitespace
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Ensure file ends with single newline
    text = text.rstrip("\n") + "\n"

    if text != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    return False


def main():
    files = sorted(BASE.glob("sections/*.md")) + [BASE / "all_docs.md"]
    changed = 0
    for f in files:
        if not f.exists():
            continue
        if clean_file(f):
            print(f"  Cleaned: {f.name}")
            changed += 1
        else:
            print(f"  No change: {f.name}")
    print(f"\nDone: {changed}/{len(files)} files cleaned.")


if __name__ == "__main__":
    main()
