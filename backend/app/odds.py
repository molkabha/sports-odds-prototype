"""
Mock odds module.

These are NOT real betting-market odds.
They are deterministic values generated for demonstration purposes only.

Decimal odds format (European):
  - odds = 2.00 → implied probability = 50%
  - odds > 2.00 → underdog (less than 50% implied win chance)
  - 1.01 < odds < 2.00 → favourite (more than 50% implied win chance)

The mock values are seeded on game_id so they remain consistent across restarts.
We deliberately construct the fixture odds so that some games trigger the
"Favorite Undervalued" signal and some do not, making the demo clearly legible.
"""

import hashlib

# Hardcoded odds for fixture games — keyed by game_id.
# Chosen so that some games trigger the signal (higher-ranked team has lower
# implied probability) and some don't.
FIXTURE_ODDS: dict[str, tuple[float, float]] = {
    # game_id → (home_decimal_odds, away_decimal_odds)
    #
    # BOS (rank 1) vs NYK (rank 7)
    # BOS has lower probability (2.60) than NYK (1.55) → SIGNAL ✓
    "401705123": (2.60, 1.55),
    #
    # OKC (rank 2) vs DEN (rank 5)
    # OKC has higher probability (1.70) than DEN (2.20) → no signal
    "401705124": (1.70, 2.20),
    #
    # CLE (rank 3) vs ATL (rank 14)
    # CLE has lower probability (2.40) than ATL (1.65) → SIGNAL ✓
    "401705125": (2.40, 1.65),
    #
    # PHX (rank 20) vs GSW (rank 4)
    # GSW (better ranked) has lower probability (2.10 away) than PHX (1.80) → SIGNAL ✓
    "401705126": (1.80, 2.10),
    #
    # MIN (rank 6) vs LAC (rank 11)
    # MIN has higher probability (1.65) than LAC (2.30) → no signal
    "401705127": (1.65, 2.30),
    #
    # SAC (rank 9) vs MEM (rank 22)
    # SAC has higher probability (1.75) than MEM (2.10) → no signal
    "401705128": (1.75, 2.10),
}


def get_odds(game_id: str, home_name: str, away_name: str) -> tuple[float, float]:
    """
    Return (home_decimal_odds, away_decimal_odds) for a game.

    For fixture games, uses the hardcoded FIXTURE_ODDS table.
    For live games (not in the table), generates deterministic odds from
    a hash of the team names so results stay consistent across runs.
    """
    if game_id in FIXTURE_ODDS:
        return FIXTURE_ODDS[game_id]

    return _generate_deterministic_odds(game_id, home_name, away_name)


def _generate_deterministic_odds(game_id: str, home_name: str, away_name: str) -> tuple[float, float]:
    """
    Generate plausible decimal odds from a hash of the inputs.
    Range: 1.40–2.80, rounded to 2 decimal places.
    The two odds values are intentionally asymmetric.
    """
    seed_home = int(hashlib.md5(f"{game_id}{home_name}home".encode()).hexdigest(), 16)
    seed_away = int(hashlib.md5(f"{game_id}{away_name}away".encode()).hexdigest(), 16)

    # Map hash to range [1.40, 2.80]
    home_odds = 1.40 + (seed_home % 140) / 100
    away_odds = 1.40 + (seed_away % 140) / 100

    return round(home_odds, 2), round(away_odds, 2)
