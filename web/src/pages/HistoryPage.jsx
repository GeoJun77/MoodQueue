import { useState, useEffect } from 'react';
import { getMoodHistory, getPlaylistHistory } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function HistoryPage() {
  const navigate = useNavigate();
  const [moodHistory, setMoodHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const moodConfig = {
    happy:      { emoji: '😊', color: '#f59e0b' },
    sad:        { emoji: '😢', color: '#3b82f6' },
    angry:      { emoji: '😠', color: '#ef4444' },
    calm:       { emoji: '😌', color: '#10b981' },
    energetic:  { emoji: '⚡', color: '#f97316' },
    nostalgic:  { emoji: '🌅', color: '#8b5cf6' },
    romantic:   { emoji: '❤️', color: '#ec4899' },
    focused:    { emoji: '🎯', color: '#06b6d4' },
    anxious:    { emoji: '😰', color: '#64748b' },
    relieved:   { emoji: '😮‍💨', color: '#1DB954' },
    melancholic:{ emoji: '🌧️', color: '#6366f1' },
    spiritual:  { emoji: '🙏', color: '#d97706' },
    party:      { emoji: '🎉', color: '#f43f5e' },
    motivated:  { emoji: '💪', color: '#dc2626' },
    lonely:     { emoji: '🌑', color: '#475569' },
    hopeful:    { emoji: '🌟', color: '#eab308' },
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const [moodRes, playlistRes] = await Promise.all([
        getMoodHistory(),
        getPlaylistHistory(),
      ]);
      const merged = moodRes.data.map(entry => ({
        ...entry,
        playlist: playlistRes.data.find(p => p.mood_entry_id === entry.id),
      }));
      setMoodHistory(merged);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric', month: 'short',
      hour: '2-digit', minute: '2-digit',
    });
  };

  const getMostFrequentMood = () => {
    if (moodHistory.length === 0) return null;
    const counts = {};
    moodHistory.forEach(m => {
      counts[m.detected_mood] = (counts[m.detected_mood] || 0) + 1;
    });
    return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0];
  };

  const topMood = getMostFrequentMood();

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <div style={styles.sidebarLogo}>
          <div style={styles.logoIcon}>🎵</div>
          <span style={styles.logoText}>MoodQueue</span>
        </div>
        <nav style={styles.nav}>
          <div
            style={{ ...styles.navItem, ...styles.navItemMuted }}
            onClick={() => navigate('/')}
          >
            <span>🏠</span> Home
          </div>
          <div style={styles.navItem}>
            <span>🕐</span> History
          </div>
        </nav>
      </div>

      <div style={styles.main}>
        <div style={styles.header}>
          <h1 style={styles.headerTitle}>Mood History</h1>
          <button style={styles.backBtn} onClick={() => navigate('/')}>
            ← Back to home
          </button>
        </div>

        {!loading && (
          <div style={styles.statsBar}>
            <div style={styles.stat}>
              <span style={styles.statNumber}>{moodHistory.length}</span>
              <span style={styles.statLabel}>Total moods</span>
            </div>
            <div style={styles.statDivider} />
            <div style={styles.stat}>
              <span style={styles.statNumber}>
                {moodHistory.filter(m => m.playlist).length}
              </span>
              <span style={styles.statLabel}>Playlists created</span>
            </div>
            <div style={styles.statDivider} />
            <div style={styles.stat}>
              <span style={styles.statNumber}>
                {topMood ? (moodConfig[topMood]?.emoji || '🎵') : '—'}
              </span>
              <span style={styles.statLabel}>Top mood</span>
            </div>
          </div>
        )}

        {loading && (
          <div style={styles.loading}>
            <p style={{ color: '#64748b' }}>Loading your history...</p>
          </div>
        )}

        {!loading && moodHistory.length === 0 && (
          <div style={styles.empty}>
            <span style={styles.emptyEmoji}>🎵</span>
            <h2 style={styles.emptyTitle}>No mood entries yet</h2>
            <p style={styles.emptyText}>
              Go to the home screen and describe your mood to get started
            </p>
            <button style={styles.goHomeBtn} onClick={() => navigate('/')}>
              Go to home →
            </button>
          </div>
        )}

        <div style={styles.list}>
          {moodHistory.map((item) => {
            const mood = moodConfig[item.detected_mood] || { emoji: '🎵', color: '#1DB954' };
            return (
              <div key={item.id} style={styles.card}>
                <div style={{ ...styles.accentBar, background: mood.color }} />
                <div style={styles.cardContent}>
                  <div style={styles.cardHeader}>
                    <span style={styles.moodEmoji}>{mood.emoji}</span>
                    <div style={{ flex: 1 }}>
                      <p style={{ ...styles.moodName, color: mood.color }}>
                        {item.detected_mood}
                      </p>
                      <p style={styles.date}>{formatDate(item.created_at)}</p>
                    </div>
                    <div style={{ ...styles.badge, background: mood.color + '20' }}>
                      <span style={{ ...styles.badgeText, color: mood.color }}>
                        {Math.round((item.confidence_score || 0) * 100)}%
                      </span>
                    </div>
                  </div>

                  <p style={styles.rawText}>"{item.raw_text}"</p>

                  {item.playlist && (
                    <a
                      href={item.playlist.spotify_playlist_url}
                      target="_blank"
                      rel="noreferrer"
                      style={styles.playlistChip}
                    >
                      <span style={styles.playlistChipIcon}>🎵</span>
                      <span style={styles.playlistChipText}>
                        {item.playlist.name}
                      </span>
                      <span style={{ color: '#64748b', fontSize: 12 }}>↗</span>
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <style>{`
        * { box-sizing: border-box; }
        body { margin: 0; background: #0a0a0f; }
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
  main: { flex: 1, padding: 40, maxWidth: 800, overflowY: 'auto' },
  header: {
    display: 'flex', justifyContent: 'space-between',
    alignItems: 'center', marginBottom: 32,
  },
  headerTitle: { fontSize: 28, fontWeight: 800, margin: 0, letterSpacing: -0.5 },
  backBtn: {
    background: 'transparent', border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 10, padding: '8px 16px', color: '#64748b',
    cursor: 'pointer', fontSize: 13, fontFamily: 'inherit',
  },
  statsBar: {
    display: 'flex', background: '#0f172a',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 16, marginBottom: 24, overflow: 'hidden',
  },
  stat: {
    flex: 1, display: 'flex', flexDirection: 'column',
    alignItems: 'center', padding: '16px 0',
  },
  statNumber: { fontSize: 24, fontWeight: 800, color: '#1DB954', letterSpacing: -0.5 },
  statLabel: { fontSize: 11, color: '#64748b', marginTop: 4 },
  statDivider: { width: 1, background: 'rgba(255,255,255,0.06)' },
  loading: { textAlign: 'center', padding: 60 },
  empty: {
    textAlign: 'center', padding: '60px 0',
    display: 'flex', flexDirection: 'column', alignItems: 'center',
  },
  emptyEmoji: { fontSize: 48, marginBottom: 16 },
  emptyTitle: { fontSize: 20, fontWeight: 700, margin: '0 0 8px' },
  emptyText: { color: '#64748b', fontSize: 14, margin: '0 0 24px', maxWidth: 300 },
  goHomeBtn: {
    background: 'linear-gradient(135deg, #1DB954, #17a34a)',
    border: 'none', borderRadius: 12, padding: '12px 24px',
    color: '#fff', fontSize: 14, fontWeight: 600,
    cursor: 'pointer', fontFamily: 'inherit',
  },
  list: { display: 'flex', flexDirection: 'column', gap: 12 },
  card: {
    display: 'flex', background: '#0f172a',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 16, overflow: 'hidden',
    boxShadow: '0 2px 12px rgba(0,0,0,0.2)',
  },
  accentBar: { width: 4, flexShrink: 0 },
  cardContent: { flex: 1, padding: 16 },
  cardHeader: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 },
  moodEmoji: { fontSize: 28 },
  moodName: { fontSize: 15, fontWeight: 700, margin: 0, textTransform: 'capitalize' },
  date: { fontSize: 11, color: '#64748b', margin: '2px 0 0' },
  badge: { padding: '4px 10px', borderRadius: 20 },
  badgeText: { fontSize: 12, fontWeight: 700 },
  rawText: {
    color: '#64748b', fontSize: 12, fontStyle: 'italic',
    lineHeight: 1.5, margin: '0 0 12px',
    display: '-webkit-box', WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical', overflow: 'hidden',
  },
  playlistChip: {
    display: 'flex', alignItems: 'center', gap: 8,
    padding: '8px 12px', borderRadius: 10,
    background: 'rgba(29,185,84,0.08)',
    border: '1px solid rgba(29,185,84,0.2)',
    textDecoration: 'none', transition: 'all 0.2s',
  },
  playlistChipIcon: { fontSize: 14 },
  playlistChipText: {
    flex: 1, color: '#f1f5f9', fontSize: 12, fontWeight: 500,
    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
  },
};