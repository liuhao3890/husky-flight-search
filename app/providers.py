from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote


@dataclass(frozen=True)
class Provider:
    id: str
    name: str
    region: str
    note: str
    url: str


# NOTE: Link-outs are intentionally conservative (no scraping).
# Some programs don't support deep-link prefills reliably; we still create a useful starting URL.

PROVIDERS: list[dict] = [
    {
        "id": "united",
        "name": "United MileagePlus",
        "region": "US",
        "note": "Official award search (may require login).",
        "url": "https://www.united.com/en/us/book-flight",
    },
    {
        "id": "aa",
        "name": "American AAdvantage",
        "region": "US",
        "note": "Official award search (AA.com).",
        "url": "https://www.aa.com/booking/find-flights",
    },
    {
        "id": "alaska",
        "name": "Alaska Mileage Plan",
        "region": "US",
        "note": "Official award search (AlaskaAir.com).",
        "url": "https://www.alaskaair.com/search",
    },
    {
        "id": "aeroplan",
        "name": "Air Canada Aeroplan",
        "region": "Canada",
        "note": "Air Canada flight reward search.",
        "url": "https://www.aircanada.com/ca/en/aco/home/book/flights.html",
    },
    {
        "id": "lifemiles",
        "name": "Avianca LifeMiles",
        "region": "Latin America",
        "note": "LifeMiles award booking portal (often requires login).",
        "url": "https://www.lifemiles.com/",
    },
    {
        "id": "ana",
        "name": "ANA Mileage Club",
        "region": "Japan",
        "note": "ANA award search (usually requires login).",
        "url": "https://www.ana.co.jp/en/us/amc/",
    },
    {
        "id": "koreanair",
        "name": "Korean Air SKYPASS",
        "region": "Korea",
        "note": "Korean Air award search (requires login).",
        "url": "https://www.koreanair.com/",
    },
]


def build_links(
    origin: str,
    destination: str,
    depart_start: Optional[str] = None,
    depart_end: Optional[str] = None,
    cabin: str = "economy",
    passengers: int = 1,
    **_: object,
) -> list[dict]:
    """Return provider link-outs.

    For v0 we keep links mostly generic. We include a short prefilled hint in the URL fragment
    for quick copy/paste.
    """

    hint = f"{origin}-{destination} {depart_start or ''}{'..' + depart_end if depart_end else ''} {cabin} x{passengers}".strip()
    hint_q = quote(hint)

    out = []
    for p in PROVIDERS:
        out.append(
            {
                "provider": p,
                "url": p["url"] + ("#" + hint_q if hint else ""),
                "hint": hint,
            }
        )
    return out
