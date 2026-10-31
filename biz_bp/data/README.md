# Data Directory

Generated JSON collections are written here by `scripts/make_seed_data.py`.

Expected files:

- `businesses.json` — 120 parent documents.
- `reviews.json` — 600 child documents referencing business and user ObjectIds.
- `export/` — extended-JSON exports of businesses, reviews, users and blacklist.

The dataset is synthetic and deterministic. Do not replace it with the Yelp Open Dataset.

Primary export fallback:

```powershell
.\venv\Scripts\python.exe .\scripts\export_data.py
```

`scripts/export_data.ps1` requires MongoDB Database Tools.