import asyncio
from typing import List, Dict, Any

import pytest

from pathiumapi import middleware
from pathiumapi._core import HTTPError


async def _call_app(app, scope, events: List[Dict[str, Any]]):
    sent: List[Dict[str, Any]] = []

    async def receive():
        if events:
            return events.pop(0)
        await asyncio.sleep(0)
        return {"type": "http.disconnect"}

    async def send(msg):
        sent.append(msg)

    await app(scope, receive, send)
    return sent


def _make_scope(origin: str = None, client: tuple = ("1.2.3.4", 12345)):
    headers = []
    if origin:
        headers.append((b"origin", origin.encode()))
    return {"type": "http", "method": "GET", "path": "/", "headers": headers, "client": client}


def _simple_app(status=200):
    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": status, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    return app


def test_cors_adds_headers():
    async def _test():
        app = _simple_app()
        wrapped = middleware.cors_middleware_factory(allow_origins=None)(app)
        scope = _make_scope(origin="https://example.com")
        sent = await _call_app(wrapped, scope, [])

        start = next(m for m in sent if m["type"] == "http.response.start")
        hdrs = dict((k.decode(), v.decode()) for k, v in start.get("headers", []))
        assert "Access-Control-Allow-Origin" in hdrs
        assert "Access-Control-Allow-Methods" in hdrs

    asyncio.run(_test())


def test_security_headers_added():
    async def _test():
        app = _simple_app()
        wrapped = middleware.security_headers_middleware(hsts_max_age=100, include_subdomains=False)(app)
        scope = _make_scope()
        sent = await _call_app(wrapped, scope, [])

        start = next(m for m in sent if m["type"] == "http.response.start")
        hdrs = dict((k.decode(), v.decode()) for k, v in start.get("headers", []))
        assert hdrs.get("Strict-Transport-Security") == "max-age=100"
        assert hdrs.get("X-Frame-Options") == "DENY"

    asyncio.run(_test())


def test_rate_limiter_blocks_after_limit():
    async def _test():
        app = _simple_app()
        # allow 2 requests per 1 second window
        wrapped = middleware.rate_limit_middleware_factory(requests=2, window_seconds=1)(app)
        scope = _make_scope(client=("9.9.9.9", 1111))

        # first two should pass
        await _call_app(wrapped, scope.copy(), [])
        await _call_app(wrapped, scope.copy(), [])

        # third should raise HTTPError 429
        with pytest.raises(HTTPError) as exc:
            await _call_app(wrapped, scope.copy(), [])

        assert exc.value.status == 429

    asyncio.run(_test())
