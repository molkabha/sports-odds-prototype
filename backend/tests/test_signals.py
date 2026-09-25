import pytest
from app.signals import implied_probability, evaluate_signal, SIGNAL_LABEL


# --- implied_probability ---

def test_implied_probability_basic():
    assert implied_probability(2.0) == 0.5


def test_implied_probability_favourite():
    # odds of 1.50 → ~66.7% probability
    prob = implied_probability(1.50)
    assert abs(prob - 0.6667) < 0.001


def test_implied_probability_underdog():
    # odds of 3.00 → 33.3%
    assert implied_probability(3.0) == round(1 / 3.0, 4)


def test_implied_probability_invalid_zero():
    with pytest.raises(ValueError):
        implied_probability(0.0)


def test_implied_probability_invalid_one():
    with pytest.raises(ValueError):
        implied_probability(1.0)


def test_implied_probability_invalid_negative():
    with pytest.raises(ValueError):
        implied_probability(-2.5)


# --- evaluate_signal ---

def test_signal_triggered_when_higher_ranked_has_lower_probability():
    """
    Home team rank=5 (better), but odds=2.50 → probability 40%.
    Away team rank=20 (worse), but odds=1.80 → probability ~55.6%.
    Higher-ranked home team has lower probability → signal triggered.
    """
    result = evaluate_signal(
        home_rank=5,
        away_rank=20,
        home_probability=implied_probability(2.50),
        away_probability=implied_probability(1.80),
        home_name="Team A",
        away_name="Team B",
    )
    assert result["triggered"] is True
    assert result["label"] == SIGNAL_LABEL
    assert result["undervalued_team"] == "Team A"


def test_signal_not_triggered_when_higher_ranked_has_higher_probability():
    """
    Home team rank=3 (better) with odds=1.60 → probability ~62.5%.
    Away team rank=15 (worse) with odds=2.50 → probability 40%.
    Higher-ranked home team has higher probability → no signal.
    """
    result = evaluate_signal(
        home_rank=3,
        away_rank=15,
        home_probability=implied_probability(1.60),
        away_probability=implied_probability(2.50),
        home_name="Team A",
        away_name="Team B",
    )
    assert result["triggered"] is False
    assert result["label"] is None


def test_signal_away_team_is_higher_ranked_and_undervalued():
    """
    Away team has the better rank but lower implied probability → signal triggered
    and undervalued_team is the away team.
    """
    result = evaluate_signal(
        home_rank=18,
        away_rank=2,
        home_probability=implied_probability(1.70),
        away_probability=implied_probability(2.30),
        home_name="Home FC",
        away_name="Away Stars",
    )
    assert result["triggered"] is True
    assert result["undervalued_team"] == "Away Stars"


def test_signal_not_triggered_away_team_higher_ranked_but_favoured():
    """
    Away team rank=1 (best), home team rank=25 (worst).
    Away team odds=1.40 → 71.4% probability.
    Home team odds=2.80 → 35.7% probability.
    Away team is higher-ranked AND has higher probability → no signal.
    """
    result = evaluate_signal(
        home_rank=25,
        away_rank=1,
        home_probability=implied_probability(2.80),
        away_probability=implied_probability(1.40),
        home_name="Home FC",
        away_name="Away Stars",
    )
    assert result["triggered"] is False


def test_signal_missing_home_rank():
    result = evaluate_signal(
        home_rank=None,
        away_rank=5,
        home_probability=0.50,
        away_probability=0.60,
        home_name="Team A",
        away_name="Team B",
    )
    assert result["triggered"] is False
    assert "unavailable" in result["explanation"].lower()


def test_signal_missing_away_rank():
    result = evaluate_signal(
        home_rank=5,
        away_rank=None,
        home_probability=0.50,
        away_probability=0.60,
        home_name="Team A",
        away_name="Team B",
    )
    assert result["triggered"] is False
    assert "unavailable" in result["explanation"].lower()


def test_signal_both_ranks_missing():
    """
    When both ranks are None, signal must not be evaluated and no fabricated
    rank may be used.  The explanation must mention unavailability.
    """
    result = evaluate_signal(
        home_rank=None,
        away_rank=None,
        home_probability=0.50,
        away_probability=0.60,
        home_name="Team A",
        away_name="Team B",
    )
    assert result["triggered"] is False
    assert result["label"] is None
    assert result["undervalued_team"] is None
    assert "unavailable" in result["explanation"].lower()


def test_signal_equal_ranks():
    result = evaluate_signal(
        home_rank=10,
        away_rank=10,
        home_probability=0.50,
        away_probability=0.50,
        home_name="Team A",
        away_name="Team B",
    )
    assert result["triggered"] is False
    assert "equal" in result["explanation"].lower()
