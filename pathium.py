import re
__version__ = "0.1.10"
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
