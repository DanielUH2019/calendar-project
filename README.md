# Calendar Project

A full-stack web app for **managing rooms and reservations**: authenticated users can maintain rooms, check availability by date range and capacity, and create reservations that avoid overlapping bookings.

## What it does

- **Rooms** — capacity, ownership, and CRUD for room records.
- **Reservations** — date-bounded bookings tied to rooms, with availability checks for the requested window.
- **Accounts** — JWT auth, optional superuser admin flows, password recovery when SMTP is configured.

## Stack

| Layer    | Technology |
| -------- | ---------- |
| API      | [FastAPI](https://fastapi.tiangolo.com), [SQLModel](https://sqlmodel.tiangolo.com), [Alembic](https://alembic.sqlalchemy.org), PostgreSQL |
| Frontend | [React](https://react.dev), [TypeScript](https://www.typescriptlang.org/), [Vite](https://vitejs.dev), [TanStack Router](https://tanstack.com/router) & [Query](https://tanstack.com/query), [Tailwind CSS](https://tailwindcss.com) |
| Ops      | Docker Compose (local), optional [Traefik](https://traefik.io) on your server, or [Render](https://render.com) via [`render.yaml`](./render.yaml) |
| Tests    | [pytest](https://pytest.org) (API), [Playwright](https://playwright.dev) (E2E) |

## Quick start

1. Copy [`.env.example`](./.env.example) to `.env` and set secrets (see below).
2. Start the stack:

   ```bash
   docker compose watch
   ```

3. Open the app at <http://localhost:5173> and the API docs at <http://localhost:8000/docs>.

For hybrid local runs (frontend or backend outside Docker), ports, Mailcatcher, and Traefik tips, see **[development.md](./development.md)**.

## Configuration

Before any real deployment, change at least:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD` (when not using a provider URL)

Generate values with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

`PROJECT_NAME`, `FRONTEND_HOST`, and `BACKEND_CORS_ORIGINS` should match your public frontend URL so CORS and email links work. On Render, the frontend is built with **`VITE_API_URL`** at **image build time**; changing the API URL later requires rebuilding the web service—see [deployment.md](./deployment.md#render-blueprint).

## Documentation

| Topic | Doc |
| ----- | --- |
| Local development | [development.md](./development.md) |
| Deploy (Traefik + Docker Compose, Render blueprint) | [deployment.md](./deployment.md) |
| Backend | [backend/README.md](./backend/README.md) |
| Frontend | [frontend/README.md](./frontend/README.md) |

## Release notes

See [release-notes.md](./release-notes.md).

## License

This project is licensed under the MIT License. (It originated from the [FastAPI full-stack template](https://github.com/fastapi/full-stack-fastapi-template); this repository focuses on the calendar and room-reservation domain.)
