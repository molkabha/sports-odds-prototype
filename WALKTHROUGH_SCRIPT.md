# Walkthrough Script — Sports Odds Research Tool
# 5–7 minute screen recording

---

## 0:00–0:45 — Introduction

"Hi Emmanuel. I'll give you a quick walkthrough of the prototype I built for
the assessment.

The core idea is simple: pull today's NBA games from a real sports data API,
attach odds to those games, and flag any game where the higher-ranked team has
a lower implied win probability than their opponent. That's the Favorite
Undervalued signal.

I kept the scope intentionally small — one league, one signal, mocked odds —
because that's exactly what the assessment asks for and it's the right call
for a 4–6 hour timebox. Let me show you what it looks like running."

---

## 0:45–2:00 — Live demo

[Switch to browser, show the running app at localhost:5173]

"Here's the app. At the top you can see today's date, the league — NBA — and
this blue badge in the header that says 'Odds: MOCKED (demo data)'. That's
there on purpose. The odds are not real betting-market data and I didn't want
there to be any ambiguity about that.

Below that, there's a summary line — six games today — and it tells me how
many Favorite Undervalued signals were detected. In this case, three.

[Point to a flagged game card]

The flagged games are highlighted in orange, with a badge in the top-right
corner that says 'Favorite Undervalued'. Let me point out what the numbers
mean here.

Take this first game — Boston Celtics ranked #1 hosting the New York Knicks
ranked #7. The mock odds on Boston are 2.60 and on the Knicks 1.55. The
implied probabilities work out to 38.5% for Boston and 64.5% for the Knicks.

So the market is saying the Celtics only have a 38.5% chance of winning,
even though they're the better-ranked team. That's the signal — the
higher-ranked team looks undervalued by the odds. The probability in red
is Boston's, the undervalued team.

[Scroll to a non-flagged game]

And here's a non-flagged game — Oklahoma City Thunder versus Denver. OKC is
ranked #2, Denver #5. OKC's implied probability is 58.8%, which is higher
than Denver's 45.5%, so the market is already pricing in OKC as the
favourite. No signal there — everything is consistent with the rankings."

---

## 2:00–3:30 — Architecture

[Switch to code editor or terminal, show folder structure]

"The project is split into a FastAPI backend and a React frontend. The
backend has four modules.

`api_client.py` handles the ESPN scoreboard API — that's the data source.
It normalises the raw response into a simple internal dict with the fields
we care about: game ID, team names, abbreviations, and rank. If the ESPN
API is unreachable — which it is in a network sandbox — it logs a warning
and falls back to a static fixture that mirrors the exact same structure.

`odds.py` is the mock odds module. For the fixture games it uses hardcoded
decimal odds that I chose specifically to produce a mix of signalled and
non-signalled games. For live games that come from the real API, it
generates odds deterministically from a hash of the team names, so the
values are stable across restarts.

`signals.py` is where the business logic lives. It has two functions —
`implied_probability`, which is just `1 / decimal_odds`, and
`evaluate_signal`, which compares the two probabilities and returns a
result dict. This is the most important module and it's the one with tests.

`main.py` is a small FastAPI app — two endpoints, `GET /api/health` and
`GET /api/games`. The games endpoint calls the client, attaches odds, runs
the signal, and returns a Pydantic-validated response.

The React frontend is one component file plus CSS. It fetches `/api/games`
on mount, handles the three states — loading, error, empty — and renders
each game as a card. Flagged games get the orange border and badge."

---

## 3:30–4:45 — Technical decisions

"A few decisions worth explaining.

**Why ESPN?** It's a public endpoint, no API key, and it returns structured
game and team data including standings rank. The main limitation is that it
blocks requests from some network environments, which is why the fixture
fallback exists. In a real project I'd use a contracted sports data provider,
but for a prototype this is a reasonable starting point.

**Why mocked odds?** There are free odds APIs but they either require account
registration or have rate limits that make them awkward for a demo. The
assessment explicitly says mocked odds are fine if clearly labelled — so I
kept it simple and made sure the label is unavoidable in both the UI and the
API response.

**Why no database?** The assessment is a read-only research tool that fetches
today's games. Adding Postgres would mean managing a migration, a schema, a
connection pool — none of which adds anything to what's being demonstrated
here. If we need to track signals over time, that's a natural next step.

**How the signal handles edge cases** — if a team's rank is missing, the
signal returns `triggered: false` with an explanation. Invalid odds raise
a ValueError that's caught in the main endpoint. The frontend handles an
API failure with a clear error message instead of crashing."

---

## 4:45–5:45 — Tradeoffs

"The main tradeoffs are scope-driven.

I'm limited to one league. The architecture supports more — you'd add a new
api_client, a league parameter on the endpoint — but adding it in this
timebox would just be padding.

The odds are mocked. In a real sprint I'd wire up a proper odds provider.
The signal logic is written against decimal odds so swapping in real data
is straightforward.

The implied probability calculation ignores the bookmaker's overround — the
two probabilities in a game don't sum to 100%. That's a known simplification
and it doesn't affect the signal comparison, it just means the numbers are
slightly inflated. I called this out in the README.

And the fixture fallback means the demo always works regardless of whether
the live API is reachable. The tradeoff is that you're seeing the same six
games every time when running locally without ESPN access. That's a fair
tradeoff for a prototype."

---

## 5:45–6:30 — Next steps

"If this became a real 2-week sprint, I'd tackle a few things.

First, integrate a licensed odds provider to replace the mock values. The
Odds API has a reasonable free tier to start with.

Second, add data persistence — store historical games and signals in a
database so you can track how often the signal has been right and start
building a backtest.

Third, expand the team context. Right now we only have rank. Adding recent
form, home/away splits, and injury data would make the signal more
meaningful.

Fourth, deploy it. Containerise with Docker, set up a simple CI pipeline,
and put it on something like Railway or Fly.io so it's not localhost-only.

And longer term, add more signals. The architecture already isolates the
signal logic in its own module, so dropping in a new signal is a small
addition without touching the rest of the stack.

That's the prototype. The README has full setup instructions and all the
tradeoffs are documented there. Thanks for taking a look."

---

## Recording notes

- Resolution: 1080p or higher
- Show the terminal with `uvicorn` running and `pytest` output before
  switching to the browser
- Keep the browser font size at default so the card layout is visible
- No face required — screen + voice is fine
- Keep the tone conversational; don't read verbatim from this script
