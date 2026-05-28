# REST API (v1-style)

Base URL: `http://127.0.0.1:5001` (dev).

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/sessions` | Login → `{ user, token }` |
| DELETE | `/api/auth/sessions` | Logout (client drops JWT; `204`) |
| POST | `/api/auth/token/validation` | Body `{ "token" }` → validate |
| POST | `/api/users` | Register → `201` |
| GET | `/api/users/me` | Current user + `library_stats` (Bearer) |
| PATCH | `/api/users/me` | Update `name`, `profile_pic` (Bearer) |
| PATCH | `/api/users/me/password` | Change password (Bearer) |
| GET | `/api/library/items` | List items; `?q=`, `?is_favorite=true` (Bearer) |
| POST | `/api/library/items` | Add item (Bearer) |
| GET/PATCH/PUT/DELETE | `/api/library/items/<id>` | One item (Bearer); delete → `204` |
| GET | `/api/library/statistics` | Counts (Bearer) |

**OpenAPI:** [`/openapi.yaml`](/openapi.yaml) · **Swagger UI:** [`/docs`](/docs)

Legacy `/auth/login`, `/auth/register`, etc. are **removed** — use the table above.
