from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .validate import ValidationError
from .transform import Product


CSV_COLUMNS = [
    "id",
    "name",
    "price",
    "currency",
    "category",
    "rating",
    "reviews_count",
    "in_stock",
    "url",
]


def write_json(path: Path, valid: list[Product], invalid: list[ValidationError], meta: dict[str, Any]) -> None:
    payload = {
        "meta": meta,
        "items": [p.as_dict() for p in valid],  # already sorted
        "errors": [
            {"id": e.id, "errors": e.errors, "item": e.item}
            for e in invalid  # already sorted
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, valid: list[Product]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for p in valid:  # already sorted
            d = p.as_dict()
            # Keep deterministic float formatting
            d["price"] = f"{d['price']:.2f}"
            d["rating"] = f"{d['rating']:.2f}"
            w.writerow(d)