# Roadmap / Features

This file lists the features requested for Lilac and suggested branch names.

1. Developer Tools (separate package: `lilac-cli` / `lilac-tools`)
   - CLI commands: `lilac new <project>`, `lilac run` — branch: `feat/cli`
   - Project scaffolding templates — branch: `feat/cli-scaffold`
   - Code generators for routes and middleware — branch: `feat/codegen`
   - Type hints + mypy stubs distribution — branch: `feat/type-stubs`
   - Config support (`lilac.config.json`) — branch: `feat/config` 

2. Extensions (keep separate packages to keep core small)
   - `lilac-jinja` — Jinja2 templating integration — branch: `ext/jinja`
   - `lilac-auth` — sessions / JWT / OAuth helpers — branch: `ext/auth`
   - `lilac-sql` — DB integrations (SQLAlchemy, Prisma, adapters) — branch: `ext/sql`

3. Packaging & Distribution
   - `pyproject.toml` (done) — `maintenance/post-release`
   - GitHub Actions release publish on tag (added `.github/workflows/publish.yml`)
   - Publish `lilac` and `lilac-cli` to PyPI (requires `PYPI_API_TOKEN` secret)

4. Documentation & Examples
   - Quick start guide + example projects (blog, REST API, file server) — `docs/examples`
   - Middleware examples (logging, CORS, auth) — `docs/middleware`
   - Comparison docs vs Flask / FastAPI — `docs/compare`

