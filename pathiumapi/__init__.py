"""PathiumAPI package public interface.

Import symbols from `pathiumapi` to get the minimal API surface used by
applications. These exported names have docstrings that appear as hovers in
most IDEs and editors.
"""

from ._core import (
    __version__,
    Request,
    Response,
    Route,
    Router,
    Pathium,
    HTTPError,
    logging_middleware_factory,
    error_middleware,
)

from .validation import validate_body

# Import optional auth helpers lazily — if PyJWT is not installed we expose
# placeholder functions that raise clear runtime errors when invoked. This
# prevents importing `pathiumapi` (for CLI/tools) from failing in virtualenvs
# that don't have PyJWT installed.
try:
    from .auth import jwt_middleware_factory, create_token
except Exception:  # pragma: no cover - runtime import
    def jwt_middleware_factory(*args, **kwargs):
        raise RuntimeError("PyJWT is not installed. Install with `pip install PyJWT` to use jwt_middleware_factory")

    def create_token(*args, **kwargs):
        raise RuntimeError("PyJWT is not installed. Install with `pip install PyJWT` to use create_token")

__all__ = [
    "__version__",
    "Request",
    "Response",
    "Route",
    "Router",
    "Pathium",
    "HTTPError",
    "logging_middleware_factory",
    "error_middleware",
    "validate_body",
    "jwt_middleware_factory",
    "create_token",
]
