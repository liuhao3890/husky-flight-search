from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.providers import PROVIDERS, build_links

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR.parent / "husky.sqlite"


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                depart_start TEXT,
                depart_end TEXT,
                cabin TEXT NOT NULL,
                passengers INTEGER NOT NULL,
                notes TEXT
            );
            """
        )


@dataclass
class Search:
    id: int
    created_at: str
    origin: str
    destination: str
    depart_start: Optional[str]
    depart_end: Optional[str]
    cabin: str
    passengers: int
    notes: Optional[str]


def row_to_search(r: sqlite3.Row) -> Search:
    return Search(
        id=int(r["id"]),
        created_at=str(r["created_at"]),
        origin=str(r["origin"]),
        destination=str(r["destination"]),
        depart_start=r["depart_start"],
        depart_end=r["depart_end"],
        cabin=str(r["cabin"]),
        passengers=int(r["passengers"]),
        notes=r["notes"],
    )


app = FastAPI(title="husky-flight-search", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM searches ORDER BY id DESC LIMIT 50"
        ).fetchall()
    searches = [row_to_search(r) for r in rows]
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "providers": PROVIDERS,
            "searches": searches,
        },
    )


@app.post("/searches")
def create_search(
    origin: str = Form(...),
    destination: str = Form(...),
    depart_start: str | None = Form(None),
    depart_end: str | None = Form(None),
    cabin: str = Form("economy"),
    passengers: int = Form(1),
    notes: str | None = Form(None),
) -> RedirectResponse:
    origin = origin.strip().upper()
    destination = destination.strip().upper()

    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    with db() as conn:
        conn.execute(
            """
            INSERT INTO searches (created_at, origin, destination, depart_start, depart_end, cabin, passengers, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (created_at, origin, destination, depart_start, depart_end, cabin, passengers, notes),
        )
        conn.commit()

    return RedirectResponse(url="/", status_code=303)


@app.get("/searches/{search_id}", response_class=HTMLResponse)
def view_search(request: Request, search_id: int) -> HTMLResponse:
    with db() as conn:
        r = conn.execute("SELECT * FROM searches WHERE id = ?", (search_id,)).fetchone()
    if not r:
        return HTMLResponse("Not found", status_code=404)
    s = row_to_search(r)
    links = build_links(
        origin=s.origin,
        destination=s.destination,
        depart_start=s.depart_start,
        depart_end=s.depart_end,
        cabin=s.cabin,
        passengers=s.passengers,
    )
    return templates.TemplateResponse(
        request,
        "search.html",
        {"search": s, "links": links},
    )


@app.post("/searches/{search_id}/delete")
def delete_search(search_id: int) -> RedirectResponse:
    with db() as conn:
        conn.execute("DELETE FROM searches WHERE id = ?", (search_id,))
        conn.commit()
    return RedirectResponse(url="/", status_code=303)


# Simple JSON API
@app.get("/api/providers")
def api_providers() -> Any:
    return {"providers": PROVIDERS}


@app.get("/api/searches")
def api_list_searches(limit: int = 100) -> Any:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM searches ORDER BY id DESC LIMIT ?", (int(limit),)
        ).fetchall()
    return {"searches": [asdict(row_to_search(r)) for r in rows]}


@app.post("/api/searches")
def api_create_search(payload: dict[str, Any]) -> Any:
    origin = str(payload.get("origin", "")).strip().upper()
    destination = str(payload.get("destination", "")).strip().upper()
    depart_start = payload.get("depart_start")
    depart_end = payload.get("depart_end")
    cabin = str(payload.get("cabin", "economy"))
    passengers = int(payload.get("passengers", 1))
    notes = payload.get("notes")

    if not origin or not destination:
        return {"error": "origin and destination are required"}

    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    with db() as conn:
        cur = conn.execute(
            """
            INSERT INTO searches (created_at, origin, destination, depart_start, depart_end, cabin, passengers, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (created_at, origin, destination, depart_start, depart_end, cabin, passengers, notes),
        )
        conn.commit()
        search_id = int(cur.lastrowid)

        r = conn.execute("SELECT * FROM searches WHERE id = ?", (search_id,)).fetchone()

    s = row_to_search(r)
    return {"search": asdict(s), "links": build_links(**asdict(s))}
