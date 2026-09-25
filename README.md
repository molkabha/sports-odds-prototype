# Sports Odds Research Tool

A prototype built for a technical assessment. It retrieves NBA games from a real
sports data API, attaches deterministic mock odds, and flags games where the
higher-ranked team has a lower implied win probability than their opponent —
the **Favorite Undervalued** signal.

---

## Features

- Fetches today's NBA games from the ESPN public scoreboard API (no API key required)
- Falls back to a static fixture when the live API is unreachable (off-season, network issues)
- Deterministic mock odds attached to each game (clearly labelled throughout)
- Implied probability calculated from decimal odds: `p = 1 / decimal_odds`
- **Favorite Undervalued** signal: triggered when the higher-ranked team's implied
  probability is lower than the lower-ranked opponent's
- Simple React UI with loading, error, and empty states
- Flagged games visually highlighted in the UI
- 14 focused pytest tests covering the core signal logic

---

## Architecture

```
ESPN Scoreboard API  (or static fixture if unreachable)
        ↓
   api_client.py     normalises raw response into internal dicts
        ↓
     odds.py         provides deterministic mock decimal odds per game
        ↓
   signals.py        calculates implied probabilities, evaluates signal
        ↓
    main.py          FastAPI — exposes GET /api/games
        ↓
   React frontend    fetches /api/games, renders table, highlights flags
```

---

## Data Sources

**Sports API:** ESPN public scoreboard  
`https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard`

- No API key required
- Returns today's NBA games with team names and league-standings rank
- If the API returns 0 games (off-season) or is unreachable, the app falls back
  to a static fixture of 6 representative NBA matchups. The fixture mirrors the
  exact structure of a real ESPN response.

**League:** NBA

**Odds:** All odds are **MOCKED** — they are not live betting-market data.  
Fixture game odds are hardcoded to guarantee at least 3 signalled games and
3 non-signalled games for a clear demo. For games arriving from the live API,
odds are generated deterministically from a hash of the team names so results
are consistent across restarts.

---

## Signal Logic

**Favorite Undervalued** — triggered when the market appears to undervalue the
stronger team.

1. Identify the higher-ranked team (lower rank number = better; rank 1 is first place)
2. Calculate each team's implied win probability from their decimal odds:
   ```
   probability = 1 / decimal_odds
   ```
   Example: odds of 2.50 → probability = 1 / 2.50 = **0.40 (40%)**
3. If the higher-ranked team's implied probability is **lower** than the
   lower-ranked team's, the signal fires.

Example from the fixture data:

| Team | Rank | Odds | Implied prob |
|------|------|------|-------------|
| Boston Celtics | #1 | 2.60 | **38.5%** |
| New York Knicks | #7 | 1.55 | 64.5% |

Boston is ranked higher but the market gives them only a 38.5% chance →
**Favorite Undervalued** triggered.

> **Assumption:** implied probability is calculated as the raw reciprocal of
> decimal odds with no vig/margin removal. The assessment only requires a basic
> probability comparison, so the overround is left in.

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt

# Copy env example (no keys required for this prototype)
cp .env.example .env

# Start the API server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### Run the tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## API Endpoints

### `GET /api/health`

Simple health check.

```json
{ "status": "ok" }
```

### `GET /api/games`

Returns today's NBA games with rankings, mock odds, implied probabilities,
and signal evaluation.

```json
{
  "date": "2025-01-15",
  "league": "NBA",
  "odds_source": "MOCKED (demo data)",
  "games": [
    {
      "game_id": "401705123",
      "status": "Scheduled",
      "home_team": { "name": "Boston Celtics", "abbreviation": "BOS", "rank": 1 },
      "away_team": { "name": "New York Knicks", "abbreviation": "NYK", "rank": 7 },
      "odds": { "home_decimal": 2.60, "away_decimal": 1.55, "is_mocked": true },
      "home_probability": 0.3846,
      "away_probability": 0.6452,
      "signal": {
        "triggered": true,
        "label": "Favorite Undervalued",
        "undervalued_team": "Boston Celtics",
        "explanation": "..."
      }
    }
  ]
}
```

---

## Assumptions and Tradeoffs

- **Mocked odds** — no free real-time odds provider was integrated. The mock
  values are deterministic and clearly labelled everywhere in the UI and API
  response.
- **One league (NBA)** — the assessment asks for a single league. Adding more
  would require only a second API client and a league selector; the architecture
  supports it.
- **No vig removal** — implied probabilities use the raw reciprocal. The two
  probabilities in a game do not sum to 100%; that is expected and not a bug.
- **No database** — game data is fetched fresh on each request. Caching and
  persistence are out of scope for a 4–6 hour prototype.
- **No authentication** — the prototype is a local demo tool with no user
  accounts or sensitive data.
- **Missing rank data** — if the live ESPN API returns games without rank data
  (possible depending on the season), ranks are left as `null`/`None`. The
  signal is not evaluated for those games; the explanation field returns
  `"Ranking data unavailable for one or both teams"`. No fabricated or
  sequential ranks are ever used.

---

## Future Work

If this became a real 2-week sprint, the next priorities would be:

1. **Real odds provider** — integrate a licensed odds API (e.g., The Odds API)
   to replace the mock values with live market data.
2. **Additional leagues** — the current structure makes it straightforward to
   add NFL, MLB, or Premier League with a new `api_client` implementation.
3. **Data persistence** — store historical games and odds in a database (Postgres
   or SQLite to start) so signals can be tracked over time and backtested.
4. **Richer team context** — pull in coach data, recent form, injury reports to
   give the signal more explanatory depth.
5. **Improved reliability** — add response caching (Redis or simple in-memory)
   to avoid hammering the sports API and to handle outages gracefully.
6. **More signals** — the architecture isolates signal logic in `signals.py`,
   making it easy to add new signals (e.g., home-underdog, line movement) without
   touching the rest of the stack.
7. **Deployment** — containerise with Docker and deploy to a simple VPS or
   managed platform (Fly.io, Railway) with a CI pipeline.
8. **Monitoring** — add structured logging and basic alerting for API failures
   and signal anomalies.
