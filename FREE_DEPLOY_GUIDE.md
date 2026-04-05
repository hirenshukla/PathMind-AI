# PathMind AI - Fully Free Deployment Guide

This guide deploys your project with zero hosting cost:

- Frontend: Vercel (Hobby free)
- Backend API: Render (Free Web Service)
- Database: Neon (Free Postgres)

GitHub profile link: https://github.com/hirenshukla

## 1) Publish this code to GitHub

Create a new repository in your GitHub account, for example:

- `https://github.com/hirenshukla/pathmind-saas`

Upload this full project folder to that repo.

## 2) Create free Neon Postgres

1. Sign in to Neon and create a free project.
2. Create one database (default `neondb` is fine).
3. Copy the connection string and convert/confirm format:

`postgresql+asyncpg://USER:PASSWORD@HOST/DBNAME?sslmode=require`

Keep this value for Render `DATABASE_URL`.

## 3) Deploy backend on Render (free)

1. In Render, connect your GitHub repo.
2. Create a new **Blueprint** from the repo root (uses `render.yaml`).
3. For the generated `pathmind-backend` service, set env vars:

- `DATABASE_URL` = Neon asyncpg URL
- `JWT_SECRET_KEY` = long random string (64+ chars recommended)
- `DATA_GOV_IN_API_KEY` = your data.gov.in key
- `CORS_ORIGINS` = `https://<your-vercel-app>.vercel.app`
- `CORS_ALLOW_ORIGIN_REGEX` = `https://.*\.vercel\.app`
- `TRUSTED_HOSTS` = `<your-backend>.onrender.com`
- `FRONTEND_URL` = `https://<your-vercel-app>.vercel.app`

4. Deploy and wait for healthy status.
5. Verify backend:

- `https://<your-backend>.onrender.com/health`
- `https://<your-backend>.onrender.com/api/v1/realdata/government-jobs`
- `https://<your-backend>.onrender.com/api/v1/realdata/trending-skills`

## 4) Deploy frontend on Vercel (free)

1. Import the same GitHub repo in Vercel.
2. Set **Root Directory** to `frontend`.
3. Set environment variables:

- `API_PROXY_TARGET` = `https://<your-backend>.onrender.com`
- `NEXT_PUBLIC_API_URL` = `/api/v1`

4. Deploy.

The frontend now proxies `/api/v1/*` to Render backend via `frontend/next.config.js` rewrites.

## 5) Final live test checklist

1. Open `https://<your-vercel-app>.vercel.app/app.html`
2. Click demo login and test:
3. Dashboard shows Trending Skills with LIVE badge.
4. Government Sector shows live opportunity cards.
5. Signup/login works.
6. No CORS errors in browser console.

## 6) Free-tier notes (important)

1. Render free backend sleeps after inactivity; first request may be slow.
2. Neon free has usage limits (storage/compute caps).
3. Vercel Hobby is free for hobby/non-commercial scale.

## 7) What is already prepared in this codebase

1. `render.yaml` added for Render free backend blueprint.
2. `backend/.python-version` pinned for stable Python runtime.
3. `frontend/next.config.js` now supports proxy rewrites using `API_PROXY_TARGET`.
4. Backend CORS now supports `CORS_ALLOW_ORIGIN_REGEX`.
5. Real data integrations + fallback behavior are in place and tested.
