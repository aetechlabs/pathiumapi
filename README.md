# PathiumAPI — Minimal ASGI API Framework

PathiumAPI is a tiny, synchronous-friendly ASGI-style web framework inspired
by FastAPI and other micro-frameworks. It provides routing, request/
response helpers, middleware, and simple route parameter converters.

Quick start
-----------

1. Create an app in `examples/app.py` (see the example in this repo).
2. Run using an ASGI server such as `uvicorn`:

```bash
python -m pip install uvicorn
uvicorn examples.app:app --reload
```

Example
-------
See [examples/app.py](examples/app.py) for a minimal app demonstrating
routing, path converters and middleware.

Development
-----------
- Run tests: `python -m pytest -q`
- Static checks: `flake8 PathiumAPI.py` and `mypy --ignore-missing-imports PathiumAPI.py`

Contributing
------------
PRs welcome. Follow the branch naming in `PLANNING.md` and open a PR
against `main` when ready.
