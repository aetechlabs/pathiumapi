# PathiumAPI — Minimal ASGI API Framework

**Version 0.2.0** | [GitHub](https://github.com/aetechlabs/pathiumapi) | [PyPI](https://pypi.org/project/PathiumAPI/)

PathiumAPI is a small, synchronous-friendly ASGI-style web framework inspired by
FastAPI and other micro-frameworks. It focuses on a compact, explicit API for
routing, request/response helpers, middleware, and simple route parameter
converters. It's ideal for small services, learning, or as a foundation to
build more opinionated tooling.

Key Features
------------
- **Minimal Core**: Dependency-free routing and ASGI handling
- **Request/Response Helpers**: Simple `Request` and `Response` objects with JSON support
- **Path Converters**: Type-aware parameter conversion (e.g. `{id:int}`)
- **Pydantic Integration**: Request body and query parameter validation with `@validate_body` and `@validate_query`
- **OpenAPI Support**: Auto-generated OpenAPI 3.0 specs and interactive Swagger UI docs
- **Authentication**: JWT middleware and helpers for protected routes
- **Built-in Middleware**: CORS, security headers, rate limiting, logging, and error handling
- **CLI Tools**: Scaffold and run apps with `pathiumapi new` and `pathiumapi run`
 - **CLI Tools & Runner**: Scaffold and run apps with `pathiumapi new` and
     `pathiumapi run` — a built-in, purpose-built runner so you don't need a
     separate `uvicorn` command to run development servers. The CLI also
     provides a small scaffolding helper to create a new `pathiumapi` project.

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
from pydantic import BaseModel

app = Pathium()

class User(BaseModel):
    name: str
    email: str

@app.get("/")
async def index(req):
    return Response("Hello, PathiumAPI!")

@app.get("/users/{id:int}")
async def get_user(req, id: int):
    return Response.json({"id": id, "name": f"User {id}"})

@app.post("/users")
@app.validate_body(User)
async def create_user(req):
    user_data = req.validated_body
    return Response.json({"created": user_data.dict()}, status=201)
```

Run and manage your app with the built-in `pathiumapi` CLI

```bash
# install the package (if not already installed)
pip install PathiumAPI
```

Quick CLI workflow
------------------

- Scaffold a new app:

```bash
pathiumapi new myapp
cd myapp
```

- Run the app (looks for `app.py` with an `app` object):

```bash
pathiumapi run
# or run a folder containing app.py from anywhere
pathiumapi run path/to/myapp
```

- Generate scaffolding (route stub example):

```bash
# creates routes/users.py and attempts to auto-register in app.py
pathiumapi generate route users --path /users --method get
```

Notes
-----
- `pathiumapi run` will use `uvicorn` under-the-hood if it is installed; if
    `uvicorn` is not available the CLI will ask you to `pip install uvicorn`.
- The CLI's `run` command expects a folder with an `app.py` file. It does not
    take a module argument; pass the folder path instead.
- If you want live reload you can either install `uvicorn` and run it directly
    with `uvicorn app:app --reload`, or you can add a `--reload` forwarding flag to
    `pathiumapi run` like so: `pathiumapi run myapp --reload`.

Visit `http://localhost:8000/docs` (the built-in Swagger UI) for interactive API documentation!

Examples and Documentation
--------------------------

### Available Examples
- **`examples/app.py`** — Minimal app with basic routing
- **`examples/auth_app.py`** — JWT authentication with login and protected routes
- **`examples/middleware_demo.py`** — CORS, security headers, and rate limiting
- **`examples/query_app.py`** — Query parameter validation with Pydantic models

### Features Overview

**OpenAPI & Documentation**
```python
from pathiumapi.openapi_pydantic import add_openapi, add_docs

add_openapi(app, title="My API", version="1.0.0")
add_docs(app)  # Serves Swagger UI at /docs
```

**Request Validation**
```python
from pydantic import BaseModel

class QueryParams(BaseModel):
    page: int = 1
    limit: int = 10

@app.get("/items")
@app.validate_query(QueryParams)
async def list_items(req):
    params = req.validated_query
    return Response.json({"page": params.page, "limit": params.limit})
```

**JWT Authentication**
```python
from pathiumapi.auth import jwt_middleware_factory, create_token

# Protect routes requiring authentication
app.use(jwt_middleware_factory(secret="your-secret-key"))
```

**Middleware**
```python
from pathiumapi.middleware import cors_middleware, security_headers_middleware

app.use(cors_middleware(allow_origins=["*"]))
app.use(security_headers_middleware())
```

For comprehensive usage details, see `usage.md`.

Development
-----------
- Run tests: `python -m pytest -q`
- Static checks (optional): `flake8` and `mypy`

Contributing
------------
See `CONTRIBUTING.md` for branch naming, PR workflow, and guidelines. Open a
PR against `main` when ready and include tests for new functionality.

What's New
----------

### v0.2.0 (Latest)
- Improved onboarding and README quickstart
- OpenAPI + Pydantic improvements: component schemas, `@validate_query`, and
    more robust schema normalization for OpenAPI consumption
- New examples and tests demonstrating query-model docs and validation

### v0.1.11
- Auto-generation of OpenAPI query parameter schemas from Pydantic models
- `@validate_query` decorator with OpenAPI integration
- Enhanced query parameter validation and documentation

### Recent Releases
- **v0.1.10** — Common middleware (CORS, security headers, rate limiting)
- **v0.1.9** — JWT authentication middleware and helpers
- **v0.1.8** — Pydantic integration for request body validation
- **v0.1.7** — OpenAPI generation and Swagger UI documentation

See `CHANGELOG.md` for complete release history and `release-notes/` for detailed notes.

License
-------
MIT

