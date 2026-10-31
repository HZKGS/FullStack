# API Endpoints

Base URL: `http://127.0.0.1:5000`

## Authentication header

Protected requests require:

```http
Authorization: Bearer <jwt_token>
```

## Required endpoints

| Method | URL | Permission | Success | Notes |
| :--- | :--- | :--- | :--- | :--- |
| GET | `/api/v1.0/businesses` | Public | 200 | `pn`, `ps`, `q`, repeated `category`, `town`, `min_rating`, `max_rating`, `active`, `sort` |
| POST | `/api/v1.0/businesses` | Authenticated | 201 | Validates required fields and returns `Location` |
| GET | `/api/v1.0/businesses/<id>` | Public | 200 | Invalid ObjectId 400; missing 404 |
| PUT | `/api/v1.0/businesses/<id>` | Authenticated | 200 | Partial allow-listed update |
| DELETE | `/api/v1.0/businesses/<id>` | Admin | 204 | Cascades review deletion |
| GET | `/api/v1.0/businesses/<id>/reviews` | Public | 200 | `pn`, `ps`, `rating`, `sort` |
| POST | `/api/v1.0/businesses/<id>/reviews` | Authenticated | 201 | One review per user/business |
| GET | `/api/v1.0/businesses/<id>/reviews/<rid>` | Public | 200 | Review must belong to business |
| PUT | `/api/v1.0/businesses/<id>/reviews/<rid>` | Owner/Admin | 200 | Ownership is checked |
| DELETE | `/api/v1.0/businesses/<id>/reviews/<rid>` | Admin | 204 | Recomputes business rating |
| GET | `/api/v1.0/login` | Public | 200 | Compatibility endpoint; query or JSON credentials |
| GET | `/api/v1.0/logout` | Authenticated | 200 | Adds JWT `jti` to blacklist |

## Additional endpoints

| Method | URL | Permission | Success | Notes |
| :--- | :--- | :--- | :--- | :--- |
| POST | `/api/v1.0/login` | Public | 200 | Preferred login form; JSON body |
| POST | `/api/v1.0/users` | Public | 201 | Non-admin registration |
| GET | `/api/v1.0/businesses/advanced` | Public | 200 | `$match → $project → $unwind → $match → $sort → $skip → $limit` |
| GET | `/api/v1.0/businesses/stats/by-town` | Public | 200 | `$group` count and average rating by town |
| GET | `/api/v1.0/businesses/nearby` | Public | 200 | `longitude`, `latitude`, `max_distance`, `min_distance` in metres |
| GET | `/health` | Public | 200 | Process-level health only |

## Example login

```http
POST /api/v1.0/login
Content-Type: application/json

{"username":"admin","password":"<local password>"}
```

```json
{
  "token": "<jwt>",
  "token_type": "Bearer",
  "expires_in": 28800,
  "user": {"id":"...","username":"admin","email":"admin@locallens.local","admin":true}
}
```

## Error convention

```json
{"error":"Validation failed","details":["..."]}
```

Routine status codes: 400 validation, 401 missing/invalid/revoked token, 403 insufficient role/ownership, 404 missing resource, 409 duplicate business/username/review.