Branching & Contribution Guidelines

This project uses a simple feature-branch workflow to develop new features, fixes, and documentation.

Branch naming
- `main` / `master`: stable production-ready branch.
- `feature/<short-description>`: new features.
- `fix/<short-description>`: bug fixes.
- `docs/<short-description>`: documentation changes.

Workflow
1. Create a branch from `main`: `git checkout -b feature/my-new-endpoint`
2. Implement changes and include or update tests where appropriate.
3. Commit logically-scoped changes with clear messages.
4. Push branch: `git push origin feature/my-new-endpoint`.
5. Open a Pull Request against `main`, include description, rationale, and any migration notes.
6. Get at least one reviewer approval, address feedback, then merge (Squash & merge or Merge commit depending on repo policy).

Versioning
- Follow semantic versioning for releases. Patch bumps for small fixes, minor bumps for backward-compatible features, and major bumps for breaking changes.

Testing & CI
- Run existing tests locally before opening a PR: `pytest -q`.

Documentation
- Keep `usage.md` and `README.md` up to date; include examples and CLI usage.

Questions
- If you're unsure about API changes, open a discussion or draft PR so maintainers can give feedback early.
