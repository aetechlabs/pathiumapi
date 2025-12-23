"""Common middleware: CORS, security headers, and simple rate limiting.

These are lightweight, zero-dependency middleware factories suitable for
embedding in `Pathium` apps. They are intentionally simple and designed
for local development or as a reference implementation.
"""
from typing import Callable, List, Optional, Dict, Any
import time

from ._core import Middleware, Scope, Receive, Send, HTTPError


def cors_middleware_factory(
    allow_origins: Optional[List[str]] = None,
    allow_methods: Optional[List[str]] = None,
    allow_headers: Optional[List[str]] = None,
    allow_credentials: bool = False,
) -> Middleware:
    """Return CORS middleware.

    - `allow_origins`: list of allowed origins or None to allow any origin.
    - `allow_methods`: list of allowed methods (default: GET,POST,PUT,PATCH,DELETE,OPTIONS)
    - `allow_headers`: list of allowed headers echoed back when present.
    - `allow_credentials`: whether to set Access-Control-Allow-Credentials.
    """
    if allow_methods is None:
        allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    def middleware(app: Callable[[Scope, Receive, Send], Any]):
        async def inner(scope: Scope, receive: Receive, send: Send) -> None:
            if scope.get("type") != "http":
                await app(scope, receive, send)
                return

            headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
            origin = headers.get("origin")

            def send_wrapper(msg: Dict[str, Any]):
                if msg.get("type") == "http.response.start":
                    hdrs = dict((k.decode(), v.decode()) for k, v in msg.get("headers", [])) if msg.get("headers") else {}
                    # Decide allowed origin
                    if origin:
                        if allow_origins is None or origin in allow_origins or "*" in allow_origins:
                            hdrs["Access-Control-Allow-Origin"] = origin if allow_origins and origin != "*" else "*"
                    elif allow_origins is None:
                        hdrs["Access-Control-Allow-Origin"] = "*"

                    hdrs["Access-Control-Allow-Methods"] = ", ".join(allow_methods)
                    if allow_headers:
                        hdrs["Access-Control-Allow-Headers"] = ", ".join(allow_headers)
                    if allow_credentials:
                        hdrs["Access-Control-Allow-Credentials"] = "true"

                    msg["headers"] = [(k.encode(), v.encode()) for k, v in hdrs.items()]

                return send(msg)

            await app(scope, receive, send_wrapper)

        return inner

    return middleware


def security_headers_middleware(
    hsts_max_age: Optional[int] = 63072000,
    include_subdomains: bool = True,
    frame_options: str = "DENY",
) -> Middleware:
    """Add common security headers to responses.

    - `hsts_max_age`: if None, HSTS header is not added.
    """
    def middleware(app: Callable[[Scope, Receive, Send], Any]):
        async def inner(scope: Scope, receive: Receive, send: Send) -> None:
            if scope.get("type") != "http":
                await app(scope, receive, send)
                return

            def send_wrapper(msg: Dict[str, Any]):
                if msg.get("type") == "http.response.start":
                    hdrs = dict((k.decode(), v.decode()) for k, v in msg.get("headers", [])) if msg.get("headers") else {}
                    if hsts_max_age is not None:
                        hsts = f"max-age={hsts_max_age}"
                        if include_subdomains:
                            hsts += "; includeSubDomains"
                        hdrs["Strict-Transport-Security"] = hsts
                    hdrs["X-Frame-Options"] = frame_options
                    hdrs["X-Content-Type-Options"] = "nosniff"
                    hdrs["Referrer-Policy"] = "no-referrer"
                    msg["headers"] = [(k.encode(), v.encode()) for k, v in hdrs.items()]
                return send(msg)

            await app(scope, receive, send_wrapper)

        return inner

    return middleware


def rate_limit_middleware_factory(requests: int = 10, window_seconds: int = 60):
    """Return a simple in-memory fixed-window rate limiter middleware.

    NOTE: This implementation is memory-backed and per-process. For production
    use a distributed store (Redis) and token-bucket algorithm.
    """
    # store: {key: (window_start_ts, count)}
    store: Dict[str, Any] = {}

    def middleware(app: Callable[[Scope, Receive, Send], Any]):
        async def inner(scope: Scope, receive: Receive, send: Send) -> None:
            if scope.get("type") != "http":
                await app(scope, receive, send)
                return

            # Identify client by remote addr if available, otherwise 'anon'
            client = scope.get("client")
            key = client[0] if client and isinstance(client, (list, tuple)) else "anon"
            now = int(time.time())
            window_start, count = store.get(key, (now, 0))
            if now - window_start >= window_seconds:
                window_start, count = now, 0

            count += 1
            store[key] = (window_start, count)

            if count > requests:
                raise HTTPError(429, "Too Many Requests")

            await app(scope, receive, send)

        return inner

    return middleware
