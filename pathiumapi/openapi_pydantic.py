"""Helpers to auto-generate OpenAPI components from Pydantic models.

This module detects Pydantic model types referenced in handler annotations
or via the `validate_body` helper and returns JSON Schema components.
"""
from typing import Any, Dict, Type

try:
    from pydantic import BaseModel
except Exception:  # pragma: no cover - optional dependency
    BaseModel = None  # type: ignore


def is_pydantic_model(obj: Any) -> bool:
    return BaseModel is not None and isinstance(obj, type) and issubclass(obj, BaseModel)


def model_to_schema(model: Type[Any]) -> Dict[str, Any]:
    """Return a JSON Schema dict for a Pydantic model.

    Uses `model.model_json_schema()` on Pydantic v2 or `.schema()` on v1.
    """
    if BaseModel is None:
        raise RuntimeError("Pydantic is not installed")

    # Pydantic v2
    if hasattr(model, "model_json_schema"):
        schema = model.model_json_schema()
        # ensure top-level $schema not included in components
        schema.pop("$schema", None)
        # normalize keys
        schema.setdefault("properties", {})
        schema.setdefault("required", [])
        return schema

    # Pydantic v1
    if hasattr(model, "schema"):
        schema = model.schema()
        schema.setdefault("properties", {})
        schema.setdefault("required", [])
        return schema

    raise RuntimeError("Unsupported Pydantic model type")
