import pytest

jwt = pytest.importorskip("jwt")

from pathiumapi import jwt_middleware_factory, create_token


def test_jwt_middleware_factory_exists():
    mw = jwt_middleware_factory("secret")
    assert callable(mw)


def test_create_token_and_decode():
    tok = create_token({"sub": "alice"}, "secret")
    decoded = jwt.decode(tok, "secret", algorithms=["HS256"])
    assert decoded["sub"] == "alice"
