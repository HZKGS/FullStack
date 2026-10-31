# LocalLens API

Flask + MongoDB coursework API for a local-business/review directory. The project implements the endpoint table in `G:\FullStack\AGENT.md`, JWT blacklist logout, role checks, pagination, multi-value filters, aggregation, geospatial search, deterministic synthetic data and a Postman collection.

## 1. Structure

```text
biz_bp/
├── app.py
├── globals.py                 # env loading, MongoDB connections, indexes
├── decorators.py              # JWT blacklist and admin checks
├── utils.py
├── requirements.txt
├── requirements.lock.txt
├── make_dataset.py            # AGENT.md compatibility entry point
├── create_users.py            # AGENT.md compatibility entry point
├── blueprints/
│   ├── auth/auth.py
│   ├── businesses/businesses.py
│   └── reviews/reviews.py
├── data/                      # generated JSON and extended-JSON exports
├── docs/                      # endpoint, schema, verification and self-assessment notes
├── postman/                   # importable 17-request collection
├── scripts/
│   ├── init_local_env.ps1
│   ├── start_mongo.ps1
│   ├── make_seed_data.py
│   ├── import_seed_data.py
│   ├── import_data.ps1
│   ├── create_users.py
│   ├── export_data.py
│   ├── export_data.ps1
│   └── run_smoke_test.ps1
├── tests/
│   └── test_api_smoke.py
└── venv/                      # local virtual environment, gitignored
```

## 2. Local startup

The project-local virtual environment and MongoDB server are already prepared on this machine.

```powershell
Set-Location 'G:\FullStack\biz_bp'
.\scripts\init_local_env.ps1      # creates gitignored .env.local if absent
.\scripts\start_mongo.ps1         # starts project-local mongod on 127.0.0.1:27017
.\venv\Scripts\python.exe .\scripts\import_seed_data.py
.\venv\Scripts\python.exe .\create_users.py
.\venv\Scripts\python.exe .\app.py
```

`globals.py` reads `.env.local` without a dotenv dependency. The file is gitignored and contains generated local-only credentials. Do not copy it into the submission package.

MongoDB data is stored only in `G:\FullStack\.mongo\data`; the project-local server is under `G:\FullStack\.mongo\server`.

## 3. Seed data

```powershell
.\venv\Scripts\python.exe .\make_dataset.py
.\venv\Scripts\python.exe .\scripts\import_seed_data.py
```

Expected seed size: 120 businesses, 600 reviews and four demo users.

The primary importer uses PyMongo because MongoDB Database Tools (`mongoimport`, `mongoexport`) are not included in the extracted server package. `scripts\import_data.ps1` remains available if the tools are installed.

## 4. Tests

```powershell
Set-Location 'G:\FullStack\biz_bp'
.\scripts\run_smoke_test.ps1
```

The test uses the real local MongoDB database and covers authentication, blacklist logout, business/review CRUD, permissions, pagination, category filtering, the seven-stage aggregation, town grouping and `$geoNear`.

Evidence: `docs\TEST_EVIDENCE.md` and `G:\FullStack\WORKLOG.md`.

## 5. Postman

Import `postman/LocalLens.postman_collection.json` into Postman Desktop.

1. Confirm `base_url` is `http://127.0.0.1:5000`.
2. Read `ADMIN_PASSWORD` from the gitignored `.env.local` and place it in the collection's `admin_password` variable; do not save it into a committed environment file.
3. Run the collection in order.
4. Export the run result for the final submission PDF.

The collection JSON validates and contains 17 ordered requests. A Postman Desktop run is still pending because no Postman CLI/Newman command is available on `PATH`.

## 6. Additional query endpoints

- `GET /api/v1.0/businesses/advanced` — required multi-stage aggregation.
- `GET /api/v1.0/businesses/stats/by-town` — grouped town statistics.
- `GET /api/v1.0/businesses/nearby` — `$geoNear` search, distances in metres.
- `POST /api/v1.0/users` — account registration.

## 7. Export

```powershell
.\venv\Scripts\python.exe .\scripts\export_data.py
```

Extended JSON files are written to `data\export`. If MongoDB Database Tools are installed later, `scripts\export_data.ps1` can produce official `mongoexport` output instead.

## 8. Verification status

- Automated API smoke test: passed on 2026-10-18.
- Live HTTP check: passed on port 5001.
- Postman Desktop execution: pending.
- Submission ZIP/PDF/video package: pending.