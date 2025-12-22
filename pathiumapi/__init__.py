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
]
