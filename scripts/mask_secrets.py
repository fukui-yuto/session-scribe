"""Detect and mask sensitive information in text content."""
import io
import re
import os
import sys
from typing import Optional

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


_USERNAME = os.getenv("USERNAME") or os.getenv("USER") or "user"


def _build_patterns() -> list[tuple[str, str, re.Pattern]]:
    """Build list of (name, replacement, compiled_pattern) tuples."""
    patterns = [
        # API keys - common prefixes
        (
            "api_key",
            "[REDACTED_API_KEY]",
            re.compile(
                r"""(?:sk-[a-zA-Z0-9]{20,}"""
                r"""|AIza[a-zA-Z0-9_-]{35}"""
                r"""|ghp_[a-zA-Z0-9]{36}"""
                r"""|gho_[a-zA-Z0-9]{36}"""
                r"""|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}"""
                r"""|glpat-[a-zA-Z0-9_-]{20,}"""
                r"""|xox[bsrap]-[a-zA-Z0-9-]{10,}"""
                r"""|AKIA[A-Z0-9]{16}"""
                r"""|ya29\.[a-zA-Z0-9_-]{50,}"""
                r"""|Bearer\s+[a-zA-Z0-9._-]{20,})"""
            ),
        ),
        # Email addresses
        (
            "email",
            "[REDACTED_EMAIL]",
            re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        ),
        # Private IPv4 addresses
        (
            "private_ip",
            "[REDACTED_IP]",
            re.compile(
                r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
                r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
                r"|192\.168\.\d{1,3}\.\d{1,3})\b"
            ),
        ),
        # SSH private keys
        (
            "ssh_key",
            "[REDACTED_SSH_KEY]",
            re.compile(
                r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
                r"[\s\S]*?"
                r"-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
            ),
        ),
        # Passwords in connection strings / env vars
        (
            "password",
            "[REDACTED_PASSWORD]",
            re.compile(
                r"""(?:password|passwd|pwd|secret|token)\s*[=:]\s*['"]?[^\s'"]{8,}""",
                re.IGNORECASE,
            ),
        ),
        # Windows user paths
        (
            "user_path_win",
            r"C:\\Users\\[USER]",
            re.compile(
                r"C:\\Users\\" + re.escape(_USERNAME),
                re.IGNORECASE,
            ),
        ),
        # Unix user paths
        (
            "user_path_unix",
            "/home/[USER]",
            re.compile(
                r"(?:/home/|/Users/)" + re.escape(_USERNAME),
            ),
        ),
    ]
    return patterns


_PATTERNS = _build_patterns()


def mask_text(
    text: str,
    extra_patterns: Optional[list[tuple[str, str, re.Pattern]]] = None,
) -> tuple[str, list[dict]]:
    """Mask sensitive information in the given text.

    Args:
        text: The text to mask.
        extra_patterns: Additional (name, replacement, pattern) tuples.

    Returns:
        Tuple of (masked_text, list of dicts describing what was masked).
    """
    masked = text
    findings = []
    patterns = _PATTERNS + (extra_patterns or [])

    for name, replacement, pattern in patterns:
        matches = list(pattern.finditer(masked))
        if matches:
            findings.append({
                "type": name,
                "count": len(matches),
            })
            masked = pattern.sub(replacement, masked)

    return masked, findings


def mask_session_data(session_data: dict) -> tuple[dict, list[dict]]:
    """Mask sensitive information in parsed session data.

    Args:
        session_data: Output from parse_session().

    Returns:
        Tuple of (masked_session_data, all_findings).
    """
    import copy
    data = copy.deepcopy(session_data)
    all_findings = []

    data["cwd"], findings = mask_text(data["cwd"])
    all_findings.extend(findings)

    for msg in data["messages"]:
        msg["content"], findings = mask_text(msg["content"])
        all_findings.extend(findings)

        for tu in msg["tool_uses"]:
            input_str = str(tu["input"])
            masked_str, findings = mask_text(input_str)
            all_findings.extend(findings)
            if masked_str != input_str:
                tu["input"] = {"masked": masked_str}

    return data, all_findings


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    masked, findings = mask_text(text)
    print(masked)
    if findings:
        print("\n--- Masking Summary ---", file=sys.stderr)
        for f in findings:
            print(f"  {f['type']}: {f['count']} occurrences", file=sys.stderr)
