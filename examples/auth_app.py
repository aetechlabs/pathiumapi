"""Example app demonstrating JWT auth middleware.

Run with: `uvicorn examples.auth_app:app` (or embed in tests/examples).
"""
from pathiumapi import Pathium, Response, jwt_middleware_factory, create_token

SECRET = "dev-secret"

app = Pathium()

@app.post("/login")
async def login(req):
    data = await req.json() or {}
    username = data.get("username")
    password = data.get("password")
    # Very small example: accept any non-empty username/password
    if not username or not password:
        return Response.json({"detail": "invalid credentials"}, status=400)

    token = create_token({"sub": username}, SECRET)
    return Response.json({"access_token": token})

app.use(jwt_middleware_factory(SECRET, exempt_paths=["/login"]))

@app.get("/protected")
async def protected(req):
    user = req.scope.get("user")
    return Response.json({"user": user})
