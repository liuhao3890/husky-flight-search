# husky-flight-search

MVP: Points/award flight search helper (like Point.me / PointsYeah), starting with **link-out + saved searches**.

## What it does (v0)
- Save award search intents (origin/destination/date window/cabin/pax)
- Generate provider-specific link-outs for:
  - United MileagePlus
  - American AAdvantage
  - Alaska Mileage Plan
  - Air Canada Aeroplan
  - Avianca LifeMiles
  - ANA Mileage Club
  - Korean Air SKYPASS

No scraping. No automated availability checking (yet).

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000

## Roadmap
- Better provider deep links + prefilled parameters
- Auth + multi-user
- Real availability sources (APIs where available)
- Alerts/watchlists
