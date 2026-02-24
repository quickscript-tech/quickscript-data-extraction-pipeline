from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class RawProductCard:
    index: int
    data_id: str | None
    category: str | None
    name: str
    price_text: str
    rating_text: str
    reviews_text: str
    stock_text: str
    url: str


def load_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_cards(html: str) -> list[RawProductCard]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.product-card")
    out: list[RawProductCard] = []

    for i, card in enumerate(cards, start=1):
        data_id = (card.get("data-id") or None)
        category = (card.get("data-category") or None)

        name_el = card.select_one(".product-name")
        price_el = card.select_one(".price")
        rating_el = card.select_one(".rating")
        reviews_el = card.select_one(".reviews")
        stock_el = card.select_one(".stock")
        link_el = card.select_one("a.product-link")

        def t(el: Any) -> str:
            return el.get_text(strip=True) if el else ""

        url = (link_el.get("href") if link_el else "") or ""

        out.append(
            RawProductCard(
                index=i,
                data_id=data_id,
                category=category,
                name=t(name_el),
                price_text=t(price_el),
                rating_text=t(rating_el),
                reviews_text=t(reviews_el),
                stock_text=t(stock_el),
                url=url.strip(),
            )
        )

    return out
