import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../services/api';

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    if (!token) {
      setError('Invalid reset link');
      return;
    }

    setLoading(true);
    setError('');
    try {
      await api.post(
        `/api/auth/reset-password?token=${encodeURIComponent(token)}&new_password=${encodeURIComponent(password)}`
      );
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid or expired reset link');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.blob1} />
      <div style={styles.blob2} />

      <div style={styles.inner}>
        {/* Logo */}
        <div style={styles.logoSection}>
          <div style={styles.logoCircle}>🎵</div>
          <h1 style={styles.appName}>MoodQueue</h1>
        </div>

        <div style={styles.card}>
          {!success ? (
            <>
              <h2 style={styles.title}>Create a new password</h2>
              <p style={styles.subtitle}>
                Choose a strong password for your account.
              </p>

              <form onSubmit={handleSubmit} style={styles.form}>
                {/* New password */}
                <div style={styles.inputGroup}>
                  <span style={styles.inputIcon}>🔒</span>
                  <input
                    style={styles.input}
                    type={showPassword ? 'text' : 'password'}
                    placeholder="New password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                  />
                  <button
                    type="button"
                    style={styles.eyeButton}
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>

                {/* Confirm password */}
                <div style={styles.inputGroup}>
                  <span style={styles.inputIcon}>🔒</span>
                  <input
                    style={styles.input}
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Confirm new password"
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                  />
                </div>

                {error && <p style={styles.error}>{error}</p>}

                <button
                  type="submit"
                  style={{ ...styles.submitButton, opacity: loading ? 0.7 : 1 }}
                  disabled={loading}
                >
                  {loading ? 'Resetting...' : 'Reset my password →'}
                </button>
              </form>
            </>
          ) : (
            /* Success state */
            <div style={styles.successBox}>
              <span style={styles.successEmoji}>✅</span>
              <h2 style={styles.title}>Password reset!</h2>
              <p style={styles.subtitle}>
                Your password has been updated successfully.
                You can now sign in with your new password.
              </p>
              <button
                style={styles.submitButton}
                onClick={() => navigate('/login')}
              >
                Sign in now →
              </button>
            </div>
          )}
        </div>

        <p style={styles.footerText}>
          Remember your password?{' '}
          <span style={styles.footerLink} onClick={() => navigate('/login')}>
            Sign in
          </span>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #111827 100%)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    position: 'relative', overflow: 'hidden',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
  blob1: {
    position: 'absolute', width: 400, height: 400, borderRadius: '50%',
    top: -100, right: -100,
    background: 'radial-gradient(circle, #1DB95430, transparent)',
    pointerEvents: 'none',
  },
  blob2: {
    position: 'absolute', width: 350, height: 350, borderRadius: '50%',
    bottom: -50, left: -80,
    background: 'radial-gradient(circle, #7c3aed30, transparent)',
    pointerEvents: 'none',
  },
  inner: {
    display: 'flex', flexDirection: 'column',
    alignItems: 'center', width: '100%',
    maxWidth: 440, padding: '0 24px', zIndex: 1,
  },
  logoSection: { textAlign: 'center', marginBottom: 40 },
  logoCircle: {
    width: 72, height: 72, borderRadius: 24,
    background: 'linear-gradient(135deg, #1DB954, #17a34a)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: 32, margin: '0 auto 16px',
    boxShadow: '0 8px 32px #1DB95440',
  },
  appName: {
    fontSize: 32, fontWeight: 800, color: '#f1f5f9',
    margin: 0, letterSpacing: -0.5,
  },
  card: {
    width: '100%',
    background: 'rgba(15, 23, 42, 0.8)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 24, padding: 28,
    backdropFilter: 'blur(20px)',
    boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
  },
  title: {
    fontSize: 20, fontWeight: 800, color: '#f1f5f9',
    margin: '0 0 8px', letterSpacing: -0.3,
  },
  subtitle: {
    fontSize: 14, color: '#64748b', margin: '0 0 24px', lineHeight: 1.6,
  },
  form: { display: 'flex', flexDirection: 'column', gap: 12 },
  inputGroup: {
    display: 'flex', alignItems: 'center',
    background: 'rgba(255,255,255,0.05)',
    border: '1.5px solid rgba(255,255,255,0.08)',
    borderRadius: 14, padding: '0 16px',
  },
  inputIcon: { fontSize: 16, marginRight: 10 },
  input: {
    flex: 1, background: 'transparent', border: 'none',
    outline: 'none', color: '#f1f5f9', fontSize: 15,
    padding: '14px 0',
  },
  eyeButton: {
    background: 'transparent', border: 'none',
    cursor: 'pointer', fontSize: 16, padding: 4,
  },
  error: { color: '#ef4444', fontSize: 13, margin: 0, textAlign: 'center' },
  submitButton: {
    background: 'linear-gradient(135deg, #1DB954, #17a34a)',
    border: 'none', borderRadius: 14, padding: '16px 0',
    color: '#fff', fontSize: 16, fontWeight: 700,
    cursor: 'pointer', marginTop: 8,
    boxShadow: '0 8px 24px #1DB95440', width: '100%',
    fontFamily: 'inherit',
  },
  successBox: { textAlign: 'center' },
  successEmoji: { fontSize: 48, display: 'block', marginBottom: 16 },
  footerText: { marginTop: 24, color: '#64748b', fontSize: 14 },
  footerLink: {
    color: '#1DB954', fontWeight: 700,
    cursor: 'pointer', textDecoration: 'underline',
  },
};