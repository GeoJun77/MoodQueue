import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import TrackList from '../components/TrackList';
import { deleteMoodEntry, getErrorMessage, getMoodHistory } from '../services/api';
import { getMood } from '../moods';

const formatDate = (iso) => {
  // The API stores UTC without a timezone suffix
  const d = new Date(/[zZ]|[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`);
  return d.toLocaleString(undefined, { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};

export default function HistoryPage() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [open, setOpen] = useState(null);

  useEffect(() => {
    getMoodHistory()
      .then((r) => setEntries(r.data))
      .catch((err) => setError(getErrorMessage(err, 'Could not load your history')))
      .finally(() => setLoading(false));
  }, []);

  const topMood = useMemo(() => {
    const counts = {};
    entries.forEach((e) => { counts[e.detected_mood] = (counts[e.detected_mood] || 0) + 1; });
    return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0];
  }, [entries]);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this mood and its playlist?')) return;
    try {
      await deleteMoodEntry(id);
      setEntries((list) => list.filter((e) => e.id !== id));
    } catch (err) {
      setError(getErrorMessage(err, 'Could not delete this entry'));
    }
  };

  return (
    <Layout>
      <header className="page-header">
        <div>
          <p className="eyebrow">Your journey</p>
          <h1 className="page-title">Mood History</h1>
        </div>
      </header>

      {error && <p className="error-box">{error}</p>}

      {!loading && entries.length > 0 && (
        <div className="stats">
          <div className="stat">
            <span className="stat-num">{entries.length}</span>
            <span className="stat-label">Moods</span>
          </div>
          <div className="stat">
            <span className="stat-num">{entries.filter((e) => e.playlist).length}</span>
            <span className="stat-label">Playlists</span>
          </div>
          <div className="stat">
            <span className="stat-num">{topMood ? getMood(topMood).emoji : '—'}</span>
            <span className="stat-label">Top mood</span>
          </div>
        </div>
      )}

      {loading && <p className="muted">Loading your history…</p>}

      {!loading && !error && entries.length === 0 && (
        <div className="card empty">
          <div className="empty-emoji">🎵</div>
          <h2>No moods yet</h2>
          <p>Describe how you feel to get your first playlist.</p>
          <Link className="btn" to="/">Go to home →</Link>
        </div>
      )}

      {entries.map((e) => {
        const mood = getMood(e.detected_mood);
        const p = e.playlist;
        const isOpen = open === e.id;
        return (
          <article className="card entry" key={e.id}>
            <div className="entry-top">
              <span className="entry-emoji">{mood.emoji}</span>
              <div className="entry-body">
                <div className="entry-row">
                  <span className="entry-mood" style={{ color: mood.color }}>{mood.label}</span>
                  <span className="badge">{Math.round((e.confidence_score || 0) * 100)}%</span>
                  <span className="entry-date">{formatDate(e.created_at)}</span>
                </div>
                <p className="entry-text">“{e.raw_text}”</p>
              </div>
            </div>
            <div className="entry-actions">
              {p?.tracks?.length > 0 && (
                <button className="btn btn-ghost" onClick={() => setOpen(isOpen ? null : e.id)}>
                  {isOpen ? '▲ Hide' : '▼ Show'} {p.name} ({p.track_count})
                </button>
              )}
              {p?.spotify_playlist_url && (
                <a className="btn" href={p.spotify_playlist_url} target="_blank" rel="noreferrer">▶ Spotify</a>
              )}
              <button className="btn btn-danger" onClick={() => handleDelete(e.id)}>Delete</button>
            </div>
            {isOpen && <TrackList tracks={p.tracks} />}
          </article>
        );
      })}
    </Layout>
  );
}
