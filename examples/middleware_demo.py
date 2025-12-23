"""Simple example demonstrating middleware composition with Pathium.

Run with an ASGI server that can load plain callables, or adapt into
the project's example apps.
"""
from pathiumapi import middleware


def build_app():
    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"hello middleware"})

    app = middleware.security_headers_middleware()(app)
    app = middleware.cors_middleware_factory(allow_origins=["*"])(app)
    app = middleware.rate_limit_middleware_factory(requests=5, window_seconds=60)(app)
    return app


app = build_app()

if __name__ == "__main__":
    print("Built middleware-wrapped app. Serve with an ASGI server.")
