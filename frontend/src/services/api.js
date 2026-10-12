import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Backend URL. Set it in frontend/.env:
//   EXPO_PUBLIC_API_URL=http://192.168.1.20:8000   (your computer's local IP)
// A phone can't use "localhost": that would be the phone itself.
const BASE_URL = (process.env.EXPO_PUBLIC_API_URL || 'http://192.168.1.20:8000').replace(/\/$/, '');

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Interceptor — runs automatically before EVERY request.
// Reads the JWT token from local storage and attaches it
// to the Authorization header so protected routes work.
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Same helper as the web app: readable message for any API error
export const getErrorMessage = (err, fallback = 'Something went wrong') => {
  if (!err?.response) return 'Cannot reach the server. Please try again in a moment.';
  const detail = err.response.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length) {
    return detail.map((d) => (d.msg || '').replace(/^Value error, /, '')).filter(Boolean).join('\n') || fallback;
  }
  return fallback;
};

export const register = (email, username, password) =>
  api.post('/api/auth/register', { email, username, password });

export const login = (email, password) =>
  api.post('/api/auth/login', { email, password });

export const getMe = () =>
  api.get('/api/auth/me');

export const analyzeMood = (text) =>
  api.post('/api/mood/analyze', { text });

export const getMoodHistory = () =>
  api.get('/api/mood/history');

export const connectSpotify = () =>
  api.get('/api/playlist/connect');

export const getPlaylistHistory = () =>
  api.get('/api/playlist/history');

export default api;