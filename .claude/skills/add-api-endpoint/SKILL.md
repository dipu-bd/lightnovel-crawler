---
name: add-api-endpoint
description: Add or modify a FastAPI endpoint in lncrawl — router aggregation, ensure_user/ensure_admin security, DTO vs DAO models, pagination, ServerErrors. Use when touching lncrawl/server/api/, security.py, or server/models/.
---

# Server API (`lncrawl/server/api/`)

Each domain is one module with a module-level `router = APIRouter()` and relative paths.
`server/api/__init__.py` aggregates them: one `include_router(alias, prefix, tags,
dependencies=[Security(...)])` block per module; the composite router mounts at `/api` in
`server/app.py`.

## Recipe: new endpoint / router

1. Add the handler to the matching `server/api/<domain>.py` (or create a new module +
   `include_router` block in `__init__.py`).
2. Auth: router-level `dependencies=[Security(ensure_user)]` covers most modules; use
   `Security(ensure_admin)` for admin routers. To get the caller inside a handler, add a
   `user: User = Security(ensure_user)` parameter; to tighten one route inside a looser
   router, use per-route `dependencies=[Security(ensure_admin)]`.
3. Delegate all logic to a service singleton (`ctx.<service>`) — handlers stay thin. Return
   DAO SQLModel objects or `server/models/` Pydantic DTOs directly; FastAPI serializes them.
4. Request bodies are Pydantic models in `server/models/` (re-exported from its
   `__init__.py`) via `Body(...)`; query/path params via `Query(...)`/`Path(...)`.
5. Quota/permission checks go through `ctx.tier.<check>(user)` — never inline tier logic.

## Security model (`server/security.py`)

- `ensure_user` accepts **either** HTTP Basic (email+password) **or** a Bearer JWT; rejects
  inactive users. JWT scopes = provided scopes ∪ {user.role, user.tier}
  (`services/users.py`); `verify_token` requires all `Security(..., scopes=[...])` scopes.
- `ensure_admin` = `ensure_user` with the ADMIN scope plus an explicit role check (the role
  check matters because the Basic-auth path bypasses scope verification).
- `ensure_local` exists but is currently used by no endpoint — don't copy it as a live
  pattern without checking.
- WebSocket routers must **not** inherit HTTP security dependencies — that's why the LSP
  router is included first, without a parent dependency (see the comment in
  `api/__init__.py`). The only WebSocket is `/api/lsp`.
- Protected static files (`/static/novels|images|sources/...`) authenticate via a `?token=`
  **query param** (`StaticFilesGuard` middleware), not headers — that's how the web UI loads
  images and downloads artifacts.

## Conventions

- **Paths**: list endpoints extend the router prefix with a bare `"s"` —
  `@router.get("s")` under prefix `/novel` serves `GET /api/novels` while
  `@router.get("/{novel_id}")` serves `GET /api/novel/{id}`. Follow it for new list routes.
- **Pagination**: `Paginated[T]` (`server/models/pagination.py`) = `{total, offset, limit,
  items}`; conventional params `offset: int = Query(default=0)`, `limit: Query(default=20,
  le=100)`. When adding filters, apply the same conditions to the `total` count query —
  some existing services count unfiltered totals; don't copy that.
- **Errors**: raise the pre-instantiated singletons from `ServerErrors`
  (`lncrawl/exceptions.py`), optionally `.with_extra(detail)`. Add new error kinds to that
  catalog; do **not** hand-roll `HTTPException`. Exception handlers registered in `app.py`
  produce `{"error": ..., "detail": ...}` bodies. WebSocket errors use the separate
  `WebSocketError` classes.
- Swagger UI at `/docs`, ReDoc at `/redoc`, raw spec at `/openapi.json`; `/health` is the
  unauthenticated liveness probe.
- `server/web/` is committed build output synced from the lncrawl-web repo's `artifacts`
  branch by the "Sync Web" workflow — **never hand-edit it**.
