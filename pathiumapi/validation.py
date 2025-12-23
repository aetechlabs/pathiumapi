"""Pydantic integration helpers.

Provides a minimal `validate_body` decorator to validate JSON request bodies
into a Pydantic model instance. Validation is lazy and works with both Pydantic
v1 and v2 by detecting the available API.
"""
from typing import Any, Callable
from functools import wraps

try:
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover - runtime import
    BaseModel = None  # type: ignore


def validate_data(model: type, data: Any):
    """Validate `data` against `model` (Pydantic BaseModel subclass).

    Returns a model instance. Raises RuntimeError if Pydantic is not present
    or model is not a subclass of BaseModel.
    """
    if BaseModel is None:
        raise RuntimeError("pydantic is not installed")
    if not issubclass(model, BaseModel):
        raise RuntimeError("model must be a Pydantic BaseModel subclass")

    # Pydantic v2 uses `model_validate`, v1 uses `parse_obj`
    if hasattr(model, "model_validate"):
        return model.model_validate(data)
    if hasattr(model, "parse_obj"):
        return model.parse_obj(data)
    # Fallback to constructor
    return model(**(data or {}))


def validate_body(model: type) -> Callable:
    """Decorator to validate request JSON body into `model`.

    The decorated handler will receive the validated model instance as the
    second positional argument after `req`.

    Example:

        @app.post('/items')
        @validate_body(ItemModel)
        async def create(req, item: ItemModel):
            return Response.json(item.model_dump())

    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(req, *args, **kwargs):
            data = await req.json()
            obj = validate_data(model, data or {})
            return await func(req, obj, *args, **kwargs)

        # expose the validated model on the wrapper so tooling (e.g., OpenAPI)
        # can detect the request body model for schema generation
        setattr(wrapper, "__validated_model__", model)
        return wrapper

    return decorator
