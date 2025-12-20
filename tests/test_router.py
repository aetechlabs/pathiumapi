import re
from pathiumapi import Router, Route, Response


def test_route_simple_match():
    r = Router()

    async def handler(req):
        return Response("ok")

    r.add("GET", "/hello", handler)
    route, params = r.find("GET", "/hello")
    assert route is not None
    assert params == {}


def test_route_params_and_converter():
    r = Router()

    async def handler(req, id):
        return Response.json({"id": id})

    r.add("GET", "/items/{id:int}", handler)
    route, params = r.find("GET", "/items/42")
    assert route is not None
    assert params["id"] == 42


def test_route_no_match_on_converter():
    r = Router()

    async def handler(req, id):
        return Response.json({"id": id})

    r.add("GET", "/items/{id:int}", handler)
    route, params = r.find("GET", "/items/abc")
    assert route is None
