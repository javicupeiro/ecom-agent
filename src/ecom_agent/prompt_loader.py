"""Load Markdown prompts with optional language-specific lookup."""

from __future__ import annotations

from pathlib import Path


def load_prompt(prompts_dir: Path, name: str, lang: str | None = None) -> str:
    """Return the stripped text of a prompt .md file.

    Resolution order:
    1. ``<prompts_dir>/<lang>/<name>.md``  (if *lang* is given and file exists)
    2. ``<prompts_dir>/<name>.md``
    """
    if lang:
        path = prompts_dir / lang / f"{name}.md"
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
    path = prompts_dir / f"{name}.md"
    return path.read_text(encoding="utf-8").strip()
