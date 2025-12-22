#!/usr/bin/env python3
"""Release helper: bump version, update files, changelog, and create git tag.

Usage:
  python scripts/release.py --bump patch [--push]
  python scripts/release.py --version 1.2.3 --push

By default this will update `VERSION`, `pyproject.toml`, and
`pathiumapi/_core.py`, prepend a changelog entry in `CHANGELOG.md`,
commit the changes, and create an annotated tag `vX.Y.Z` locally. Use
`--push` to push commit and tag to origin.
"""
from __future__ import annotations

import argparse
import datetime
import re
import subprocess
from pathlib import Path
from typing import Tuple


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
PYPROJECT = ROOT / "pyproject.toml"
CORE = ROOT / "pathiumapi" / "_core.py"
CHANGELOG = ROOT / "CHANGELOG.md"


def read_version() -> str:
    return VERSION_FILE.read_text(encoding='utf8').strip()


def bump_version(current: str, part: str) -> str:
    major, minor, patch = (int(x) for x in current.split("."))
    if part == "patch":
        patch += 1
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError("unknown bump part")
    return f"{major}.{minor}.{patch}"


def replace_in_file(path: Path, pattern: str, repl: str) -> None:
    txt = path.read_text(encoding='utf8')
    new = re.sub(pattern, repl, txt, flags=re.M)
    path.write_text(new, encoding='utf8')


def prepend_changelog(version: str) -> None:
    today = datetime.date.today().isoformat()
    header = f"## {version} - {today}\n\n- Release notes go here.\n\n"
    if CHANGELOG.exists():
        content = CHANGELOG.read_text(encoding='utf8')
    else:
        content = "# Changelog\n\n"
    CHANGELOG.write_text(header + content, encoding='utf8')


def git_has_uncommitted() -> bool:
    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return bool(res.stdout.strip())


def run(cmd: list[str]):
    print("$", " ".join(cmd))
    subprocess.check_call(cmd)


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--bump", choices=("patch", "minor", "major"))
    g.add_argument("--version")
    p.add_argument("--push", action="store_true", help="push commit and tag to origin")
    p.add_argument("--force", action="store_true", help="allow with uncommitted changes")
    args = p.parse_args()

    if git_has_uncommitted() and not args.force:
        print("Uncommitted changes detected. Commit or use --force to continue.")
        raise SystemExit(1)

    current = read_version()
    if args.version:
        new_version = args.version
    else:
        new_version = bump_version(current, args.bump)

    print(f"Bumping version: {current} -> {new_version}")

    # Update VERSION
    VERSION_FILE.write_text(new_version + "\n", encoding='utf8')

    # Update pyproject.toml version = "x.y.z"
    replace_in_file(PYPROJECT, r'version\s*=\s*"[^"]+"', f'version = "{new_version}"')

    # Update package __version__ in pathiumapi/_core.py
    replace_in_file(CORE, r'__version__\s*=\s*"[^"]+"', f'__version__ = "{new_version}"')

    # Prepend changelog entry
    prepend_changelog(new_version)

    # Commit and tag
    run(["git", "add", "VERSION", str(PYPROJECT), str(CORE), str(CHANGELOG)])
    run(["git", "-c", "commit.gpgSign=false", "commit", "-m", f"release: {new_version}"])
    run(["git", "tag", "-a", f"v{new_version}", "-m", f"Release {new_version}"])

    if args.push:
        run(["git", "push", "origin", "HEAD"])
        run(["git", "push", "origin", f"v{new_version}"])

    print("Done.")


if __name__ == "__main__":
    main()
