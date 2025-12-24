"""Test that the docs page includes the greeting."""
import asyncio
from pathiumapi._core import Pathium, add_openapi, add_docs, Request


def test_docs_includes_greeting():
    """Test that 'Good day' greeting is present in the Swagger UI docs."""
    app = Pathium()
    
    @app.get("/")
    async def index(req):
        return "Hello"
    
    add_openapi(app)
    add_docs(app)
    
    # Find the docs handler
    docs_handler = None
    for route in app.router.routes:
        if route.path == "/docs":
            docs_handler = route.handler
            break
    
    assert docs_handler is not None, "Docs route should be registered"
    
    # Create a mock request
    scope = {
        'type': 'http',
        'method': 'GET',
        'path': '/docs',
        'query_string': b'',
        'headers': []
    }
    
    async def receive():
        return {'type': 'http.request', 'body': b'', 'more_body': False}
    
    req = Request(scope, receive)
    
    # Call the handler
    response = asyncio.run(docs_handler(req))
    
    # Verify the greeting is in the HTML
    assert b"Good day" in response.body_bytes, "Greeting should be present in docs HTML"
    assert b'class="greeting"' in response.body_bytes, "Greeting div should be present"
