# Server Setup Guide

This guide explains how to prepare an Ubuntu/Linux server for deploying the
SLA Monitoring application. It mirrors the `server-setup` conventions used by
the Hospitia project (shared Docker network, Nginx as the only public-facing
entrypoint, pinned images, rotated JSON-file logs).

> **Assumptions**
>
> * PostgreSQL and Nginx run on the **same server**.
> * The FastAPI backend (`backend/monitoring`) is built and deployed as its
>   own container, joined to the same Docker network, with container name
>   `sla-monitoring-backend` listening on port `8000` (matches
>   `nginx/conf.d/api.conf`). It is not part of this Compose file, the same
>   way Hospitia's app services are deployed independently of its infra
>   Compose file.
> * The target server is running **Ubuntu/Linux**.

---

## Prerequisites

* Git
* Docker
* Docker Compose

---

## Configure Environment Variables

```bash
cd server-setup
cp .sample.env .env
```

Open `.env` and set real values for `POSTGRES_USER`, `POSTGRES_PASSWORD`, and
`POSTGRES_DB`.

---

## Create the Docker Network

All containers (Postgres, Nginx, and the backend once deployed) must share a
network so they can reach each other by container name.

```bash
docker network create sla-monitoring-network
```

If it already exists, Docker returns an error you can safely ignore.

---

## Start the Infrastructure

```bash
docker compose -f docker-compose.yml up -d
```

Verify both containers are running:

```bash
docker compose ps
```

---

## Domains

| Domain | Points to | Notes |
| --- | --- | --- |
| `slamonitoring.hospitia.in` | Nginx (port 80/443, HTTP) | Serves the built Angular bundle as static files — see `nginx/conf.d/app.conf`. |
| `api.slamonitoring.hospitia.in` | Nginx (port 80/443, HTTP) | Reverse-proxied to `sla-monitoring-backend:8000` — see `nginx/conf.d/api.conf`. |
| `db.slamonitoring.hospitia.in` | Nginx (port 5432, TCP passthrough) | Proxied at L4 (not HTTP) to `sla-monitoring-postgres:5432` — see `nginx/stream.d/postgres.conf`. Postgres itself publishes no port; Nginx is the only container with `5432` exposed to the host. Connect with e.g. `postgresql://<user>:<password>@db.slamonitoring.hospitia.in:5432/sla_monitoring`. |

---

## Deploy the Backend

Build the FastAPI backend image and run it attached to the shared network so
Nginx can reach it by name:

```bash
docker run -d \
  --name sla-monitoring-backend \
  --network sla-monitoring-network \
  --restart on-failure \
  --env-file /path/to/backend.env \
  sla-monitoring-backend:latest
```

Inside `backend.env`, set `POSTGRES_SERVER=sla-monitoring-postgres` (the
Postgres container name) instead of `localhost`, so the backend reaches the
database over the shared Docker network.

> **Ordering note:** Nginx resolves `sla-monitoring-backend` at startup, so it
> will fail to start (or keep restarting) until that container exists on
> `sla-monitoring-network`. Deploy the backend first, or restart Nginx
> afterwards: `docker compose restart nginx`.

---

## Deploy the Frontend

Unlike the backend, the frontend isn't its own container — Nginx serves the
built bundle directly as static files, off the host filesystem, via the bind
mount already declared in `docker-compose.yml`
(`../frontend/sla-monitoring/dist/sla-monitoring/browser` →
`/usr/share/nginx/html`, read-only). That path is relative to this repo's
root, wherever it's cloned on the server — e.g. if this repo lives at
`/home/smit/sla-monitoring`, Nginx ends up serving
`/home/smit/sla-monitoring/frontend/sla-monitoring/dist/sla-monitoring/browser/index.html`.
So the only step is building it in place:

```bash
cd frontend/sla-monitoring
npm ci
npm run build
```

That writes `dist/sla-monitoring/browser/index.html` (and the hashed
JS/CSS), which `nginx/conf.d/app.conf` serves at `slamonitoring.hospitia.in`
— `location /` falls back to `index.html` for any unmatched path
(`try_files $uri $uri/ /index.html`) so Angular's client-side router handles
deep links like `/files/:guid` correctly, while hashed static assets
(`*.js`, `*.css`, fonts, images) get a long-lived `Cache-Control` header
since a new build always ships under a new filename.

Nginx only reads this directory at request time (no build step of its own),
so a redeploy is just: rebuild, then nothing else — the next request picks
up the new files immediately. If Nginx was started before the first build
ever ran, restart it once so it re-resolves the now-populated mount:
`docker compose restart nginx`.

Before setting the `apiBaseUrl` in `src/environments/environment.prod.ts`,
point it at `http://api.slamonitoring.hospitia.in/api/v1` — self-hosting the
frontend on this domain avoids the cross-origin request that the previous
Vercel-hosted frontend needed `ALLOWED_ORIGINS` for, but the backend must
still allow this domain if you keep both deployments around.

---

## 🎉 Server Setup Complete

Once the backend container is running and joined to
`sla-monitoring-network`, and the frontend has been built at least once, the
full app is reachable through Nginx: the dashboard at
`slamonitoring.hospitia.in`, the API reverse-proxied at
`api.slamonitoring.hospitia.in`, and Postgres through Nginx's TCP
passthrough at `db.slamonitoring.hospitia.in:5432`.
