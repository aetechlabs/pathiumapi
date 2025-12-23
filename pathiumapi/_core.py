"""Core types and helpers for PathiumAPI.

This module exposes the primary API surface used by applications:
- `Request`, `Response` — request and response helpers
- `Route`, `Router` — routing primitives
- `Pathium` — the minimal ASGI application object
- `HTTPError`, `logging_middleware_factory`, `error_middleware`
- OpenAPI generation helpers: `add_openapi()`, `add_docs()`
"""

import re
__version__ = "0.1.12"
import json
from typing import (
    Callable,
    Dict,
    Any,
    List,
    Optional,
    Tuple,
    Coroutine,
)

Scope = Dict[str, Any]
# ASGI-style callables use Coroutines (async def) so annotate with Coroutine
Receive = Callable[[], Coroutine[Any, Any, Dict[str, Any]]]
Send = Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]
# A request handler returns a `Response` coroutine
Handler = Callable[..., Coroutine[Any, Any, 'Response']]
# Middleware wraps an ASGI app: (scope, receive, send) -> Coroutine
Middleware = Callable[
    [Callable[[Scope, Receive, Send], Coroutine[Any, Any, None]]],
    Callable[[Scope, Receive, Send], Coroutine[Any, Any, None]]
]


class Request:
    """Represents an incoming HTTP request.

    Attributes:
        scope: The ASGI scope dictionary for the request.
        _receive: The ASGI receive callable.
        _body: Cached request body bytes (filled on first read).

    Typical usage in handlers:

        async def handler(req: Request):
            data = await req.json()
            params = req.query_params
    """
    def __init__(self, scope: Scope, receive: Receive):
        assert scope['type'] == 'http'
        self.scope = scope
        self._receive = receive
        self._body: Optional[bytes] = None

    @property
    def method(self) -> str:
        return self.scope['method'].upper()

    @property
    def path(self) -> str:
        return self.scope['path']

    @property
    def headers(self) -> Dict[str, str]:
        hdrs: Dict[str, str] = {}
        for k, v in self.scope["headers"]:
            hdrs[k.decode().lower()] = v.decode()
        return hdrs

    @property
    def query_params(self) -> Dict[str, str]:
        raw = self.scope.get('query_string', b"") or b""
        qs = raw.decode()
        params: Dict[str, str] = {}
        if not qs:
            return params

        for pair in qs.split("&"):
            if not pair:
                continue
            if "=" in pair:
                k, v = pair.split("=", 1)
            else:
                k, v = pair, ""
            params[k] = v

        return params

    async def body(self) -> bytes:
        if self._body is None:
            chunks = []
            more = True
            while more:
                msg = await self._receive()
                if msg['type'] == "http.request":
                    chunks.append(msg.get("body", b""))
                    more = msg.get("more_body", False)
                else:
                    more = False
            self._body = b"".join(chunks)
        return self._body

    async def json(self) -> Any:
        b = await self.body()
        if not b:
            return None
        return json.loads(b.decode())


class Response:
    """Represents an HTTP response.

    Construct with text, bytes, or a Python object (dict/list) to return JSON.
    Use `Response.json(obj)` as a convenience helper to create a JSON response.
    """
    def __init__(
        self,
        content: bytes | str | dict | list | None = b"",
        status: int = 200,
        headers: Optional[List[Tuple[str, str]]] = None,
        media_type: Optional[str] = None,
    ):
        self.status = status
        self.headers = headers or []
        self.body_bytes: bytes

        if isinstance(content, (dict, list)):
            self.body_bytes = json.dumps(content).encode()
            self.headers.append((
                "content-type",
                "application/json; charset=utf-8",
            ))
        elif isinstance(content, str):
            self.body_bytes = content.encode()
            self.headers.append((
                "content-type",
                media_type or "text/plain; charset=utf-8",
            ))
        elif isinstance(content, (bytes, bytearray)):
            self.body_bytes = bytes(content)
            if media_type:
                self.headers.append(("content-type", media_type))
        elif content is None:
            self.body_bytes = b""
            if media_type:
                self.headers.append(("content-type", media_type))
        else:
            raise TypeError("Unsupported content type for Response")

    @classmethod
    def json(
        cls,
        data: Any,
        status: int = 200,
        headers: Optional[List[Tuple[str, str]]] = None,
    ):
        return cls(data, status=status, headers=headers or [])


