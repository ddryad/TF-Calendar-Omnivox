# TF-Calendar — Omnivox Service

A small FastAPI microservice that logs into a student's [Omnivox](https://www.omnivox.ca/) portal and scrapes their class schedule into a clean, structured format.

It exists as a separate service — rather than living inside the main API — because it depends on Python's HTML-scraping ecosystem (`requests` + `BeautifulSoup`) and needs to simulate a real login/session flow against Omnivox, which is a very different job from the rest of the platform.

This is one of three repositories that make up the full **TF-Calendar** project:

| Repo | Role |
|---|---|
| [TF-Calendar](https://github.com/ddryad/TF-Calendar) | NestJS REST API — auth, users, calendars, scheduling logic |
| **TF-Calendar-Omnivox** *(this repo)* | Scrapes a student's Omnivox schedule |
| [TF-Calendar-Frontend](https://github.com/Haroune07/TF-Calendar-Frontend) | React SPA |

## How it works

1. The [TF-Calendar API](https://github.com/ddryad/TF-Calendar) sends a student's Omnivox credentials (student ID + password) to `POST /classes`.
2. This service opens a `requests.Session`, submits the Omnivox login form, and follows the resulting redirect chain to establish an authenticated session — exactly like a browser would.
3. It fetches the student's Omnivox home page and parses out every calendar entry tagged as a course (`data-nom-categorie` containing `COURS`) from the embedded modal data.
4. Each raw entry (French date strings, time ranges, room, category) is normalized into a typed `ClassItem`: a name, description, ISO start datetime, and duration in hours.
5. The API consumes this list and imports it as calendar activities for the user.

## Tech stack

- [FastAPI](https://fastapi.dev/) + [Pydantic](https://docs.pydantic.dev/) for the HTTP layer and data validation
- [Requests](https://requests.readthedocs.io/) for the login/session handling
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [Uvicorn](https://www.uvicorn.org/) as the ASGI server

## Getting started

### Prerequisites
- Python 3.11+

### Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The service listens on `http://localhost:8000`.

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/classes` | Takes `{ "da": "<student id>", "password": "<omnivox password>" }`, returns a list of `ClassItem` |

Example:

```bash
curl -X POST http://localhost:8000/classes \
  -H "Content-Type: application/json" \
  -d '{"da": "1234567", "password": "your-omnivox-password"}'
```

Returns `401` if the credentials are rejected by Omnivox, and `502`/`500` if Omnivox is unreachable or the page structure has changed.

## Notes

- The Omnivox base URL is currently hardcoded to one college's instance (`collegemv.omnivox.ca`) in `scraper.py`. To support other institutions, this should be extracted into an environment variable.
- Because this scrapes a real third-party site rather than using an official API, it's inherently fragile — if Omnivox changes its login form or markup, `login()` / `get_classes()` will need updating.
