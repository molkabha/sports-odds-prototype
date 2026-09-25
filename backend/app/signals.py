"""
Signal logic for the Sports Odds Research Tool.

Implements exactly one signal: "Favorite Undervalued"

Definition:
  The higher-ranked team (lower rank number = better) has a lower implied win
  probability than its lower-ranked opponent, suggesting the market undervalues
  the stronger team.

Implied probability formula:
  probability = 1 / decimal_odds

Example:
  Team A rank=5, odds=2.50 → probability = 0.40 (40%)
  Team B rank=20, odds=1.80 → probability = 0.556 (55.6%)
  Team A is higher-ranked but has a lower probability → signal triggered
"""

from typing import Optional


SIGNAL_LABEL = "Favorite Undervalued"
MIN_VALID_ODDS = 1.01  # odds ≤ 1.0 are mathematically impossible


def implied_probability(decimal_odds: float) -> float:
    """
    Convert decimal odds to implied win probability.
    Raises ValueError for invalid odds (≤ 1.0).
    """
    if decimal_odds <= 1.0:
        raise ValueError(f"Odds must be > 1.0, got {decimal_odds}")
    return round(1 / decimal_odds, 4)


def evaluate_signal(
    home_rank: Optional[int],
    away_rank: Optional[int],
    home_probability: float,
    away_probability: float,
    home_name: str,
    away_name: str,
) -> dict:
    """
    Evaluate the Favorite Undervalued signal for a single game.

    Returns a dict with:
      - triggered (bool)
      - label (str or None)
      - undervalued_team (str or None)
      - explanation (str or None)

    If either rank is missing, the signal cannot be evaluated → triggered=False.
    """
    if home_rank is None or away_rank is None:
        return _no_signal("Ranking data unavailable for one or both teams")

    # Lower rank number = better team (rank 1 is the best)
    if home_rank < away_rank:
        # Home team is higher ranked
        higher_ranked_name = home_name
        higher_ranked_prob = home_probability
        lower_ranked_prob = away_probability
    elif away_rank < home_rank:
        # Away team is higher ranked
        higher_ranked_name = away_name
        higher_ranked_prob = away_probability
        lower_ranked_prob = home_probability
    else:
        # Equal rank — signal is undefined
        return _no_signal("Teams have equal rankings")

    if higher_ranked_prob < lower_ranked_prob:
        explanation = (
            f"{higher_ranked_name} is the higher-ranked team but has a lower "
            f"implied win probability ({higher_ranked_prob:.1%}) than their opponent "
            f"({lower_ranked_prob:.1%}), suggesting the market undervalues them."
        )
        return {
            "triggered": True,
            "label": SIGNAL_LABEL,
            "undervalued_team": higher_ranked_name,
            "explanation": explanation,
        }

    return _no_signal()


def _no_signal(reason: Optional[str] = None) -> dict:
    return {
        "triggered": False,
        "label": None,
        "undervalued_team": None,
        "explanation": reason,
    }
