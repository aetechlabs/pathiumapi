## 0.2.0 - 2025-12-24

- Release notes go here.

## 0.1.12 - 2025-12-23

### Added
- Improved README quickstart and CLI documentation to help new users get
	started quickly from PyPI.
- OpenAPI/Pydantic integration: automatic component schema generation for
	request bodies and query parameter models (see `pathiumapi/openapi_pydantic.py`).
- `@validate_query` decorator and OpenAPI integration (`pathiumapi/validation.py`).
- Examples demonstrating query-model docs and validation: `examples/query_app.py`.

### Changed
- Normalized Pydantic schema generation to always include `properties` and
	`required` keys for wider OpenAPI compatibility.
- Improved examples and tests; updated CI build steps to reduce stale-artifact
	upload failures.

### Fixed
- Minor packaging metadata and documentation inconsistencies discovered during
	release preparation.

Developer notes:
- Call `add_openapi(app)` and `add_docs(app)` in your app to expose `/openapi.json`
	and the interactive Swagger UI at `/docs`.

## 0.1.11 - 2025-12-23

### Added
- Auto-generation of OpenAPI query parameter schemas from Pydantic models (`pathiumapi/openapi_pydantic.py`).
- `validate_query` decorator and OpenAPI integration (`pathiumapi/validation.py`, `pathiumapi/_core.py`).
- Tests and an example demonstrating query-model docs (`tests/test_openapi_query.py`, `examples/query_app.py`).

### Changed
- Normalized Pydantic schema generation to always include `properties` and `required` keys for OpenAPI consumption.

Developer notes:
- Visit `/openapi.json` or `/docs` after calling `add_openapi(app)` and `add_docs(app)` to view generated documentation.

## 0.1.10 - 2025-12-23

### Added
- Common middleware: CORS, security headers, and a simple in-memory rate limiter (`pathiumapi/middleware.py`).

### Changed
- Bumped package to `0.1.10`; added tests and an example for middleware.

### Fixed
- None specific to this patch.

Developer notes:
- See `examples/middleware_demo.py` and `tests/test_middleware.py` for usage and tests.


## 0.1.9 - 2025-12-23

### Added
- JWT authentication middleware and helpers: `jwt_middleware_factory` and `create_token`.
- Example auth app at `examples/auth_app.py` demonstrating login and a protected route.

### Changed
- CI: clean `dist/` before building to avoid stale artifacts during uploads.
- CI: enable `skip_existing` on PyPI uploads to tolerate previously-uploaded identical files.

### Fixed
- Packaging and release process improvements; updated docs and release helper.

Developer notes:
- Created GitHub Releases for `v0.1.8` and `v0.1.9` and added release note files under `release-notes/`.
- Added `PyJWT` as a development dependency for auth tests/examples.


## 0.1.8 - 2025-12-23

### Added
- Pydantic integration helpers for easy request body validation via `@validate_body(Model)`.

### Changed
- Improved release process documentation to discourage using `--force` with the release helper; prefer committing or cleaning the working tree before releasing.

### Fixed
- Minor packaging metadata and egg-info consistency fixes applied during release preparation.

Developer notes:
- Added tests for Pydantic validation and included `pydantic>=1.10` as a development dependency.
- Created `feature/pydantic-validation` branch and merged into `main` with validation helpers and tests.

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

