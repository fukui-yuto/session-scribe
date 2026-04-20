"""Save structured article drafts to the local knowledge base."""
import io
import os
import re
import sys
from datetime import datetime

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from pathlib import Path


DEFAULT_OUTPUT_DIR = os.environ.get(
    "SESSION_SCRIBE_OUTPUT_DIR",
    os.path.expanduser("~/knowledge-log"),
)


def sanitize_filename(title: str) -> str:
    """Convert a title into a safe filename."""
    safe = re.sub(r'[<>:"/\\|?*]', "", title)
    safe = re.sub(r"\s+", "-", safe.strip())
    safe = re.sub(r"-+", "-", safe)
    safe = safe.strip("-")
    if len(safe) > 80:
        safe = safe[:80].rstrip("-")
    return safe


def save_draft(
    content: str,
    title: str,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    session_id: str = "",
    project: str = "",
) -> str:
    """Save a draft article to the output directory.

    Args:
        content: The Markdown content of the article.
        title: The article title (used for filename).
        output_dir: Directory to save to.
        session_id: Original session ID for reference.
        project: Project name for organization.

    Returns:
        The full path of the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_title = sanitize_filename(title)
    filename = f"{date_str}_{safe_title}.md"

    filepath = os.path.join(output_dir, filename)

    # Avoid overwriting existing files
    if os.path.exists(filepath):
        counter = 1
        while os.path.exists(filepath):
            filename = f"{date_str}_{safe_title}_{counter}.md"
            filepath = os.path.join(output_dir, filename)
            counter += 1

    footer_lines = [
        "",
        "---",
        "",
        "<!-- session-scribe metadata",
        f"session_id: {session_id}",
        f"project: {project}",
        f"generated: {datetime.now().isoformat()}",
        f"tool: session-scribe",
        "-->",
    ]

    full_content = content.rstrip() + "\n" + "\n".join(footer_lines) + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    return filepath


if __name__ == "__main__":
    test_content = """# Test Article

## Environment
- OS: Windows 11
- Python: 3.12

## Problem
Test problem description.

## Solution
Test solution.

## Learnings
Test learnings.
"""
    path = save_draft(
        content=test_content,
        title="Test Article",
        session_id="test-session-123",
        project="test-project",
    )
    print(f"Saved to: {path}")