class Route:
    """A single HTTP route mapping the (method, path) to a handler.

    The route compiles the path into a regular expression and supports simple
    path converters such as `{name:int}` which will coerce the captured value
    to `int`.
    """
    def __init__(self, method: str, path: str, handler: Handler):
        self.method = method.upper()
        self.path = path
        # param_names: list of parameter names in order
        # converters: mapping name -> callable to convert string to typed value
        self.param_names, self.regex, self.converters = self._compile(path)
        self.handler = handler

    def _compile(
        self, path: str
    ) -> Tuple[List[str], re.Pattern, Dict[str, Callable[[str], Any]]]:
        param_names: List[str] = []
        converters: Dict[str, Callable[[str], Any]] = {}
        regex_str = "^"
        i = 0
        while i < len(path):
            if path[i] == "{":
                j = path.find("}", i)
                if j == -1:
                    raise ValueError("Unmatched '{' in route path")
                inner = path[i+1:j]
                # support converters: {name:type}
                if ":" in inner:
                    name, typ = inner.split(":", 1)
                else:
                    name, typ = inner, "str"

                param_names.append(name)
                if typ == "int":
                    regex_str += rf"(?P<{name}>\d+)"
                    converters[name] = int
                else:
                    # default and unknown types fall back to string
                    regex_str += rf"(?P<{name}>[^/]+)"
                    converters[name] = str
                i = j + 1
            else:
                c = re.escape(path[i])
                regex_str += c
                i += 1

        regex_str += "$"
        return param_names, re.compile(regex_str), converters

    def matches(self, method: str, path: str) -> Optional[Dict[str, Any]]:
        if method.upper() != self.method:
            return None
        m = self.regex.match(path)
        if not m:
            return None
        raw = m.groupdict()
        params: Dict[str, Any] = {}
        for k, v in raw.items():
            conv = getattr(self, "converters", {}).get(k)
            if conv is not None:
                try:
                    params[k] = conv(v)
                except Exception:
                    # conversion failed -> no match
                    return None
            else:
                params[k] = v
        return params


class Router:
    """Lightweight router holding a list of `Route` objects.

    Use `add()` to register routes and `find()` to lookup a matching route
    and extracted path parameters for an incoming request.
    """
    def __init__(self):
        self.routes: List[Route] = []

    def add(self, method: str, path: str, handler: Handler):
        self.routes.append(Route(method, path, handler))

    def find(
        self,
        method: str,
        path: str,
    ) -> Tuple[Optional[Route], Dict[str, str]]:
        for r in self.routes:
            params = r.matches(method, path)
            if params is not None:
                return r, params
        return None, {}


class Pathium:
    """Minimal ASGI application with routing and middleware support.

    Example:

        app = Pathium()

        @app.get("/items/{id:int}")
        async def get_item(req, id: int):
            return Response.json({"id": id})
    """
    def __init__(self):
        self.router = Router()
        self._middleware: List[Middleware] = []

    def route(self, method: str, path: str):
        def decorator(func: Handler):
            self.router.add(method, path, func)
            return func
        return decorator

    def get(self, path: str): return self.route("GET", path)
    def post(self, path: str): return self.route("POST", path)
    def put(self, path: str): return self.route("PUT", path)
    def patch(self, path: str): return self.route("PATCH", path)
    def delete(self, path: str): return self.route("DELETE", path)

    def use(self, mw: Middleware):
        self._middleware.append(mw)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            start_msg = {
                "type": "http.response.start",
                "status": 404,
                "headers": [],
            }
            await send(start_msg)
            not_found = {"type": "http.response.body", "body": b"Not Found"}
            await send(not_found)
            return

        async def endpoint(scope: Scope, receive: Receive, send: Send) -> None:
            req = Request(scope, receive)
            route, params = self.router.find(req.method, req.path)
            if route is None:
                resp = Response("Not Found", status=404)
            else:
                try:
                    resp = await route.handler(req, **params)
                    if not isinstance(resp, Response):
                        resp = Response(resp)
                except HTTPError as he:
                    resp = Response.json(
                        {"detail": he.detail},
                        status=he.status,
                    )
                except Exception:
                    resp = Response.json(
                        {"detail": "Internal Server Error"},
                        status=500,
                    )

            headers: List[Tuple[bytes, bytes]] = []
            for k, v in resp.headers:
                headers.append((k.encode(), v.encode()))

            start_msg = {
                "type": "http.response.start",
                "status": resp.status,
                "headers": headers,
            }
            await send(start_msg)
            body_msg = {
                "type": "http.response.body",
                "body": resp.body_bytes,
            }
            await send(body_msg)

        app: Callable[
            [Scope, Receive, Send], Coroutine[Any, Any, None]
        ] = endpoint
        for mw in reversed(self._middleware):
            app = mw(app)
        await app(scope, receive, send)


