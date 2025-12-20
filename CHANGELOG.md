# Changelog

All notable changes to this project will be documented in this file.

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

## [0.1.2] - 2025-12-20
### Changed
- Bumped release to 0.1.2 and prepared PyPI publishing workflow.

