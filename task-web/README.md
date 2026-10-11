# Family task web

React Router framework SPA with React, TypeScript, Mantine, Axios and TanStack Query. Public UI is in Russian. Node.js >=22.22.0 is required (`.nvmrc` is included).

## Local development

```sh
cd task-web
npm ci
cp .env.example .env
npm run dev
```

Open http://localhost:5173. Start FastAPI separately on port 8000. Vite proxies `/api` to `API_PROXY_TARGET` (default `http://localhost:8000`), so browser requests are same-origin. `VITE_API_BASE_URL` defaults to `/api/v1`; it is a public build-time value and must never contain secrets. PowerShell users can use `Copy-Item .env.example .env`.

## Docker Compose

From the repository root, configure the backend `.env` using the root `.env.example`, then run:

```sh
docker compose up --build
```

The `web` service runs Vite on http://localhost:5173 with mounted sources and a container-only dependency volume. It proxies API calls to `app:8000`. `npm ci` at startup keeps the volume consistent with the lockfile.

To serve the static frontend through nginx instead:

```sh
docker compose -f docker-compose.yml -f compose.production.yml up --build
```

Open http://localhost:8080. The override requires Docker Compose 2.24.4+ for `!override`. It changes only the frontend: backend deployment hardening is outside this scaffold. nginx handles deep links and proxies `/api/` without rewriting the API prefix. No Node server is needed at runtime. Vite builds the SPA shell at build time; routes and API data load on the client.

## Structure

- `app/root.tsx`: document, Mantine, notifications, session hydration and QueryClient lifecycle.
- `app/routes.ts`: route registration and lazy route modules.
- `app/routes/`: login, registration, board list, board tasks, task details, member addition, profile, protected layout and fallback.
- `app/api/contracts.ts`: types mirrored from the inspected Pydantic schemas.
- `app/api/client.ts`: Axios transport, bearer token and Russian error messages.
- `app/api/resources.ts`: all currently declared v1 operations.
- `app/api/queries.ts`: query keys, cancellable queries, mutations and invalidation.
- `app/features/forms.tsx`: reusable validated board/task forms.
- `app/shared/`: theme, session, UI primitives and display labels.
- `app/styles/`: global styles, light/dark tokens and responsive layout.

## State and authentication

TanStack Query owns server data; Zustand owns only the session token. Tokens live in memory and `sessionStorage` for the current browser tab. Session hydration happens after mounting. Signing out or changing the token creates a fresh QueryClient and clears the old cache. Authenticated 401 responses clear the matching session; late responses from another session do not. There is no refresh/logout endpoint, so logout is local and an expired session requires signing in again.

Client redirects improve navigation; actual authorization remains the backend's responsibility. Board ownership controls display of board settings. The current API does not expose a user's membership role, so fine-grained task/member permissions are enforced by the server and shown through 403 messages.

## API contract notes

Contracts were checked against `app/api/v1/`, `app/schemas/` and `app/main.py`. Service/repository/database behavior was not inspected. The live API was unavailable during scaffolding.

- Login uses JSON `{ email, password }`, despite the endpoint docstring mentioning form-data.
- Registration requires `name`, `email`, `phone`, `birthday` (nullable), `timezone` and `password`. It returns a user, so the UI redirects to login instead of assuming a token response.
- Boards use `/boards/` for listing and `/boards/create_board` for creation.
- Tasks use `limit`/`offset`, status, importance, responsible UUID and search filters. Search is 2–100 characters; limits are 1–200. The page requests 20 items and supports nullable totals.
- `done` is set through `/complete`, not the status PATCH. `/reopen` returns a task to work.
- Task editing preserves explicit nulls to clear description, deadline and responsible user.
- The current board detail endpoint returns `BoardResponse`, not the richer unused `BoardDetailResponse`. There is no member-list, member removal/role edit, user lookup, profile editing, password reset, file upload or real-time endpoint in the inspected routes. These features are not fabricated. Members and responsible users currently use UUID input; the profile lets a user copy their UUID.

Generate a comparison contract from a running backend:

```sh
npm run api:generate
```

This writes `app/api/openapi.generated.ts`. It does not silently replace the source-backed contracts; review generated differences and update `contracts.ts` and API calls together.

## UI and dependencies

Mantine provides components, theme handling and notifications. The default palette uses warm neutral backgrounds and sage accents. Light/dark CSS tokens and a theme switch are included. The small shared UI layer keeps app wording and layout consistent without duplicating the entire Mantine API. Tailwind, tailwind-merge, class-variance-authority and Sonner are omitted because their styling/notification roles are covered here. Upload, masking and drag-and-drop packages are deferred until those features are implemented. `isbot` is required by React Router's generated build entry, even in SPA mode.

## Checks

```sh
npm run typecheck
npm run build
npm run format:check
```

Docker configuration can be validated without a running engine:

```sh
docker compose --env-file .env.example config --quiet
docker compose --env-file .env.example -f docker-compose.yml -f compose.production.yml config --quiet
```

The backend Docker build and end-to-end API operations require a working Docker engine and backend environment. A successful frontend build does not verify backend permissions or persistence.
