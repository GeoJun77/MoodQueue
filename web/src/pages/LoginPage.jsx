import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, register } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password || (!isLogin && !username)) {
      setError('Please fill in all fields');
      return;
    }
    setLoading(true);
    setError('');
    try {
      let response;
      if (isLogin) {
        response = await login(email, password);
      } else {
        response = await register(email, username, password);
      }
      await signIn(response.data.access_token);
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
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
          <p style={styles.tagline}>Your mood, your soundtrack</p>
        </div>

        {/* Card */}
        <div style={styles.card}>
          {/* Tab switcher */}
          <div style={styles.tabSwitcher}>
            <button
              style={{ ...styles.tab, ...(isLogin ? styles.tabActive : {}) }}
              onClick={() => setIsLogin(true)}
            >
              Sign In
            </button>
            <button
              style={{ ...styles.tab, ...(!isLogin ? styles.tabActive : {}) }}
              onClick={() => setIsLogin(false)}
            >
              Sign Up
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} style={styles.form}>
            {/* Email */}
            <div style={styles.inputGroup}>
              <span style={styles.inputIcon}>✉️</span>
              <input
                style={styles.input}
                type="email"
                placeholder="Email address"
                value={email}
                onChange={e => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            {/* Username — register only */}
            {!isLogin && (
              <div style={styles.inputGroup}>
                <span style={styles.inputIcon}>👤</span>
                <input
                  style={styles.input}
                  type="text"
                  placeholder="Username"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                />
              </div>
            )}

            {/* Password */}
            <div style={styles.inputGroup}>
              <span style={styles.inputIcon}>🔒</span>
              <input
                style={styles.input}
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <button
                type="button"
                style={styles.eyeButton}
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>

            {/* Error message */}
            {error && <p style={styles.error}>{error}</p>}

            {/* Submit button */}
            <button
              type="submit"
              style={{ ...styles.submitButton, opacity: loading ? 0.7 : 1 }}
              disabled={loading}
            >
              {loading ? 'Loading...' : (isLogin ? 'Sign In →' : 'Create Account →')}
            </button>

            {/* Forgot password — only shown in login mode */}
            {isLogin && (
              <p style={styles.forgotText}>
                <span
                  style={styles.forgotLink}
                  onClick={() => navigate('/forgot-password')}
                >
                  Forgot your password?
                </span>
              </p>
            )}
          </form>
        </div>

        {/* Toggle */}
        <p style={styles.footerText}>
          {isLogin ? "New to MoodQueue? " : "Already have an account? "}
          <span
            style={styles.footerLink}
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? 'Sign up free' : 'Sign in'}
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
    position: 'absolute', width: 400, height: 400,
    borderRadius: '50%', top: -100, right: -100,
    background: 'radial-gradient(circle, #1DB95430, transparent)',
    pointerEvents: 'none',
  },
  blob2: {
    position: 'absolute', width: 350, height: 350,
    borderRadius: '50%', bottom: -50, left: -80,
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
    margin: '0 0 8px', letterSpacing: -0.5,
  },
  tagline: { fontSize: 15, color: '#64748b', margin: 0 },
  card: {
    width: '100%', background: 'rgba(15, 23, 42, 0.8)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 24, padding: 28,
    backdropFilter: 'blur(20px)',
    boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
  },
  tabSwitcher: {
    display: 'flex', background: 'rgba(255,255,255,0.05)',
    borderRadius: 14, padding: 4, marginBottom: 28,
  },
  tab: {
    flex: 1, padding: '10px 0', borderRadius: 11,
    border: 'none', background: 'transparent',
    color: '#64748b', fontSize: 14, cursor: 'pointer',
    fontWeight: 400, transition: 'all 0.2s',
  },
  tabActive: {
    background: 'rgba(255,255,255,0.1)',
    color: '#f1f5f9', fontWeight: 700,
  },
  form: { display: 'flex', flexDirection: 'column', gap: 12 },
  inputGroup: {
    display: 'flex', alignItems: 'center',
    background: 'rgba(255,255,255,0.05)',
    border: '1.5px solid rgba(255,255,255,0.08)',
    borderRadius: 14, padding: '0 16px',
    transition: 'border-color 0.2s',
  },
  inputIcon: { fontSize: 16, marginRight: 10, flexShrink: 0 },
  input: {
    flex: 1, background: 'transparent', border: 'none',
    outline: 'none', color: '#f1f5f9', fontSize: 15,
    padding: '14px 0',
  },
  eyeButton: {
    background: 'transparent', border: 'none',
    cursor: 'pointer', fontSize: 16, padding: 4,
  },
  error: {
    color: '#ef4444', fontSize: 13,
    margin: '4px 0', textAlign: 'center',
  },
  submitButton: {
    background: 'linear-gradient(135deg, #1DB954, #17a34a)',
    border: 'none', borderRadius: 14, padding: '16px 0',
    color: '#fff', fontSize: 16, fontWeight: 700,
    cursor: 'pointer', marginTop: 8,
    boxShadow: '0 8px 24px #1DB95440',
    transition: 'all 0.2s', letterSpacing: 0.2,
  },
  forgotText: {
    textAlign: 'center', margin: '4px 0 0',
  },
  forgotLink: {
    color: '#64748b', fontSize: 13,
    cursor: 'pointer', textDecoration: 'underline',
  },
  footerText: { marginTop: 24, color: '#64748b', fontSize: 14 },
  footerLink: {
    color: '#1DB954', fontWeight: 700,
    cursor: 'pointer', textDecoration: 'underline',
  },
};