class HTTPError(Exception):
    """Exception used to return HTTP error responses from handlers.

    Raise `HTTPError(status, detail)` inside a handler. When used with the
    provided `error_middleware`, it will be converted into a JSON response
    with the provided status and detail message.
    """
    def __init__(self, status: int, detail: str = ""):
        self.status = status
        self.detail = detail or f"HTTP {status}"
        super().__init__(self.detail)


# Middleware helpers
def logging_middleware_factory(
    logger: Optional[Callable[[str], None]] = None,
 ) -> Middleware:
    """Return a middleware that logs request method and path.

    Example:
        app.use(logging_middleware_factory(print))
    """
    def middleware(
        app: Callable[[Scope, Receive, Send], Coroutine[Any, Any, None]]
    ):
        async def inner(scope: Scope, receive: Receive, send: Send) -> None:
            if scope.get("type") == "http":
                method = scope.get("method", "").upper()
                path = scope.get("path", "")
                msg = f"{method} {path}"
                if logger:
                    logger(msg)
            await app(scope, receive, send)

        return inner

    return middleware


def error_middleware(
    app: Callable[[Scope, Receive, Send], Coroutine[Any, Any, None]]
):
    """Middleware that converts uncaught exceptions to JSON 500 responses."""

    async def inner(scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await app(scope, receive, send)
        except HTTPError as he:
            headers = [
                (b"content-type", b"application/json; charset=utf-8"),
            ]
            start_msg = {
                "type": "http.response.start",
                "status": he.status,
                "headers": headers,
            }
            await send(start_msg)
            body = json.dumps({
                "detail": he.detail,
            }).encode()
            await send({
                "type": "http.response.body",
                "body": body,
            })
        except Exception:
            headers = [
                (b"content-type", b"application/json; charset=utf-8"),
            ]
            start_msg = {
                "type": "http.response.start",
                "status": 500,
                "headers": headers,
            }
            await send(start_msg)
            body = json.dumps({
                "detail": "Internal Server Error",
            }).encode()
            await send({
                "type": "http.response.body",
                "body": body,
            })

    return inner


# --- OpenAPI / docs helpers -------------------------------------------------
def _converter_to_openapi_type(conv: Callable[[str], Any]) -> Dict[str, str]:
    if conv is int:
        return {"type": "integer", "format": "int32"}
    return {"type": "string"}


def _route_to_openapi_entry(route: Route) -> Dict[str, Any]:
    """Create a minimal OpenAPI path entry for a `Route`.

    This intentionally produces a compact schema useful for interactive
    documentation and quick discovery. It does not perform full request body
    schema inference (use Pydantic integration in a follow-up feature).
    """
    parameters = []
    for name, conv in getattr(route, "converters", {}).items():
        parameters.append({
            "name": name,
            "in": "path",
            "required": True,
            "schema": _converter_to_openapi_type(conv),
        })

    summary = (route.handler.__doc__ or "").strip()

    op: Dict[str, Any] = {
        "summary": summary,
        "parameters": parameters,
        "responses": {
            "200": {"description": "Successful Response"},
            "default": {"description": "Unexpected error"},
        },
    }

    # Attach requestBody / response schema $ref if handler declares Pydantic models
    try:
        from .openapi_pydantic import is_pydantic_model, model_to_schema

        handler = route.handler
        # request body via validate_body exposes __validated_model__ on wrapper
        validated = getattr(handler, "__validated_model__", None)
        if validated and is_pydantic_model(validated):
            op["requestBody"] = {
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{validated.__name__}"}
                    }
                },
                "required": True,
            }

        # query params via validate_query exposes __validated_query_model__
        qmodel = getattr(handler, "__validated_query_model__", None)
        if qmodel and is_pydantic_model(qmodel):
            schema = model_to_schema(qmodel)
            props = schema.get("properties", {})
            required = set(schema.get("required", []))
            for pname, pschema in props.items():
                param = {
                    "name": pname,
                    "in": "query",
                    "required": pname in required,
                    "schema": pschema,
                }
                op["parameters"].append(param)

        # response model via decorator or return annotation
        resp = getattr(handler, "__response_model__", None)
        if resp is None:
            ann = getattr(handler, "__annotations__", {})
            resp = ann.get("return")
        if resp and is_pydantic_model(resp):
            op["responses"]["200"] = {
                "description": "Successful Response",
                "content": {
                    "application/json": {"schema": {"$ref": f"#/components/schemas/{resp.__name__}"}}
                },
            }
    except Exception:
        # optional Pydantic integration; ignore if missing
        pass

    return {route.method.lower(): op}


