from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
IGNORE = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "target",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    "data",
}
BINARY = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".zip",
    ".exe",
    ".dll",
    ".pdb",
    ".db",
    ".sqlite",
    ".woff",
    ".woff2",
    ".ttf",
}
PATTERNS = {
    "personal email": re.compile(r"mayconxz00dev@gmail\.com", re.I),
    "personal phone": re.compile(r"96481[- .]?0480", re.I),
    "private IPv4": re.compile(
        r"(?<!\d)(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?!\d)"
    ),
    "OpenAI-like secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub PAT-like secret": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}

findings: list[str] = []
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if any(part in IGNORE for part in path.parts) or path.suffix.lower() in BINARY:
        continue
    try:
        text = path.read_text("utf-8")
    except UnicodeDecodeError:
        continue
    for label, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(f"{path.relative_to(ROOT)}:{line}: {label}")

if findings:
    print("Public-safety scan failed:")
    print("\n".join(findings))
    raise SystemExit(1)

print("Public-safety scan passed.")
