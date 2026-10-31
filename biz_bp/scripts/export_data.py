"""Export each LocalLens collection as MongoDB Extended JSON.

This is a fallback for environments where the MongoDB Database Tools
(mongoexport) are not installed. It never prints credentials.
"""

from __future__ import annotations

import sys
from pathlib import Path

from bson import json_util

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from globals import DB  # noqa: E402

EXPORT_DIR = ROOT / "data" / "export"
COLLECTIONS = ("businesses", "reviews", "users", "blacklist")


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    for name in COLLECTIONS:
        documents = list(DB[name].find({}))
        output = EXPORT_DIR / f"{name}.json"
        output.write_text(
            json_util.dumps(documents, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Exported {len(documents)} documents from {name} to {output}")
    print("Note: users.json contains password hashes, not plaintext passwords.")


if __name__ == "__main__":
    main()