from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from .extract import RawProductCard


CURRENCY_SYMBOL_MAP = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
}


def stable_id(name: str, url: str, fallback_index: int, explicit: str | None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    base = f"{name}|{url}|{fallback_index}".encode("utf-8")
    return hashlib.sha1(base).hexdigest()[:12]


def parse_currency(price_text: str) -> str:
    for sym, code in CURRENCY_SYMBOL_MAP.items():
        if sym in price_text:
            return code
    # also allow explicit codes in fixture/text
    for code in ("USD", "EUR", "GBP"):
        if code in price_text.upper():
            return code
    return "UNK"


def parse_price(price_text: str) -> float | None:
    # Extract the first number-like token. Demo expects dot decimals in fixture.
    # Examples: "$39.99", "€24.50"
    m = re.search(r"([-+]?\d+(?:\.\d+)?)", price_text.replace(",", ""))
    if not m:
        return None
    try:
        d = Decimal(m.group(1))
    except (InvalidOperation, ValueError):
        return None
    return float(d)


def parse_rating(rating_text: str) -> float | None:
    m = re.search(r"([-+]?\d+(?:\.\d+)?)", rating_text)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def parse_reviews_count(reviews_text: str) -> int | None:
    m = re.search(r"(-?\d+)", reviews_text.replace(",", ""))
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def parse_in_stock(stock_text: str) -> bool:
    s = stock_text.strip().lower()
    return "in stock" in s


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    price: float
    currency: str
    category: str
    rating: float
    reviews_count: int
    in_stock: bool
    url: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "category": self.category,
            "rating": self.rating,
            "reviews_count": self.reviews_count,
            "in_stock": self.in_stock,
            "url": self.url,
        }


def transform(card: RawProductCard) -> Product:
    cur = parse_currency(card.price_text)
    price = parse_price(card.price_text)
    rating = parse_rating(card.rating_text)
    reviews = parse_reviews_count(card.reviews_text)
    category = (card.category or "").strip()

    pid = stable_id(card.name.strip(), card.url.strip(), card.index, card.data_id)

    # Use safe defaults; validation will reject if required constraints not met.
    return Product(
        id=pid,
        name=card.name.strip(),
        price=price if price is not None else -1.0,
        currency=cur,
        category=category,
        rating=rating if rating is not None else -1.0,
        reviews_count=reviews if reviews is not None else -1,
        in_stock=parse_in_stock(card.stock_text),
        url=card.url.strip(),
    )