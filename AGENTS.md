# Base44 Dev Environment

## Stack
- **Backend**: FastAPI (Python 3.12) in `backend/`, served by uvicorn on port 8000 with `--reload`.
- **Frontend**: Vue 3 + Vite 8 in `frontend/`, dev server on port 5173 (mapped to host 3000).
- Single-origin wiring: the Vite dev server proxies `/api`, `/api/media`, `/api/static` to the backend service (`BACKEND_URL` env var, defaults to `http://localhost:8000` for local dev).

## Running
```bash
docker compose -f docker-compose.base44.yml up -d --build
```
- Frontend (web entry point): http://localhost:3000
- Backend API: internal only (proxied through Vite); interactive docs at `/docs` via the proxy.

## Data
- Defaults to **SQLite** at `backend/data/recipes.db` (bind-mounted, persists on host). No `DATABASE_URL` needed to boot.
- Image uploads default to database-backed storage served from `/api/media/{file}`. Supabase/Cloudinary are optional.

## Optional secrets (not required to boot)
- `DATABASE_URL` — PostgreSQL connection string for durable cloud storage.
- `SUPABASE_URL` / `SUPABASE_SECRET_KEY` — persistent image uploads to Supabase Storage.
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` — admin panel basic auth (default `admin`/`admin`).

## Admin panel
Available at `/api/admin` (HTTP basic auth, default `admin`/`admin`). Create/delete recipes with image upload.

## Tests
```bash
docker compose -f docker-compose.base44.yml exec -T backend sh -c "pip install --quiet pytest && python -m pytest"
```

## Quirks
- Node >= 22.12 required (Vite 8). The compose uses `node:22`.
- Backend imports are flat (`from admin import ...`), so uvicorn must run with cwd = `backend/`.
- Vite config reads `BACKEND_URL` (server-side, not exposed to client) for the dev proxy target.
