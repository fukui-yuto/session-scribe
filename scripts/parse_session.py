"""Parse Claude Code session JSONL logs into structured conversation data."""
import io
import json
import os
import glob
import sys
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


CLAUDE_PROJECTS_DIR = os.path.expanduser("~/.claude/projects")


def get_session_files(project_path: Optional[str] = None) -> list[dict]:
    """List available session files, optionally filtered by project path.

    Args:
        project_path: If given, filter to sessions from this project directory.

    Returns:
        List of dicts with keys: path, project, session_id, modified
    """
    sessions = []
    if not os.path.isdir(CLAUDE_PROJECTS_DIR):
        return sessions

    for project_dir in os.listdir(CLAUDE_PROJECTS_DIR):
        full_project_dir = os.path.join(CLAUDE_PROJECTS_DIR, project_dir)
        if not os.path.isdir(full_project_dir):
            continue

        if project_path:
            normalized = project_path.replace("\\", "/").replace(":", "").replace("/", "-")
            encoded = "C--" + normalized.lstrip("C-").lstrip("-")
            if project_dir != encoded and project_dir != normalized:
                continue

        for jsonl_file in glob.glob(os.path.join(full_project_dir, "*.jsonl")):
            session_id = os.path.basename(jsonl_file).replace(".jsonl", "")
            sessions.append({
                "path": jsonl_file,
                "project": project_dir,
                "session_id": session_id,
                "modified": os.path.getmtime(jsonl_file),
            })

    sessions.sort(key=lambda s: s["modified"], reverse=True)
    return sessions


def parse_session(jsonl_path: str) -> dict:
    """Parse a single session JSONL file into structured data.

    Returns:
        Dict with keys: session_id, project, cwd, git_branch,
        start_time, end_time, messages
    """
    records = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    session_id = ""
    cwd = ""
    git_branch = ""
    start_time = ""
    end_time = ""

    for rec in records:
        if rec.get("type") in ("user", "assistant"):
            session_id = rec.get("sessionId", "")
            cwd = rec.get("cwd", "")
            git_branch = rec.get("gitBranch", "")
            start_time = rec.get("timestamp", "")
            break

    for rec in reversed(records):
        ts = rec.get("timestamp")
        if ts:
            end_time = ts
            break

    messages = []
    for rec in records:
        rec_type = rec.get("type")
        if rec_type not in ("user", "assistant"):
            continue

        msg = rec.get("message", {})
        role = msg.get("role", rec_type)
        timestamp = rec.get("timestamp", "")

        content_parts = []
        tool_uses = []

        raw_content = msg.get("content", "")
        if isinstance(raw_content, str):
            if raw_content and raw_content != "[Request interrupted by user]":
                content_parts.append(raw_content)
        elif isinstance(raw_content, list):
            for item in raw_content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "text":
                    text = item.get("text", "")
                    if text and text != "[Request interrupted by user]":
                        content_parts.append(text)
                elif item.get("type") == "tool_use":
                    tool_uses.append({
                        "tool": item.get("name", ""),
                        "input": item.get("input", {}),
                    })
                elif item.get("type") == "tool_result":
                    result_content = item.get("content", "")
                    if isinstance(result_content, list):
                        for rc in result_content:
                            if isinstance(rc, dict) and rc.get("type") == "text":
                                content_parts.append(
                                    f"[Tool Result]: {rc.get('text', '')}"
                                )
                    elif isinstance(result_content, str) and result_content:
                        content_parts.append(f"[Tool Result]: {result_content}")

        if not content_parts and not tool_uses:
            continue

        messages.append({
            "role": role,
            "content": "\n".join(content_parts),
            "timestamp": timestamp,
            "tool_uses": tool_uses,
        })

    project = os.path.basename(os.path.dirname(jsonl_path))

    return {
        "session_id": session_id,
        "project": project,
        "cwd": cwd,
        "git_branch": git_branch,
        "start_time": start_time,
        "end_time": end_time,
        "messages": messages,
    }


def format_conversation(session_data: dict) -> str:
    """Format parsed session data into a readable conversation transcript.

    This output is fed to Claude for article structuring.
    """
    lines = []
    lines.append(f"# Session: {session_data['session_id']}")
    lines.append(f"Project: {session_data['project']}")
    lines.append(f"Directory: {session_data['cwd']}")
    lines.append(f"Branch: {session_data['git_branch']}")
    lines.append(f"Time: {session_data['start_time']} ~ {session_data['end_time']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for msg in session_data["messages"]:
        role_label = "USER" if msg["role"] == "user" else "ASSISTANT"
        lines.append(f"## [{role_label}] ({msg['timestamp']})")
        lines.append("")
        if msg["content"]:
            lines.append(msg["content"])
            lines.append("")
        for tu in msg["tool_uses"]:
            tool_name = tu["tool"]
            tool_input = tu["input"]
            if tool_name in ("Read", "Glob", "Grep"):
                lines.append(f"**Tool: {tool_name}** - {json.dumps(tool_input, ensure_ascii=False)[:200]}")
            elif tool_name == "Bash":
                cmd = tool_input.get("command", "")
                lines.append(f"**Tool: Bash** - `{cmd[:200]}`")
            elif tool_name in ("Write", "Edit"):
                fp = tool_input.get("file_path", "")
                lines.append(f"**Tool: {tool_name}** - {fp}")
            else:
                lines.append(f"**Tool: {tool_name}**")
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sessions = get_session_files()
        print(f"Found {len(sessions)} sessions:\n")
        for s in sessions[:10]:
            print(f"  {s['project']} / {s['session_id']}")
            print(f"    Path: {s['path']}")
            print()
    else:
        path = sys.argv[1]
        data = parse_session(path)
        print(format_conversation(data))
