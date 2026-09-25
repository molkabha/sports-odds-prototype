import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api_client import fetch_games, get_today
from app.odds import get_odds
from app.signals import implied_probability, evaluate_signal
from app.models import Game, GameOdds, GameSignal, GamesResponse, TeamInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sports Odds Research Tool", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/games", response_model=GamesResponse)
async def get_games():
    raw_games, is_live = await fetch_games()

    if not raw_games:
        return GamesResponse(
            date=get_today(),
            league="NBA",
            odds_source="MOCKED (demo data)",
            games=[],
        )

    games = []
    for g in raw_games:
        home = g["home"]
        away = g["away"]

        # Get mocked odds for this game
        home_odds_val, away_odds_val = get_odds(g["id"], home["name"], away["name"])

        # Calculate implied probabilities
        try:
            home_prob = implied_probability(home_odds_val)
            away_prob = implied_probability(away_odds_val)
        except ValueError as exc:
            logger.warning("Invalid odds for game %s: %s", g["id"], exc)
            home_prob = None
            away_prob = None

        # Evaluate signal
        if home_prob is not None and away_prob is not None:
            signal_data = evaluate_signal(
                home_rank=home.get("rank"),
                away_rank=away.get("rank"),
                home_probability=home_prob,
                away_probability=away_prob,
                home_name=home["name"],
                away_name=away["name"],
            )
        else:
            signal_data = {
                "triggered": False,
                "label": None,
                "undervalued_team": None,
                "explanation": "Invalid odds — could not evaluate signal",
            }

        games.append(
            Game(
                game_id=g["id"],
                status=g.get("status", "Scheduled"),
                home_team=TeamInfo(
                    name=home["name"],
                    abbreviation=home["abbreviation"],
                    rank=home.get("rank"),
                ),
                away_team=TeamInfo(
                    name=away["name"],
                    abbreviation=away["abbreviation"],
                    rank=away.get("rank"),
                ),
                odds=GameOdds(
                    home_decimal=home_odds_val,
                    away_decimal=away_odds_val,
                    is_mocked=True,
                ),
                home_probability=home_prob,
                away_probability=away_prob,
                signal=GameSignal(**signal_data),
            )
        )

    odds_note = "MOCKED (demo data)" if not is_live else "MOCKED (attached to live games)"
    data_note = "fixture" if not is_live else "live ESPN API"
    logger.info("Returning %d games from %s with %s odds", len(games), data_note, "mocked")

    return GamesResponse(
        date=get_today(),
        league="NBA",
        odds_source=odds_note,
        games=games,
    )
