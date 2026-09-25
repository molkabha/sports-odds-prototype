from pydantic import BaseModel
from typing import Optional


class TeamInfo(BaseModel):
    name: str
    abbreviation: str
    rank: Optional[int]  # lower number = better rank; None if unavailable


class GameOdds(BaseModel):
    home_decimal: float
    away_decimal: float
    is_mocked: bool = True


class GameSignal(BaseModel):
    triggered: bool
    label: Optional[str]  # "Favorite Undervalued" or None
    # Which team is the "favorite" (higher-ranked) that is undervalued
    undervalued_team: Optional[str]
    explanation: Optional[str]


class Game(BaseModel):
    game_id: str
    status: str
    home_team: TeamInfo
    away_team: TeamInfo
    odds: Optional[GameOdds]
    home_probability: Optional[float]
    away_probability: Optional[float]
    signal: GameSignal


class GamesResponse(BaseModel):
    date: str
    league: str
    odds_source: str
    games: list[Game]
