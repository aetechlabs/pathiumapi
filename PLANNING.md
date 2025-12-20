# Lilac Quick Wins

This file lists small, high-impact improvements to implement on the
`planning/quick-wins` branch.

Prioritized items:

- Route parameter converters (`{id:int}`, `{slug}`)
- Path prefix routers / mounting apps
- Middleware helpers (logging, errors)
- Async background task helper API
- Improve `Request` parsing utilities (`get_header`, `get_query`) 
- Response helpers and content negotiation
- Add unit tests for `Router`, `Request`, `Response`

Next steps (this branch):
1. Implement route parameter converters (int, str)
2. Add `PLANNING.md` (this file)
3. Implement middleware helpers

