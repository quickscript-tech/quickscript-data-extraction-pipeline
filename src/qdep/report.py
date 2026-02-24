from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from statistics import mean
from typing import Iterable

from .transform import Product


def q2(x: float) -> str:
    d = Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{d:.2f}"


@dataclass(frozen=True)
class ReportStats:
    extracted: int
    valid: int
    invalid: int
    categories: dict[str, int]
    min_price: float
    avg_price: float
    max_price: float
    avg_rating: float


def compute_stats(extracted_count: int, valid: list[Product], invalid_count: int) -> ReportStats:
    cats = Counter(p.category for p in valid)
    categories = dict(sorted(cats.items(), key=lambda kv: kv[0]))

    prices = [p.price for p in valid]
    ratings = [p.rating for p in valid]

    if prices:
        min_p = min(prices)
        max_p = max(prices)
        avg_p = mean(prices)
    else:
        min_p = max_p = avg_p = 0.0

    avg_r = mean(ratings) if ratings else 0.0

    return ReportStats(
        extracted=extracted_count,
        valid=len(valid),
        invalid=invalid_count,
        categories=categories,
        min_price=min_p,
        avg_price=avg_p,
        max_price=max_p,
        avg_rating=avg_r,
    )


def render_summary(timestamp_utc: str, stats: ReportStats) -> str:
    lines: list[str] = []
    lines.append(f"timestamp_utc: {timestamp_utc}")
    lines.append(f"extracted_items: {stats.extracted}")
    lines.append(f"valid_items: {stats.valid}")
    lines.append(f"invalid_items: {stats.invalid}")
    lines.append("")
    lines.append("categories_breakdown:")
    for k, v in stats.categories.items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append(f"price_min: {q2(stats.min_price)}")
    lines.append(f"price_avg: {q2(stats.avg_price)}")
    lines.append(f"price_max: {q2(stats.max_price)}")
    lines.append(f"rating_avg: {q2(stats.avg_rating)}")
    return "\n".join(lines) + "\n"


def write_summary(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")