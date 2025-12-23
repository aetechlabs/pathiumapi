try:
    from pydantic import BaseModel
except Exception:
    BaseModel = None  # type: ignore

from pathiumapi.openapi_pydantic import is_pydantic_model


def test_is_pydantic_model():
    if BaseModel is None:
        # If pydantic not installed, ensure function doesn't crash
        assert is_pydantic_model(object()) is False
        return

    class M(BaseModel):
        x: int

    assert is_pydantic_model(M)
