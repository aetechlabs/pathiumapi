"""Simple JWT authentication middleware and helpers for PathiumAPI.

This provides a `jwt_middleware_factory` that validates `Authorization: Bearer <token>`
and attaches decoded claims to `scope['user']` for handlers to inspect.

It depends on `PyJWT` (imported as `jwt`). If `PyJWT` is not installed, import
will raise; tests skip accordingly.
"""
from typing import Callable, Dict, Any, List

from ._core import Middleware, Scope, Receive, Send, HTTPError

import jwt


def jwt_middleware_factory(secret: str, algorithms: List[str] = None, exempt_paths: List[str] = None) -> Middleware:
    """Return middleware that validates Bearer JWTs.

    Args:
        secret: HMAC secret used to verify tokens (HS256).
        algorithms: list of accepted algorithms (defaults to ['HS256']).
        exempt_paths: list of URL paths that bypass auth (e.g., ['/login']).

    Usage:
        app.use(jwt_middleware_factory("mysecret"))
    """
    if algorithms is None:
        algorithms = ["HS256"]
    exempt_paths = exempt_paths or []

    def middleware(app: Callable[[Scope, Receive, Send], Any]):
        async def inner(scope: Scope, receive: Receive, send: Send) -> None:
            if scope.get("type") != "http":
                await app(scope, receive, send)
                return

            path = scope.get("path", "")
            if path in exempt_paths:
                await app(scope, receive, send)
                return

            headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
            auth = headers.get("authorization")
            if not auth or not auth.lower().startswith("bearer "):
                raise HTTPError(401, "Missing or invalid Authorization header")

            token = auth.split(None, 1)[1]
            try:
                claims = jwt.decode(token, secret, algorithms=algorithms)
            except jwt.ExpiredSignatureError:
                raise HTTPError(401, "Token expired")
            except jwt.InvalidTokenError:
                raise HTTPError(401, "Invalid token")

            # Attach claims to scope for downstream handlers
            scope["user"] = claims

            await app(scope, receive, send)

        return inner

    return middleware


def create_token(payload: Dict[str, Any], secret: str, algorithm: str = "HS256") -> str:
    """Create a JWT for the given payload.

    This is a tiny convenience wrapper used by example apps and tests.
    """
    return jwt.encode(payload, secret, algorithm=algorithm)
