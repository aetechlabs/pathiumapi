# PathiumAPI — Minimal ASGI API Framework

PathiumAPI is a small, synchronous-friendly ASGI-style web framework inspired by
FastAPI and other micro-frameworks. It focuses on a compact, explicit API for
routing, request/response helpers, middleware, and simple route parameter
converters. It's ideal for small services, learning, or as a foundation to
build more opinionated tooling.

Key points
----------
- Minimal, dependency-free core for routing and ASGI handling
- Simple `Request` and `Response` helpers, plus `Response.json()` convenience
- Path parameter converters (e.g. `{id:int}`) and middleware hooks
- Small CLI to scaffold and run apps (`pathiumapi new`, `pathiumapi run`)

Installation
------------
Install from PyPI:

```bash
pip install PathiumAPI
```

Quickstart
----------
Create `app.py`:

```python
from pathiumapi import Pathium, Response

app = Pathium()

@app.get("/")
async def index(req):
	return Response("Hello, PathiumAPI!")

@app.get("/users/{id}")
async def get_user(req, id: str):
	return Response.json({"id": id})
```

Run with `uvicorn`:

```bash
pip install uvicorn
uvicorn app:app --reload
```

Examples and docs
-----------------
- See `examples/app.py` for a minimal app.
- Usage examples are available in `usage.md` (recommended for PyPI long description).

Development
-----------
- Run tests: `python -m pytest -q`
- Static checks (optional): `flake8` and `mypy`

Contributing
------------
See `CONTRIBUTING.md` for branch naming, PR workflow, and guidelines. Open a
PR against `main` when ready and include tests for new functionality.

Changelog
---------
See `CHANGELOG.md` for release notes.

License
-------
MIT

