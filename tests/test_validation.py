import pytest

try:
    from pydantic import BaseModel  # type: ignore
except Exception:
    BaseModel = None  # type: ignore

from pathiumapi.validation import validate_data


def test_validate_data_skipped_if_no_pydantic():
    if BaseModel is None:
        pytest.skip("pydantic not installed")


def test_validate_data_basic():
    if BaseModel is None:
        pytest.skip("pydantic not installed")

    class Item(BaseModel):
        name: str
        qty: int

    inst = validate_data(Item, {"name": "apple", "qty": 3})
    assert inst.name == "apple"
    assert inst.qty == 3
