"""Example app showing `validate_query` usage and docs generation."""
from pydantic import BaseModel
from pathiumapi._core import Pathium, add_openapi, add_docs
from pathiumapi.validation import validate_query, response_model


class SearchQuery(BaseModel):
    q: str
    limit: int = 10


app = Pathium()


@app.get("/search")
@validate_query(SearchQuery)
@response_model(dict)
async def search(req, q: SearchQuery):
    """Search endpoint returning query echo."""
    return {"q": q.q, "limit": q.limit}


add_openapi(app)
add_docs(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("examples.query_app:app", host="127.0.0.1", port=8001, reload=True)
