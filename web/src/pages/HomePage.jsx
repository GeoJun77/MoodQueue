import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import Layout from '../components/Layout';
import TrackList from '../components/TrackList';
import { useAuth } from '../context/AuthContext';
import { analyzeMood, connectSpotify, getErrorMessage } from '../services/api';
import { getMood } from '../moods';

const suggestions = [
  "Je suis nostalgique ce soir 🌅",
  "Besoin d'énergie pour bosser ⚡",
  'Mélancolique et pensif 🌧️',
  'Je veux faire la fête 🎉',
  'Moment calme et zen 😌',
  "J'ai le mal du pays 🏠",
];

const spotifyMessages = {
  connected: '✅ Spotify connected! Your next playlists will be saved to your account.',
  cancelled: 'Spotify connection cancelled.',
  expired: 'The Spotify link expired, please try again.',
  error: "Couldn't connect Spotify. Your playlists still work with the built-in catalog.",
};

const MAX_LEN = 1000;

const greeting = () => {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 18) return 'Good afternoon';
  return 'Good evening';
};

export default function HomePage() {
  const { user, features, refreshUser } = useAuth();
  const [params, setParams] = useSearchParams();
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');

  // Coming back from the Spotify login page: /?spotify=connected
  useEffect(() => {
    const status = params.get('spotify');
    if (!status) return;
    setToast(spotifyMessages[status] || spotifyMessages.error);
    if (status === 'connected') refreshUser().catch(() => {});
    setParams({}, { replace: true });
    const t = setTimeout(() => setToast(''), 5000);
    return () => clearTimeout(t);
  }, [params, setParams, refreshUser]);

  const handleAnalyze = async () => {
    if (!text.trim() || loading) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await analyzeMood(text.trim());
      setResult(response.data);
    } catch (err) {
      setError(getErrorMessage(err, 'Could not analyze your mood. Try again.'));
    } finally {
      setLoading(false);
    }
  };

  const handleConnectSpotify = async () => {
    try {
      const response = await connectSpotify();
      window.location.href = response.data.auth_url;
    } catch (err) {
      setError(getErrorMessage(err, 'Could not connect to Spotify'));
    }
  };

  const mood = result ? getMood(result.mood) : null;

  return (
    <Layout>
      {toast && <div className="toast" role="status">{toast}</div>}

      <header className="page-header">
        <div>
          <p className="eyebrow">{greeting()}, {user?.username} 👋</p>
          <h1 className="page-title">How are you feeling?</h1>
        </div>
        {features.spotify && (
          user?.spotify_connected ? (
            <div className="pill"><span className="dot" /> Spotify connected</div>
          ) : (
            <button className="btn" onClick={handleConnectSpotify}>🎵 Connect Spotify</button>
          )
        )}
      </header>

      <section className="card">
        <h2 className="card-title">Describe your mood</h2>
        <p className="card-subtitle">Write in any language — French, English, Spanish, anything</p>
        <textarea
          className="textarea"
          placeholder="Je suis nostalgique ce soir... or I feel energetic and ready to go..."
          value={text}
          maxLength={MAX_LEN}
          onChange={(e) => setText(e.target.value)}
          rows={4}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleAnalyze();
          }}
        />
        {text.length > MAX_LEN * 0.8 && <p className="char-count">{text.length}/{MAX_LEN}</p>}
        <div className="chips">
          {suggestions.map((s) => (
            <button key={s} className="chip" onClick={() => setText(s)}>{s}</button>
          ))}
        </div>
        {error && <p className="error-box">{error}</p>}
        <button className="btn btn-block" onClick={handleAnalyze} disabled={loading || !text.trim()}>
          {loading ? (<><span className="spinner" /> Analyzing your mood…</>) : '✨ Generate my playlist'}
        </button>
        <p className="hint">Tip: Ctrl/⌘ + Enter to generate</p>
      </section>

      {result && mood && (
        <section className="card result">
          <div className="mood-header" style={{ background: `${mood.color}14` }}>
            <span className="mood-emoji">{mood.emoji}</span>
            <div style={{ flex: 1 }}>
              <p className="label-small">Detected mood</p>
              <h2 className="mood-value" style={{ color: mood.color }}>{mood.label}</h2>
            </div>
            <div className="ring" style={{ borderColor: mood.color, color: mood.color }}>
              {Math.round(result.confidence * 100)}%
            </div>
          </div>

          {result.explanation && (
            <div className="explanation">
              <span>💡</span>
              <p>{result.explanation}</p>
            </div>
          )}

          <div className="playlist-head">
            <div className="playlist-icon">🎵</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p className="label-small">Your playlist · {result.tracks.length} tracks</p>
              <p className="playlist-name">{result.playlist_name}</p>
            </div>
            {result.playlist_url ? (
              <a className="btn" href={result.playlist_url} target="_blank" rel="noreferrer">▶ Open in Spotify</a>
            ) : (
              <span className="badge" title="Built from MoodQueue's built-in catalog">MoodQueue catalog</span>
            )}
          </div>

          <TrackList tracks={result.tracks} />

          {result.analysis_source === 'local' && (
            <p className="hint" style={{ padding: '0 24px 16px' }}>
              Analyzed with MoodQueue's offline engine.
            </p>
          )}
        </section>
      )}
    </Layout>
  );
}
