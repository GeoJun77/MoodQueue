import axios from 'axios';

// Empty = same origin: the backend serves this web app and the API together.
// Set VITE_API_URL only when the API lives on another domain (e.g. Vercel + Railway).
const BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
});

// Attach the JWT to every request
api.interceptors.request.use((config) => {
  try {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
  } catch {
    /* storage unavailable (private mode) */
  }
  return config;
});

// Turns any axios error into a message we can display.
// FastAPI returns `detail` as a string (400/401) or as a list of
// validation errors (422).
export const getErrorMessage = (err, fallback = 'Something went wrong') => {
  if (!err?.response) {
    return 'Cannot reach the server. Please try again in a moment.';
  }
  const detail = err.response.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length) {
    return (
      detail
        .map((d) => (d.msg || '').replace(/^Value error, /, ''))
        .filter(Boolean)
        .join(' · ') || fallback
    );
  }
  if (err.response.status >= 500) return 'Server error. Please try again later.';
  return fallback;
};

// Auth
export const register = (email, username, password) =>
  api.post('/api/auth/register', { email, username, password });
export const login = (email, password) => api.post('/api/auth/login', { email, password });
export const getMe = () => api.get('/api/auth/me');
export const deleteAccount = () => api.delete('/api/auth/me');
export const forgotPassword = (email) => api.post('/api/auth/forgot-password', { email });
export const resetPassword = (token, new_password) =>
  api.post('/api/auth/reset-password', { token, new_password });

// Server features (AI / Spotify / email)
export const getStatus = () => api.get('/api/status');

// Moods
export const analyzeMood = (text) => api.post('/api/mood/analyze', { text });
export const getMoodHistory = () => api.get('/api/mood/history');
export const deleteMoodEntry = (id) => api.delete(`/api/mood/history/${id}`);

// Spotify
export const connectSpotify = () => api.get('/api/playlist/connect');
export const disconnectSpotify = () => api.post('/api/playlist/disconnect');
export const getPlaylistHistory = () => api.get('/api/playlist/history');

export default api;
