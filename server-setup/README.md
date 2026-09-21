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

## 🎉 Server Setup Complete

Once the backend container is running and joined to
`sla-monitoring-network`, it is reachable through the Nginx reverse proxy at
`api.slamonitoring.hospitia.in`, and Postgres is reachable through Nginx's
TCP passthrough at `db.slamonitoring.hospitia.in:5432`.
