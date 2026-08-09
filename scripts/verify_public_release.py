#!/usr/bin/env python3
"""Fail closed when a community package contains private configuration."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


LIVE_NOTION_TOKEN = re.compile(r"\bntn_" + r"[A-Za-z0-9_-]{20,}\b")
LOCAL_MACHINE_PATH = re.compile(r"(?:file:///)?/" + "Users/")
NOTION_IDENTIFIER = re.compile(
    r"\b[a-f0-9]{32}\b|\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b",
    re.IGNORECASE,
)
EMAIL_ADDRESS = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
EXAMPLE_EMAIL_DOMAINS = {"example.com", "example.org", "example.net"}


def findings_for_text(text: str) -> list[str]:
    findings: list[str] = []
    if LIVE_NOTION_TOKEN.search(text):
        findings.append("live Notion token")
    if LOCAL_MACHINE_PATH.search(text):
        findings.append("local-machine path")
    if NOTION_IDENTIFIER.search(text):
        findings.append("Notion-style identifier")
    if any(match.group(1).lower() not in EXAMPLE_EMAIL_DOMAINS for match in EMAIL_ADDRESS.finditer(text)):
        findings.append("non-example email address")
    return findings


def audit_directory(root: Path) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    ignored_directories = {".git", "__pycache__", ".pytest_cache"}
    for path in sorted(
        candidate
        for candidate in root.rglob("*")
        if candidate.is_file() and not ignored_directories.intersection(candidate.parts)
    ):
        result = findings_for_text(path.read_text(encoding="utf-8", errors="ignore"))
        if result:
            findings[path.relative_to(root).as_posix()] = result
    return findings


def git_output(root: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def audit_reachable_history(root: Path) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    revisions = git_output(root, "rev-list", "--all").decode().splitlines()
    for revision in revisions:
        paths = git_output(root, "ls-tree", "-r", "--name-only", revision).decode().splitlines()
        for path in paths:
            content = git_output(root, "show", f"{revision}:{path}").decode("utf-8", errors="ignore")
            result = findings_for_text(content)
            if result:
                findings[f"{revision[:12]}:{path}"] = result
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a Notion community skill before public release.")
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--history", action="store_true", help="also inspect every reachable Git revision")
    parser.add_argument("--json", action="store_true", help="emit file labels and issue categories as JSON")
    arguments = parser.parse_args()
    root = arguments.root.resolve()

    findings = {"working_tree": audit_directory(root)}
    if arguments.history:
        findings["history"] = audit_reachable_history(root)

    has_findings = any(findings_by_scope for findings_by_scope in findings.values())
    if arguments.json:
        print(json.dumps(findings, indent=2, sort_keys=True))
    elif has_findings:
        for scope, findings_by_scope in findings.items():
            for path, categories in findings_by_scope.items():
                print(f"FAIL {scope}: {path} ({', '.join(categories)})")
    else:
        print("PASS public release audit: no private configuration detected")
    return 1 if has_findings else 0


if __name__ == "__main__":
    sys.exit(main())
