import { useState } from 'react';
import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import {
  connectSpotify, deleteAccount, disconnectSpotify, getErrorMessage,
} from '../services/api';

export default function AccountPage() {
  const { user, features, refreshUser, signOut } = useAuth();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const run = async (fn) => {
    setBusy(true);
    setError('');
    try { await fn(); } catch (err) { setError(getErrorMessage(err)); } finally { setBusy(false); }
  };

  const handleDelete = () => {
    if (!window.confirm('Delete your account and all your data? This cannot be undone.')) return;
    run(async () => { await deleteAccount(); signOut(); });
  };

  return (
    <Layout>
      <header className="page-header">
        <div>
          <p className="eyebrow">Settings</p>
          <h1 className="page-title">Account</h1>
        </div>
      </header>

      {error && <p className="error-box">{error}</p>}

      <section className="card">
        <h2 className="card-title">Profile</h2>
        <p className="muted small" style={{ margin: '8px 0 0' }}>
          <strong>{user?.username}</strong> · {user?.email}
        </p>
      </section>

      <section className="card">
        <div className="row-between">
          <div>
            <h2 className="card-title">Spotify</h2>
            <p className="muted small" style={{ margin: 0 }}>
              {!features.spotify
                ? 'Not enabled on this server. Playlists come from the built-in catalog, with Spotify, YouTube and Deezer links.'
                : user?.spotify_connected
                  ? 'Connected. New playlists are also saved to your Spotify account.'
                  : 'Connect your account to save playlists directly in Spotify.'}
            </p>
          </div>
          {features.spotify && (user?.spotify_connected ? (
            <button className="btn btn-ghost" disabled={busy}
              onClick={() => run(async () => { await disconnectSpotify(); await refreshUser(); })}>
              Disconnect
            </button>
          ) : (
            <button className="btn" disabled={busy}
              onClick={() => run(async () => { window.location.href = (await connectSpotify()).data.auth_url; })}>
              Connect Spotify
            </button>
          ))}
        </div>
      </section>

      <section className="card">
        <h2 className="card-title">Server</h2>
        <p className="muted small" style={{ margin: '8px 0 0', lineHeight: 1.8 }}>
          Mood analysis: {features.ai ? 'AI (Groq LLaMA)' : 'offline engine'}<br />
          Password reset emails: {features.email ? 'enabled' : 'not configured'}
        </p>
      </section>

      <section className="card">
        <div className="row-between">
          <div>
            <h2 className="card-title">Session</h2>
            <p className="muted small" style={{ margin: 0 }}>Sign out of MoodQueue on this device.</p>
          </div>
          <button className="btn btn-ghost" onClick={signOut}>Sign out</button>
        </div>
      </section>

      <section className="card">
        <div className="row-between">
          <div>
            <h2 className="card-title">Danger zone</h2>
            <p className="muted small" style={{ margin: 0 }}>Permanently delete your account, moods and playlists.</p>
          </div>
          <button className="btn btn-danger" disabled={busy} onClick={handleDelete}>Delete account</button>
        </div>
      </section>
    </Layout>
  );
}
