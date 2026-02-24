from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .transform import Product


@dataclass(frozen=True)
class ValidationError:
    id: str
    errors: list[str]
    item: dict[str, Any]


def validate_product(p: Product) -> list[str]:
    errs: list[str] = []

    if not p.name:
        errs.append("name must be non-empty")
    if not p.url:
        errs.append("url must be present")

    if not (p.price > 0):
        errs.append("price must be > 0")
    if not (0.0 <= p.rating <= 5.0):
        errs.append("rating must be between 0 and 5")
    if not (p.reviews_count >= 0):
        errs.append("reviews_count must be >= 0")

    return errs


def partition_valid(products: list[Product]) -> tuple[list[Product], list[ValidationError]]:
    valid: list[Product] = []
    invalid: list[ValidationError] = []

    for p in products:
        errs = validate_product(p)
        if errs:
            invalid.append(ValidationError(id=p.id, errors=errs, item=p.as_dict()))
        else:
            valid.append(p)

    # Deterministic ordering
    valid.sort(key=lambda x: x.id)
    invalid.sort(key=lambda x: x.id)
    return valid, invalid