"""生成結果のローカル履歴（data/history.json）。個人用なので DB は使わない。"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_FILE = DATA_DIR / "history.json"
MAX_ITEMS = 200


def load() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _write(items: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(items[:MAX_ITEMS], ensure_ascii=False, indent=2), encoding="utf-8"
    )


def add(tool: str, title: str, output: str, meta: dict | None = None) -> None:
    items = load()
    items.insert(
        0,
        {
            "id": uuid.uuid4().hex[:12],
            "tool": tool,
            "title": (title or "無題").strip()[:80],
            "output": output,
            "meta": meta or {},
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
    )
    _write(items)


def delete(item_id: str) -> None:
    _write([i for i in load() if i["id"] != item_id])


def clear() -> None:
    _write([])
