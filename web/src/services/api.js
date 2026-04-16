import axios from 'axios';

// Base URL of our FastAPI backend
const BASE_URL = 'https://moodqueue-production.up.railway.app';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Automatically attach JWT token to every request
// Reads from localStorage — web equivalent of AsyncStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const register = (email, username, password) =>
  api.post('/api/auth/register', { email, username, password });

export const login = (email, password) =>
  api.post('/api/auth/login', { email, password });

export const getMe = () => api.get('/api/auth/me');

export const analyzeMood = (text) =>
  api.post('/api/mood/analyze', { text });

export const getMoodHistory = () => api.get('/api/mood/history');

export const connectSpotify = () => api.get('/api/playlist/connect');

export const getPlaylistHistory = () => api.get('/api/playlist/history');

export default api;