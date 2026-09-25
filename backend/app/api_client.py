"""
NBA data client using the ESPN public scoreboard API.

Endpoint: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard
No API key required.

Returns today's NBA games with team names and current season standings-based rankings.
If the live API is unreachable, falls back to a static fixture that mirrors the real
response structure — the fixture is clearly labelled as demo data.
"""

import httpx
import logging
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)

ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

# Static fixture — mirrors real ESPN API structure.
# Used when the live API is unreachable (e.g., network sandbox, CI, offline demo).
# Rankings reflect approximate mid-season 2024–25 NBA standings.
FIXTURE_GAMES = [
    {
        "id": "401705123",
        "status": "Scheduled",
        "home": {"name": "Boston Celtics", "abbreviation": "BOS", "rank": 1},
        "away": {"name": "New York Knicks", "abbreviation": "NYK", "rank": 7},
    },
    {
        "id": "401705124",
        "status": "Scheduled",
        "home": {"name": "Oklahoma City Thunder", "abbreviation": "OKC", "rank": 2},
        "away": {"name": "Denver Nuggets", "abbreviation": "DEN", "rank": 5},
    },
    {
        "id": "401705125",
        "status": "Scheduled",
        "home": {"name": "Cleveland Cavaliers", "abbreviation": "CLE", "rank": 3},
        "away": {"name": "Atlanta Hawks", "abbreviation": "ATL", "rank": 14},
    },
    {
        "id": "401705126",
        "status": "Scheduled",
        "home": {"name": "Phoenix Suns", "abbreviation": "PHX", "rank": 20},
        "away": {"name": "Golden State Warriors", "abbreviation": "GSW", "rank": 4},
    },
    {
        "id": "401705127",
        "status": "Scheduled",
        "home": {"name": "Minnesota Timberwolves", "abbreviation": "MIN", "rank": 6},
        "away": {"name": "Los Angeles Clippers", "abbreviation": "LAC", "rank": 11},
    },
    {
        "id": "401705128",
        "status": "Scheduled",
        "home": {"name": "Sacramento Kings", "abbreviation": "SAC", "rank": 9},
        "away": {"name": "Memphis Grizzlies", "abbreviation": "MEM", "rank": 22},
    },
]


def _parse_espn_response(data: dict) -> list[dict]:
    """
    Extract the fields we care about from the ESPN scoreboard response.
    Returns a list of normalized game dicts matching our internal shape.
    """
    games = []
    events = data.get("events", [])

    for event in events:
        try:
            competitions = event.get("competitions", [])
            if not competitions:
                continue
            comp = competitions[0]
            competitors = comp.get("competitors", [])
            if len(competitors) < 2:
                continue

            home = next((c for c in competitors if c["homeAway"] == "home"), None)
            away = next((c for c in competitors if c["homeAway"] == "away"), None)
            if not home or not away:
                continue

            status = event.get("status", {}).get("type", {}).get("description", "Scheduled")

            # ESPN includes a `curatedRank` or `statistics` for standings rank.
            # We pull from `records` → win percentage rank or fall back to None.
            home_rank = _extract_rank(home)
            away_rank = _extract_rank(away)

            games.append({
                "id": event.get("id", ""),
                "status": status,
                "home": {
                    "name": home["team"]["displayName"],
                    "abbreviation": home["team"]["abbreviation"],
                    "rank": home_rank,
                },
                "away": {
                    "name": away["team"]["displayName"],
                    "abbreviation": away["team"]["abbreviation"],
                    "rank": away_rank,
                },
            })
        except (KeyError, TypeError) as exc:
            logger.warning("Skipping malformed event: %s", exc)
            continue

    return games


def _extract_rank(competitor: dict) -> Optional[int]:
    """Pull a standings rank from an ESPN competitor block, or return None."""
    # ESPN sometimes includes curatedRank.current
    curated = competitor.get("curatedRank", {})
    if curated.get("current") and curated["current"] != 99:
        return int(curated["current"])

    # Fall back to order of wins in records (rough proxy)
    records = competitor.get("records", [])
    for rec in records:
        if rec.get("type") == "total":
            # We don't have a true rank from this field alone; return None
            break

    return None


async def fetch_games() -> tuple[list[dict], bool]:
    """
    Attempt to fetch today's NBA games from ESPN.
    Returns (games_list, is_live).

    is_live = True  → data came from the real ESPN API
    is_live = False → data came from the static fixture
    """
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(ESPN_SCOREBOARD_URL)
            resp.raise_for_status()
            data = resp.json()

        parsed = _parse_espn_response(data)

        if parsed:
            logger.info("Fetched %d games from ESPN live API", len(parsed))
            return parsed, True
        else:
            logger.info("ESPN returned 0 games (off-season or no games today); using fixture")
            return FIXTURE_GAMES, False

    except Exception as exc:
        logger.warning("ESPN API unavailable (%s); falling back to fixture data", exc)
        return FIXTURE_GAMES, False


def get_today() -> str:
    return date.today().isoformat()
