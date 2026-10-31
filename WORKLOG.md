# WORKLOG.md

## 2026-10-18

### Environment and scope

- Worked only under `G:\FullStack`.
- Read `AGENT.md`, `AGENT_RULES.md`, `AGENT_RULE.md`, project Markdown notes and the two-page `FullStack软件安装2026.pdf`.
- Confirmed the project virtual environment contains:
  - Flask 3.1.3
  - Flask-CORS 6.0.5
  - PyJWT 2.15.1
  - bcrypt 5.0.0
  - pymongo 4.19.0
- MongoDB Server was not exposed on `PATH`, so the existing MongoDB 9.0.4 MSI was extracted into the project-only directory `G:\FullStack\.mongo\server`. No system-wide MongoDB installation was created.
- Started `mongod` with `--dbpath G:\FullStack\.mongo\data` and bound it to `127.0.0.1:27017`.

### Data

- Regenerated the deterministic seed data with `businesses.json` and `reviews.json`.
- Imported 120 businesses and 600 reviews into the `locallens` database with the project import script.
- Created four demo users (`admin` plus three ordinary users) using bcrypt hashes.
- Created a gitignored `.env.local` with generated local-only JWT/password values. Secret values were not printed to the log.

### Verification

- `python -m unittest -v tests.test_api_smoke` passed.
- The end-to-end test covered:
  - health check;
  - admin and ordinary-user login;
  - business pagination, category filter and validation;
  - business create/read/update/delete;
  - administrator-only business deletion;
  - review create/read/update/delete;
  - review ownership and admin permission checks;
  - CORS response header, duplicate 409 and unauthenticated 401 checks;
  - the required seven-stage aggregation pipeline;
  - town grouping aggregation;
  - `$geoNear` nearby search;
  - logout and JWT blacklist rejection.
- A live Flask process on port 5002 completed a real-HTTP create/review/delete/logout flow.
  - CORS response header: `http://localhost:4200`
  - revoked token check: `401`
  - live HTTP result: `passed`
- The Postman collection JSON parses and contains 17 ordered requests. It has not yet been executed in the Postman desktop client because no Postman CLI/Newman command is available on `PATH`.

### Data export

- Exported all four collections to `G:\FullStack\biz_bp\data\export` using the project Python fallback.
- Wrote exact installed package versions to `requirements.lock.txt`.

### Known follow-up

- MongoDB Database Tools (`mongoimport`, `mongoexport`) are not present in the extracted server package. The project therefore uses Python import/export fallbacks until the tools are installed.
- Open the Postman collection in the desktop app, set the local admin credentials, run it and export the run evidence PDF.
- Produce the final submission ZIP/PDF/video package after the remaining verification evidence is captured.
### Angular frontend

- Replaced the Angular starter template with a LocalLens directory UI.
- Added live API loading from Flask on port 5000.
- Added business search, category filters, pagination, rating/price display and top-town aggregation cards.
- Added loading, empty and backend-offline states.
- Added `provideHttpClient` and component tests.
- Added `G:\FullStack\run_locallens.ps1` and `stop_locallens.ps1`.
- Production build passed after adjusting the component stylesheet budget to 12/16 kB.
- Angular tests passed: 1 test file, 2 tests.
- Headless Chrome screenshot confirmed 120 businesses rendered with live MongoDB data.
- Running services verified: MongoDB 27017, Flask 5000 and Angular 4200.