def _openapi_paths(router: Router) -> Dict[str, Any]:
    paths: Dict[str, Any] = {}
    for r in router.routes:
        # Pathium already uses {name} style compatible with OpenAPI
        p = r.path
        entry = _route_to_openapi_entry(r)
        if p not in paths:
            paths[p] = {}
        paths[p].update(entry)
    return paths


def _swagger_ui_html(openapi_url: str) -> str:
    # Use the unpkg CDN for a simple, zero-dependency Swagger UI
    return f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
    <script>
      const ui = SwaggerUIBundle({
        url: '%s',
        dom_id: '#swagger-ui',
      });
    </script>
  </body>
  </html>
""" % (openapi_url)


def add_openapi(app: Pathium, path: str = "/openapi.json", title: str = "Pathium API", version: str = __version__) -> None:
    """Register a route that serves a minimal OpenAPI JSON spec for `app`.

    Usage:
        add_openapi(app)
    """
    async def _openapi_handler(req: Request):
        spec = {
            "openapi": "3.0.0",
            "info": {"title": title, "version": version},
            "paths": _openapi_paths(app.router),
        }

        # Try to include Pydantic-generated component schemas when available
        try:
            from .openapi_pydantic import model_to_schema, is_pydantic_model

            components: Dict[str, Any] = {"schemas": {}}
            # Scan route handlers for annotated Pydantic models in parameters
            for r in app.router.routes:
                handler = r.handler
                # Check annotated types on the handler func
                ann = getattr(handler, "__annotations__", {})
                for name, typ in ann.items():
                    if is_pydantic_model(typ):
                        components["schemas"][typ.__name__] = model_to_schema(typ)

                # Check for validated request body exposed by `validate_body`
                validated = getattr(handler, "__validated_model__", None)
                if validated and is_pydantic_model(validated):
                    components["schemas"][validated.__name__] = model_to_schema(validated)
                # Check for validated query model exposed by `validate_query`
                qvalidated = getattr(handler, "__validated_query_model__", None)
                if qvalidated and is_pydantic_model(qvalidated):
                    components["schemas"][qvalidated.__name__] = model_to_schema(qvalidated)

            if components["schemas"]:
                spec["components"] = components
        except Exception:
            # Pydantic may be missing; ignore and return basic spec
            pass

        return Response.json(spec)

    app.get(path)(_openapi_handler)


def add_docs(app: Pathium, path: str = "/docs", openapi_url: str = "/openapi.json") -> None:
    """Register a simple Swagger UI page at `path` that points to `openapi_url`.

    This is intentionally minimal: it uses the Swagger UI bundle from a CDN so
    projects do not need to vendor static files.
    """
    async def _docs_handler(req: Request):
        html = _swagger_ui_html(openapi_url)
        return Response(html, headers=[("content-type", "text/html; charset=utf-8")])

    app.get(path)(_docs_handler)

