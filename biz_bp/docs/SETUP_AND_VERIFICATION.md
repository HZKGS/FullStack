# Setup and Verification Checklist

## Environment

- [x] Work only inside `G:\FullStack`.
- [x] Use the existing `biz_bp` virtual environment (path: `G:\FullStack\biz_bp\venv`).
- [x] Confirm Flask, Flask-CORS, PyJWT, bcrypt and PyMongo imports.
- [x] Extract MongoDB 9.0.4 server into `G:\FullStack\.mongo\server`.
- [x] Start MongoDB with `--dbpath G:\FullStack\.mongo\data`.
- [x] Generate local-only `.env.local`.
- [x] Set `JWT_SECRET`, `ADMIN_PASSWORD`, `USER_PASSWORD` through `.env.local`.
- [x] Run `make_dataset.py`.
- [x] Import seed JSON with `import_seed_data.py`.
- [x] Run `create_users.py`.
- [x] Start the Flask app.

## API checks

- [x] `GET /health` returns 200.
- [x] Admin login returns a token.
- [x] Ordinary-user login returns a token.
- [x] Business pagination and category filters work.
- [x] Business create/read/update/delete return 201/200/200/204.
- [x] Review create/read/update/delete return 201/200/200/204.
- [x] Non-admin DELETE returns 403.
- [x] Logout returns 200 and the same token then returns 401.
- [x] Advanced pipeline returns `pipeline_stages` in the required order.
- [x] Town aggregation returns grouped counts.
- [x] Nearby search returns `distance_m`.
- [ ] Postman collection passes in Postman Desktop.

## Evidence

- [x] Automated smoke test: `docs\TEST_EVIDENCE.md`.
- [x] Extended JSON export: `data\export`.
- [ ] Postman run output saved as PDF.
- [ ] Code-listing and endpoint-summary PDFs.
- [ ] Demonstration video no longer than five minutes.
- [ ] Self-assessment PDF.
- [ ] Final code/data ZIPs.

## Status

Automated and live-HTTP checks passed on 2026-10-18. Postman Desktop and final submission artefacts remain.