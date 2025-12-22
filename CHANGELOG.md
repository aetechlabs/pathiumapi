## 0.1.7 - 2025-12-23

### Added
- Basic OpenAPI generation and interactive documentation endpoints: `/openapi.json` and `/docs` (served via a CDN-hosted Swagger UI).
- `scripts/release.py`: release helper that bumps `VERSION`, updates `pyproject.toml` and package `__version__`, prepends `CHANGELOG.md`, creates a git tag, and optionally pushes.

### Changed
- Release process documented in `CONTRIBUTING.md` and a release helper was added to simplify consistent version bumps and tagging.

### Fixed
- CLI robust import handling so `pathiumapi run <module>` works when the app module is outside the CWD.

Additional developer-facing improvements: added short docstrings to public API symbols for better IDE hover help, updated packaging metadata, and produced distribution artifacts (`sdist` and `wheel`).

# Changelog

All notable changes to this project will be documented in this file.

## [0.1.6] - 2025-12-22
### Added
- Improved documentation: expanded `README.md`, `usage.md`, and added `CONTRIBUTING.md` with branching and PR workflow guidance.

### Changed
- Bumped project version to `0.1.6` and updated packaging metadata.
- Published the improved docs release to PyPI (long description sourced from `README.md`).

## [0.1.2] - 2025-12-20
### Changed
- Bumped release to 0.1.2 and prepared PyPI publishing workflow.

## [0.1.1] - 2025-12-20
### Added
- Route parameter converters (e.g., `{id:int}`) with automatic conversion.
- Middleware helpers: `logging_middleware_factory` and `error_middleware`.
- Basic example app at `examples/app.py`.
- `pytest` tests for `Router` and CI workflow (GitHub Actions).
- `README.md` and `PLANNING.md` with quick-win plan.

### Fixed
- Linting (flake8) and typing (mypy) issues in `lilac.py`.

## [0.1.0] - initial
- Initial minimal framework implementation (routing, Request/Response, ASGI app).

