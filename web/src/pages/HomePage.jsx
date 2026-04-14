import { useState } from 'react';
import { analyzeMood, connectSpotify } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function HomePage() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const moodConfig = {
    happy:      { emoji: '😊', color: '#f59e0b', bg: '#fef3c720' },
    sad:        { emoji: '😢', color: '#3b82f6', bg: '#dbeafe20' },
    angry:      { emoji: '😠', color: '#ef4444', bg: '#fee2e220' },
    calm:       { emoji: '😌', color: '#10b981', bg: '#d1fae520' },
    energetic:  { emoji: '⚡', color: '#f97316', bg: '#ffedd520' },
    nostalgic:  { emoji: '🌅', color: '#8b5cf6', bg: '#ede9fe20' },
    romantic:   { emoji: '❤️', color: '#ec4899', bg: '#fce7f320' },
    focused:    { emoji: '🎯', color: '#06b6d4', bg: '#cffafe20' },
    anxious:    { emoji: '😰', color: '#64748b', bg: '#f1f5f920' },
    relieved:   { emoji: '😮‍💨', color: '#1DB954', bg: '#dcfce720' },
    melancholic:{ emoji: '🌧️', color: '#6366f1', bg: '#e0e7ff20' },
    spiritual:  { emoji: '🙏', color: '#d97706', bg: '#fef3c720' },
    party:      { emoji: '🎉', color: '#f43f5e', bg: '#ffe4e620' },
    motivated:  { emoji: '💪', color: '#dc2626', bg: '#fee2e220' },
    lonely:     { emoji: '🌑', color: '#475569', bg: '#f8fafc20' },
    hopeful:    { emoji: '🌟', color: '#eab308', bg: '#fefce820' },
  };

  const suggestions = [
    "Je suis nostalgique ce soir 🌅",
    "Besoin d'énergie pour bosser ⚡",
    "Mélancolique et pensif 🌧️",
    "Je veux faire la fête 🎉",
    "Moment calme et zen 😌",
    "J'ai le mal du pays 🏠",
  ];

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const response = await analyzeMood(text);
      setResult(response.data);
    } catch (error) {
      alert('Could not analyze your mood. Try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectSpotify = async () => {
    try {
      const response = await connectSpotify();
      window.open(response.data.auth_url, '_blank');
    } catch (error) {
      alert('Could not connect to Spotify');
    }
  };

  const mood = result
    ? (moodConfig[result.mood] || { emoji: '🎵', color: '#1DB954', bg: '#dcfce720' })
    : null;

  const getTimeOfDay = () => {
    const h = new Date().getHours();
    if (h < 12) return 'morning';
    if (h < 17) return 'afternoon';
    return 'evening';
  };

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <div style={styles.sidebarLogo}>
          <div style={styles.logoIcon}>🎵</div>
          <span style={styles.logoText}>MoodQueue</span>
        </div>
        <nav style={styles.nav}>
          <div style={styles.navItem}>
            <span>🏠</span> Home
          </div>
          <div
            style={{ ...styles.navItem, ...styles.navItemMuted }}
            onClick={() => navigate('/history')}
          >
            <span>🕐</span> History
          </div>
        </nav>
        <div style={styles.sidebarUser}>
          <div style={styles.userAvatar}>
            {user?.username?.[0]?.toUpperCase()}
          </div>
          <div style={styles.userInfo}>
            <div style={styles.userName}>{user?.username}</div>
            <div style={styles.userEmail}>{user?.email}</div>
          </div>
          <button style={styles.signOutBtn} onClick={signOut}>↪</button>
        </div>
      </div>

      <div style={styles.main}>
        <div style={styles.header}>
          <div>
            <p style={styles.greeting}>Good {getTimeOfDay()} 👋</p>
            <h1 style={styles.headerTitle}>How are you feeling?</h1>
          </div>
          {user?.spotify_connected ? (
            <div style={styles.spotifyConnected}>
              <div style={styles.spotifyDot} />
              Spotify connected
            </div>
          ) : (
            <button style={styles.spotifyBtn} onClick={handleConnectSpotify}>
              🎵 Connect Spotify
            </button>
          )}
        </div>

        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Describe your mood</h2>
          <p style={styles.cardSubtitle}>
            Write in any language — French, English, Spanish, anything
          </p>
          <textarea
            style={styles.textarea}
            placeholder="Je suis nostalgique ce soir... or I feel energetic and ready to go..."
            value={text}
            onChange={e => setText(e.target.value)}
            rows={4}
            onKeyDown={e => { if (e.key === 'Enter' && e.metaKey) handleAnalyze(); }}
          />
          <div style={styles.suggestions}>
            {suggestions.map((s, i) => (
              <button key={i} style={styles.chip} onClick={() => setText(s)}>
                {s}
              </button>
            ))}
          </div>
          <button
            style={{ ...styles.generateBtn, opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? '⏳ Analyzing your mood...' : '✨ Generate my playlist'}
          </button>
          <p style={styles.hint}>Tip: Press ⌘+Enter to generate</p>
        </div>

        {result && mood && (
          <div style={{ ...styles.card, animation: 'slideUp 0.4s ease', padding: 0, overflow: 'hidden' }}>
            <div style={{ ...styles.moodHeader, background: mood.bg }}>
              <span style={styles.moodEmoji}>{mood.emoji}</span>
              <div style={{ flex: 1 }}>
                <p style={styles.moodLabel}>Detected mood</p>
                <h2 style={{ ...styles.moodValue, color: mood.color }}>{result.mood}</h2>
              </div>
              <div style={{ ...styles.confidenceRing, borderColor: mood.color }}>
                <span style={{ ...styles.confidenceNum, color: mood.color }}>
                  {Math.round(result.confidence * 100)}%
                </span>
              </div>
            </div>

            <div style={styles.explanationBox}>
              <span>💡</span>
              <p style={styles.explanation}>{result.explanation}</p>
            </div>

            {result.playlist_generated ? (
              <div style={styles.playlistBox}>
                <div style={styles.playlistInfo}>
                  <div style={styles.playlistIcon}>🎵</div>
                  <div style={{ flex: 1 }}>
                    <p style={styles.playlistLabel}>Your playlist is ready</p>
                    <p style={styles.playlistName}>{result.playlist_name}</p>
                  </div>
                </div>
                <a href={result.playlist_url} target="_blank" rel="noreferrer" style={styles.openSpotifyBtn}>
                  ▶ Open in Spotify
                </a>
              </div>
            ) : (
              <div style={styles.noPlaylist}>
                <span>🎵</span>
                <p style={{ color: '#64748b', margin: 0, fontSize: 14 }}>
                  {user?.spotify_connected
                    ? 'Playlist generation failed. Try again.'
                    : 'Connect Spotify above to generate a playlist!'}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        * { box-sizing: border-box; }
        body { margin: 0; background: #0a0a0f; }
        textarea:focus { outline: none; border-color: #1DB954 !important; }
        button:hover { filter: brightness(1.1); }
      `}</style>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex', minHeight: '100vh', background: '#0a0a0f',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    color: '#f1f5f9',
  },
  sidebar: {
    width: 260, background: '#0f172a',
    borderRight: '1px solid rgba(255,255,255,0.06)',
    display: 'flex', flexDirection: 'column',
    padding: '24px 0', position: 'sticky', top: 0, height: '100vh',
  },
  sidebarLogo: {
    display: 'flex', alignItems: 'center', gap: 12,
    padding: '0 20px 24px',
    borderBottom: '1px solid rgba(255,255,255,0.06)', marginBottom: 16,
  },
  logoIcon: {
    width: 40, height: 40, borderRadius: 12,
    background: 'linear-gradient(135deg, #1DB954, #17a34a)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20,
  },
  logoText: { fontSize: 18, fontWeight: 800, color: '#f1f5f9' },
  nav: { flex: 1, padding: '0 12px' },
  navItem: {
    display: 'flex', alignItems: 'center', gap: 12,
    padding: '10px 12px', borderRadius: 10,
    fontSize: 14, fontWeight: 600, cursor: 'pointer',
    color: '#f1f5f9', background: 'rgba(29,185,84,0.1)',
  },
  navItemMuted: { color: '#64748b', background: 'transparent', marginTop: 4, fontWeight: 400 },
  sidebarUser: {
    display: 'flex', alignItems: 'center', gap: 10,
    padding: '16px 20px', borderTop: '1px solid rgba(255,255,255,0.06)',
  },
  userAvatar: {
    width: 36, height: 36, borderRadius: 10,
    background: 'linear-gradient(135deg, #1DB954, #17a34a)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: 14, fontWeight: 700, color: '#fff', flexShrink: 0,
  },
  userInfo: { flex: 1, minWidth: 0 },
  userName: { fontSize: 13, fontWeight: 600, color: '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
  userEmail: { fontSize: 11, color: '#64748b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
  signOutBtn: { background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer', fontSize: 18, padding: 4, flexShrink: 0 },
  main: { flex: 1, padding: 40, maxWidth: 800, overflowY: 'auto' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32 },
  greeting: { color: '#64748b', fontSize: 14, margin: '0 0 6px' },
  headerTitle: { fontSize: 28, fontWeight: 800, margin: 0, letterSpacing: -0.5 },
  spotifyConnected: {
    display: 'flex', alignItems: 'center', gap: 8,
    background: '#0f172a', border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 12, padding: '10px 16px', fontSize: 13, fontWeight: 500,
  },
  spotifyDot: { width: 8, height: 8, borderRadius: 4, background: '#1DB954' },
  spotifyBtn: {
    background: 'linear-gradient(135deg, #1DB954, #17a34a)',
    border: 'none', borderRadius: 12, padding: '10px 18px',
    color: '#fff', fontSize: 14, fontWeight: 600, cursor: 'pointer',
    boxShadow: '0 4px 16px #1DB95440',
  },
  card: {
    background: '#0f172a', border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 20, padding: 24, marginBottom: 20,
    boxShadow: '0 4px 24px rgba(0,0,0,0.3)',
  },
  cardTitle: { fontSize: 20, fontWeight: 800, margin: '0 0 4px', letterSpacing: -0.3 },
  cardSubtitle: { fontSize: 13, color: '#64748b', margin: '0 0 20px' },
  textarea: {
    width: '100%', background: 'rgba(255,255,255,0.04)',
    border: '1.5px solid rgba(255,255,255,0.08)',
    borderRadius: 14, padding: 14, color: '#f1f5f9',
    fontSize: 15, lineHeight: 1.6, resize: 'vertical',
    fontFamily: 'inherit', marginBottom: 12, transition: 'border-color 0.2s',
  },
  suggestions: { display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 },
  chip: {
    background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 20, padding: '6px 12px', color: '#94a3b8',
    fontSize: 12, cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.2s',
  },
  generateBtn: {
    width: '100%', background: 'linear-gradient(135deg, #1DB954, #17a34a)',
    border: 'none', borderRadius: 14, padding: '15px 0',
    color: '#fff', fontSize: 15, fontWeight: 700,
    boxShadow: '0 6px 20px #1DB95440', fontFamily: 'inherit',
  },
  hint: { color: '#475569', fontSize: 12, textAlign: 'center', margin: '10px 0 0' },
  moodHeader: { display: 'flex', alignItems: 'center', gap: 16, padding: 24, borderRadius: '20px 20px 0 0' },
  moodEmoji: { fontSize: 48 },
  moodLabel: { color: '#64748b', fontSize: 11, margin: '0 0 4px', textTransform: 'uppercase', letterSpacing: 0.5 },
  moodValue: { fontSize: 24, fontWeight: 800, margin: 0, textTransform: 'capitalize', letterSpacing: -0.3 },
  confidenceRing: {
    width: 60, height: 60, borderRadius: 30, border: '3px solid',
    display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
  },
  confidenceNum: { fontSize: 14, fontWeight: 800 },
  explanationBox: {
    display: 'flex', gap: 10, alignItems: 'flex-start',
    padding: '16px 24px', color: '#64748b',
    borderBottom: '1px solid rgba(255,255,255,0.06)',
  },
  explanation: { fontSize: 13, lineHeight: 1.6, margin: 0, fontStyle: 'italic' },
  playlistBox: { padding: 24 },
  playlistInfo: { display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 },
  playlistIcon: {
    width: 48, height: 48, borderRadius: 12,
    background: 'linear-gradient(135deg, #1DB954, #17a34a)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, flexShrink: 0,
  },
  playlistLabel: { color: '#64748b', fontSize: 11, margin: '0 0 4px', textTransform: 'uppercase', letterSpacing: 0.5 },
  playlistName: { color: '#f1f5f9', fontSize: 16, fontWeight: 700, margin: 0 },
  openSpotifyBtn: {
    display: 'block', width: '100%',
    background: 'linear-gradient(135deg, #1DB954, #17a34a)',
    borderRadius: 12, padding: '13px 0', color: '#fff',
    fontSize: 14, fontWeight: 700, textAlign: 'center',
    textDecoration: 'none', boxShadow: '0 4px 16px #1DB95440',
  },
  noPlaylist: {
    display: 'flex', gap: 10, alignItems: 'center',
    padding: 20, margin: 16, background: 'rgba(255,255,255,0.03)',
    borderRadius: 12, border: '1px solid rgba(255,255,255,0.06)',
  },
};