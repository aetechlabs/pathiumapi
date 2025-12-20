from pathiumapi import Lilac, Response, logging_middleware_factory, error_middleware

app = Lilac()

# register middleware
app.use(logging_middleware_factory(print))
app.use(error_middleware)

@app.get("/")
async def index(req):
    return "Hello from PathiumAPI"

@app.get("/items/{id:int}")
async def get_item(req, id):
    return Response.json({"item_id": id})

# expose `app` for ASGI servers like uvicorn
