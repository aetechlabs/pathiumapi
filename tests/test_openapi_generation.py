import asyncio

try:
    from pydantic import BaseModel
except Exception:
    BaseModel = None

from pathiumapi._core import Pathium, add_openapi
from pathiumapi.validation import validate_body, response_model


def test_openapi_includes_request_and_response_models():
    if BaseModel is None:
        # skip if pydantic isn't installed
        assert True
        return

    class Item(BaseModel):
        id: int
        name: str

    app = Pathium()

    @app.post("/items")
    @validate_body(Item)
    @response_model(Item)
    async def create(req, item: Item):
        return item

    add_openapi(app)

    # call the registered openapi handler directly
    # find route handler for /openapi.json
    handler = None
    for r in app.router.routes:
        if r.path == "/openapi.json":
            handler = r.handler
            break
    assert handler is not None

    spec = asyncio.run(handler(None))
    # handler returns a Response object; its content is in spec.body_bytes when serialized
    # but add_openapi returns Response.json(spec_dict), so spec is Response instance
    assert hasattr(spec, "body_bytes")
    body = spec.body_bytes
    assert b"/items" in body
    assert b"components" in body
