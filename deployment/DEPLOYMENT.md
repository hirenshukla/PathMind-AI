# PathMind Production Deployment

This guide deploys PathMind with:
- FastAPI backend
- Next.js frontend
- PostgreSQL
- Redis
- Caddy reverse proxy with automatic HTTPS (Let's Encrypt)

## 1) Prerequisites

- Docker + Docker Compose plugin installed
- Public server with ports `80` and `443` open
- DNS records already pointed to your server IP:
  - `pathmind.ai` (or your root domain)
  - `www.pathmind.ai`
  - `api.pathmind.ai`

## 2) Configure Environment

```bash
cd deployment
cp .env.example .env
```

Edit `deployment/.env` and set all required values:
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `APP_DOMAIN`, `WWW_DOMAIN`, `API_DOMAIN`
- `LETSENCRYPT_EMAIL`
- `CORS_ORIGINS`, `TRUSTED_HOSTS`
- `NEXT_PUBLIC_API_URL`

## 3) Start Production Stack

```bash
cd deployment
docker compose up -d --build
```

## 4) Verify Health

```bash
docker compose ps
docker compose logs backend --tail 100
docker compose logs caddy --tail 100
```

Expected:
- `backend` is healthy
- `frontend` is healthy
- `caddy` is running and issues certificates automatically

Then test:
- `https://<APP_DOMAIN>`
- `https://<API_DOMAIN>/health`

## 5) Updates / Rollback

Update:
```bash
git pull
cd deployment
docker compose up -d --build
```

Rollback to previous image tag:
- Pin image tags in compose and redeploy.

## 6) Common Issues

- Backend unhealthy:
  - Check `DATABASE_URL` and `POSTGRES_PASSWORD` match.
  - Run `docker compose logs backend --tail 200`.
- HTTPS cert not issued:
  - Confirm DNS is correct and propagated.
  - Confirm ports `80/443` are open.
  - Check `docker compose logs caddy --tail 200`.
- CORS blocked:
  - Ensure browser origin is included in `CORS_ORIGINS`.

