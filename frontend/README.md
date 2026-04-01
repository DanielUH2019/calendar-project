# Calendar Project — Frontend

React UI for the Calendar Project: **rooms**, **reservations**, auth, and admin/settings. Built with [Vite](https://vitejs.dev/), [React](https://react.dev), [TypeScript](https://www.typescriptlang.org/), [TanStack Query](https://tanstack.com/query), [TanStack Router](https://tanstack.com/router), and [Tailwind CSS](https://tailwindcss.com/).

## Requirements

- [Bun](https://bun.sh/) (recommended) or [Node.js](https://nodejs.org/)

## Quick start

```bash
bun install
bun run dev
```

Open <http://localhost:5173>. For full-stack local development (database, API, Mailcatcher), see the root [development.md](../development.md).

The dev server is typically run **outside** Docker for fast reload; use the Docker image when you want a production-like build.

## API client

The TypeScript client under `src/client` is generated from the backend OpenAPI schema.

### Regenerate automatically

- From the repo root (with the backend venv or `uv` environment available):

  ```bash
  bash ./scripts/generate-client.sh
  ```

- Commit the updated `frontend/src/client` files.

### Regenerate manually

1. Run the stack so the API is reachable.
2. Download OpenAPI JSON from `http://localhost/api/v1/openapi.json` (or your backend URL) into `frontend/openapi.json` if your script expects it.
3. From `frontend/`:

   ```bash
   bun run generate-client
   ```

Whenever the API schema changes, regenerate the client so types and requests stay in sync.

## Environment

The API base URL is set at **build time** via:

```env
VITE_API_URL=https://your-api.example.com
```

Use `frontend/.env` for local development. For Render, `VITE_API_URL` is passed as a Docker build-arg—see [deployment.md](../deployment.md#render-blueprint).

## Layout

- `src/` — application source
- `src/assets` — static assets
- `src/client` — generated OpenAPI client
- `src/components` — UI components
- `src/hooks` — hooks
- `src/routes` — file-based routes (pages)

## End-to-end tests (Playwright)

With the stack running (e.g. backend up):

```bash
docker compose up -d --wait backend
bunx playwright test
```

UI mode:

```bash
bunx playwright test --ui
```

Tear down:

```bash
docker compose down -v
```

See [Playwright docs](https://playwright.dev/docs/intro) for more.
