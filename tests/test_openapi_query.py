import asyncio

try:
    from pydantic import BaseModel
except Exception:
    BaseModel = None

from pathiumapi._core import Pathium, add_openapi
from pathiumapi.validation import validate_query


def test_openapi_includes_query_model_params():
    if BaseModel is None:
        # skip if pydantic isn't installed
        assert True
        return

    class Q(BaseModel):
        q: str
        limit: int = 10

    app = Pathium()

    @app.get("/search")
    @validate_query(Q)
    async def search(req, qmodel: Q):
        """Search endpoint"""
        return {"q": qmodel.q, "limit": qmodel.limit}

    add_openapi(app)

    handler = None
    for r in app.router.routes:
        if r.path == "/openapi.json":
            handler = r.handler
            break
    assert handler is not None

    spec_resp = asyncio.run(handler(None))
    assert hasattr(spec_resp, "body_bytes")
    body = spec_resp.body_bytes.decode()
    # components should contain Q schema
    assert "Q" in body
    # path should include query parameter 'q' and 'limit'
    assert "/search" in body
    assert '"in": "query"' in body
    assert '"name": "q"' in body
    assert '"name": "limit"' in body
