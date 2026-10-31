# Test Evidence

## Date

2026-10-18 (Asia/Shanghai)

## Environment

- Project root: `G:\FullStack`
- Flask app: `G:\FullStack\biz_bp`
- Python environment: `G:\FullStack\biz_bp\venv`
- MongoDB: project-local `mongod` 9.0.4 at `G:\FullStack\.mongo\server`
- Database: `locallens`
- Data: 120 businesses, 600 reviews, 4 demo users

## Automated smoke test

Command:

```powershell
Set-Location 'G:\FullStack\biz_bp'
.\scripts\run_smoke_test.ps1
```

Result:

```text
MongoDB is already listening on 127.0.0.1:27017.
test_end_to_end (tests.test_api_smoke.LocalLensApiSmokeTest.test_end_to_end) ... ok
----------------------------------------------------------------------
Ran 1 test in 1.314s

OK
```

Coverage includes authentication, JWT blacklist, business CRUD, review CRUD, role/ownership checks, CORS, duplicate/unauthorized responses, pagination, multi-value category filtering, aggregation, geospatial query and validation errors.

## Live HTTP check

The Flask app was started on port 5002 for an isolated real-HTTP check and stopped afterwards. The flow created a temporary business and review, exercised a CORS request, deleted both resources, logged out and confirmed the revoked token returned 401.

Observed summary:

```text
live_http=passed cors=http://localhost:4200 revoked_token_401=True
```

## Postman

- Collection: `postman/LocalLens.postman_collection.json`
- Requests: 17
- JSON validation: passed
- Live Postman Desktop run: pending
- Reason: Postman Desktop is installed, but no Postman CLI/Newman command is available on `PATH`.

## Security note

No password, JWT secret or token is recorded in this evidence file. Local credentials live only in the gitignored `G:\FullStack\biz_bp\.env.local` file.