import { useState, useEffect } from 'react'
import './App.css'

function formatPct(prob) {
  if (prob == null) return '—'
  return (prob * 100).toFixed(1) + '%'
}

function RankBadge({ rank }) {
  if (rank == null) return <span className="rank-badge rank-unknown">N/A</span>
  return <span className="rank-badge">#{rank}</span>
}

function SignalBadge({ signal }) {
  if (!signal.triggered) return null
  return (
    <div className="signal-badge">
      <span className="signal-icon">⚠</span>
      <span>{signal.label}</span>
    </div>
  )
}

function GameCard({ game }) {
  const { home_team, away_team, odds, home_probability, away_probability, signal, status } = game
  const flagged = signal.triggered

  return (
    <div className={`game-card ${flagged ? 'game-card--flagged' : ''}`}>
      {flagged && <SignalBadge signal={signal} />}

      <div className="game-status">{status}</div>

      <div className="matchup">
        <div className="team">
          <RankBadge rank={home_team.rank} />
          <span className="team-name">{home_team.name}</span>
          <span className="team-abbr">{home_team.abbreviation}</span>
        </div>

        <div className="vs-divider">vs</div>

        <div className="team team--away">
          <RankBadge rank={away_team.rank} />
          <span className="team-name">{away_team.name}</span>
          <span className="team-abbr">{away_team.abbreviation}</span>
        </div>
      </div>

      <div className="odds-row">
        <div className="odds-cell">
          <div className="odds-label">Odds (mock)</div>
          <div className="odds-values">
            <span>{odds?.home_decimal?.toFixed(2) ?? '—'}</span>
            <span className="odds-sep">/</span>
            <span>{odds?.away_decimal?.toFixed(2) ?? '—'}</span>
          </div>
        </div>

        <div className="odds-cell">
          <div className="odds-label">Implied probability</div>
          <div className="odds-values">
            <span className={flagged && signal.undervalued_team === home_team.name ? 'prob--undervalued' : ''}>
              {formatPct(home_probability)}
            </span>
            <span className="odds-sep">/</span>
            <span className={flagged && signal.undervalued_team === away_team.name ? 'prob--undervalued' : ''}>
              {formatPct(away_probability)}
            </span>
          </div>
        </div>
      </div>

      {flagged && signal.explanation && (
        <div className="signal-explanation">{signal.explanation}</div>
      )}
    </div>
  )
}

export default function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/games')
      .then(r => {
        if (!r.ok) throw new Error(`Server returned ${r.status}`)
        return r.json()
      })
      .then(d => {
        setData(d)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const flaggedCount = data?.games?.filter(g => g.signal.triggered).length ?? 0

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="header-title">
            <h1>Sports Odds Research Tool</h1>
            <p className="header-subtitle">NBA · Favorite Undervalued Signal</p>
          </div>
          {data && (
            <div className="header-meta">
              <div className="meta-item">
                <span className="meta-label">Date</span>
                <span className="meta-value">{data.date}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">League</span>
                <span className="meta-value">{data.league}</span>
              </div>
              <div className="meta-item mock-badge">
                <span>Odds: {data.odds_source}</span>
              </div>
            </div>
          )}
        </div>
      </header>

      <main className="main">
        {loading && (
          <div className="state-message">
            <div className="spinner" />
            <p>Loading today's games…</p>
          </div>
        )}

        {error && (
          <div className="state-message state-message--error">
            <p>⚠ Could not load games: {error}</p>
            <p className="state-hint">Make sure the backend is running on port 8000.</p>
          </div>
        )}

        {data && data.games.length === 0 && (
          <div className="state-message">
            <p>No games scheduled today.</p>
          </div>
        )}

        {data && data.games.length > 0 && (
          <>
            <div className="summary-bar">
              <span>{data.games.length} game{data.games.length !== 1 ? 's' : ''} today</span>
              {flaggedCount > 0 && (
                <span className="summary-signal">
                  ⚠ {flaggedCount} Favorite Undervalued signal{flaggedCount !== 1 ? 's' : ''}
                </span>
              )}
            </div>

            <div className="signal-legend">
              <div className="legend-item legend-item--signal">
                <span>⚠</span> Game highlighted in orange = Favorite Undervalued signal detected
              </div>
              <div className="legend-item">
                Probability highlighted in red = the undervalued (higher-ranked) team
              </div>
            </div>

            <div className="games-grid">
              {data.games.map(game => (
                <GameCard key={game.game_id} game={game} />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
