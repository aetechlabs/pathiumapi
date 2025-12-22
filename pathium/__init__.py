import warnings

warnings.warn(
    "The 'lilac' package is deprecated and has been renamed to 'pathiumapi'. "
    "Please import from 'pathiumapi' instead — 'lilac' will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from pathiumapi import (
    __version__,
    Request,
    Response,
    Route,
    Router,
    Lilac,
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
    "Lilac",
    "HTTPError",
    "logging_middleware_factory",
    "error_middleware",
]
