# Roadmap / Features

This file lists the features requested for pathium and suggested branch names.

1. Developer Tools (separate package: `pathium-cli` / `pathium-tools`)
   - CLI commands: `pathium new <project>`, `pathium run` — branch: `feat/cli`
   - Project scaffolding templates — branch: `feat/cli-scaffold`
   - Code generators for routes and middleware — branch: `feat/codegen`
   - Type hints + mypy stubs distribution — branch: `feat/type-stubs`
   - Config support (`pathium.config.json`) — branch: `feat/config` 

2. Extensions (keep separate packages to keep core small)
   - `pathium-jinja` — Jinja2 templating integration — branch: `ext/jinja`
   - `pathium-auth` — sessions / JWT / OAuth helpers — branch: `ext/auth`
   - `pathium-sql` — DB integrations (SQLAlchemy, Prisma, adapters) — branch: `ext/sql`

3. Packaging & Distribution
   - `pyproject.toml` (done) — `maintenance/post-release`
   - GitHub Actions release publish on tag (added `.github/workflows/publish.yml`)
   - Publish `pathium` and `pathium-cli` to PyPI (requires `PYPI_API_TOKEN` secret)

4. Documentation & Examples
   - Quick start guide + example projects (blog, REST API, file server) — `docs/examples`
   - Middleware examples (logging, CORS, auth) — `docs/middleware`
   - Comparison docs vs Flask / FastAPI — `docs/compare`

