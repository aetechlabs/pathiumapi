# Usage

## Installation

Install the latest release from PyPI:

```bash
pip install PathiumAPI
```

## Quickstart

Create a file `app.py` with a minimal app:

```python
from pathiumapi import Pathium, Response

app = Pathium()

@app.get("/")
async def index(req):
    return Response("Hello, PathiumAPI!")

@app.get("/users/{id}")
async def get_user(req, id: str):
    # Path params are passed as function args
    return Response.json({"id": id})

@app.get("/search")
async def search(req):
    # Query params available via Request.query_params
    q = req.query_params.get("q", "")
    return Response.json({"q": q})
```

Run with an ASGI server (e.g. `uvicorn`):

```bash
pip install uvicorn
uvicorn app:app --reload
```

## Request body and JSON

Use `await req.json()` to read a JSON body inside an async handler:

```python
@app.post("/items")
async def create_item(req):
    data = await req.json()
    return Response.json({"received": data}, status=201)
```

## Responses

PathiumAPI provides a simple `Response` class. You can return:

- `Response("text")` — plain text response
- `Response.json(obj)` — JSON response helper
- `Response(content, status=201, headers=[("x", "y")])` — full control

Examples:

```python
return Response("OK")
return Response.json({"key": "value"}, status=200)
```

## Routing and converters

Routes support path parameter converters using `{name:type}`. Supported types:

- `int` — integer converter
- `str` — default string converter

Example:

```python
@app.get("/items/{item_id:int}")
async def item(req, item_id: int):
    return Response.json({"item_id": item_id})
```

## Middleware

Add middleware via `app.use(middleware_factory())`. A helper `logging_middleware` is provided:

```python
app.use(logging_middleware_factory(print))
```

Middleware wraps the ASGI app and can inspect/modify the scope, request or response.

## Error handling

Raise `HTTPError(status, detail)` from handlers to return structured JSON errors. The built-in `error_middleware` converts uncaught exceptions into JSON 500 responses.

## CLI

The package provides a small CLI entrypoint `pathiumapi` with commands:

- `pathiumapi new <name>` — scaffold a new app
- `pathiumapi run` — try to run an `app.py` with `uvicorn` if installed

Example:

```bash
pathiumapi new myapp
cd myapp
pathiumapi run
```

## Advanced

- The library is a minimal ASGI framework. You can run it with any ASGI server (uvicorn, hypercorn).
- For larger projects you may want to integrate with libraries for request validation, OpenAPI generation, or dependency injection.

## Contributing & Next Steps

See `CONTRIBUTING.md` for branching, feature workflows, and how to propose changes.