Branching & Contribution Guidelines

This project uses a simple feature-branch workflow to develop new features, fixes, and documentation.

Branch naming

Workflow
1. Create a branch from `main`: `git checkout -b feature/my-new-endpoint`
2. Implement changes and include or update tests where appropriate.
3. Commit logically-scoped changes with clear messages.
4. Push branch: `git push origin feature/my-new-endpoint`.
5. Open a Pull Request against `main`, include description, rationale, and any migration notes.
6. Get at least one reviewer approval, address feedback, then merge (Squash & merge or Merge commit depending on repo policy).

Versioning
- Run existing tests locally before opening a PR: `pytest -q`.
## Releasing

We expect the following for a release:

- Bump the version and update changelog for each release.
- A helper script is provided at `scripts/release.py` to automate the common steps.

Basic usage:

```bash
# bump patch, create commit and tag locally (dry-run without pushing):
python scripts/release.py --bump patch

# bump minor and push commit + tag to origin:
python scripts/release.py --bump minor --push
```

The script updates `VERSION`, `pyproject.toml`, and `pathiumapi/_core.py`,
prepends a changelog entry to `CHANGELOG.md`, creates a commit and an annotated
tag. Use `--force` to allow running with uncommitted changes.

If you prefer manual steps, follow the previous process: bump `VERSION`,
update `pyproject.toml` and `pathiumapi/_core.py`, add a `CHANGELOG.md` entry,
commit, tag `vX.Y.Z`, and push the tag.

Documentation
- Keep `usage.md` and `README.md` up to date; include examples and CLI usage.

Questions
- If you're unsure about API changes, open a discussion or draft PR so maintainers can give feedback early.
