# Recipe Website

A modern, full-stack recipe management web application featuring a **FastAPI** backend (JSON API and server-rendered admin panel with authentication) and a **Vue 3 + Vite** single-page application frontend, deployed together on Vercel.

- Browse and search recipes, view detailed instructions with unit conversions, and save your personal favorite recipes (synchronized via Supabase Auth & stored locally/remotely).
- Manage recipes securely from the admin panel (`/api/admin`), complete with image uploads (Supabase Storage / local database) and multiple rotating example recipe templates.
- Backend data persistence uses SQL (PostgreSQL when `DATABASE_URL` is set, otherwise local SQLite).

## Table of Contents
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Admin Panel](#admin-panel)
- [Testing](#testing)
- [Docker](#docker)
- [Deploying to Vercel](#deploying-to-vercel)

## Tech Stack

**Backend** — FastAPI, Uvicorn, SQLAlchemy 2, Pydantic, Jinja2 (admin templates), Mangum (Vercel ASGI adapter), psycopg2.

**Frontend** — Vue 3 (`<script setup>` Composition API), Vue Router, Vite, Supabase JS client for authentication, plain `fetch` (`frontend/src/api.js`).

## Project Structure

```
backend/    FastAPI application: main.py (API), admin.py (admin panel), store.py (SQLAlchemy storage),
            models.py (Pydantic models), templates/, tests/, Dockerfile
frontend/   Vue 3 + Vite SPA: views/ (Home, Recipes, Recipe, Auth), components/, composables/
api/        Vercel serverless entrypoint re-exporting the FastAPI app
vercel.json Build and routing configuration for Vercel deployment
```

## Quick Start

Requires **Node >= 22.12** (see `.nvmrc`) and **Python >= 3.11**.

### 1. Backend (API on http://localhost:8000)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd backend
SITE_BASE_URL=http://localhost:5173 python -m uvicorn main:app --reload --port 8000
```

### 2. Frontend (SPA on http://localhost:5173)
```bash
cd frontend
npm install
npm run dev
```

`frontend/vite.config.js` proxies `/api`, `/api/media`, and `/api/static` to `http://localhost:8000`.

## Environment Variables

| Variable | Where | Default | Purpose |
| --- | --- | --- | --- |
| `DATABASE_URL` | backend / Vercel | `""` (local SQLite) | PostgreSQL connection string (`POSTGRES_URL` also supported) |
| `SUPABASE_URL` | backend / Vercel / frontend | `""` | Supabase project URL for Auth & Storage uploads |
| `SUPABASE_SECRET_KEY` / `SUPABASE_SERVICE_ROLE_KEY` | backend / Vercel | `""` | Server-only Supabase secret key for Storage uploads |
| `SUPABASE_STORAGE_BUCKET` | backend / Vercel | `recipe-images` | Public Supabase Storage bucket for recipe images |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | backend | `admin` / `admin` | Basic auth credentials for `/api/admin` |
| `SITE_BASE_URL` | backend | `""` | Base URL for admin panel links |
| `RECIPE_DATA_DIR` | backend | `backend/data` | Local SQLite data directory |

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Health check payload |
| GET | `/api/recipes` | List recipes (`?q=` searches title, description, and ingredients) |
| GET | `/api/recipes/{id}` | Retrieve a single recipe by ID |
| POST | `/api/recipes` | Create a new recipe |
| DELETE | `/api/recipes/{id}` | Delete a recipe by ID |
| GET | `/api/admin` | Server-rendered admin panel (HTTP Basic Auth) |
| GET | `/api/media/{file}` | Serve uploaded media files |

## Admin Panel

Access http://localhost:8000/api/admin with your admin credentials. The panel allows you to create, edit, and delete recipes, upload images, or instantly load rotating example recipe templates.

## Testing

Run backend tests with pytest:
```bash
cd backend && ../.venv/bin/python -m pytest
```

## Docker

Build and run the backend container:
```bash
docker build -t recipe-backend backend
docker run -d -p 8000:8000 --name recipe-backend recipe-backend
```
