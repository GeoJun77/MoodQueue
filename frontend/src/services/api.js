import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// The base URL of our FastAPI backend.
// We use the machine's local IP instead of "localhost" because
// the phone is a separate device — it can't reach "localhost"
// which refers to the phone itself, not our computer.
const BASE_URL = 'http://172.20.10.2:8000';

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