import { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { getMe, getStatus } from '../services/api';

const AuthContext = createContext(null);

const storage = {
  get: () => { try { return localStorage.getItem('access_token'); } catch { return null; } },
  set: (t) => { try { localStorage.setItem('access_token', t); } catch { /* ignore */ } },
  clear: () => { try { localStorage.removeItem('access_token'); } catch { /* ignore */ } },
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  // Optional server features: { ai, spotify, email }
  const [features, setFeatures] = useState({ ai: false, spotify: false, email: false });

  const refreshUser = useCallback(async () => {
    const response = await getMe();
    setUser(response.data);
    return response.data;
  }, []);

  useEffect(() => {
    getStatus().then((r) => setFeatures(r.data.features)).catch(() => {});
    (async () => {
      try {
        if (storage.get()) await refreshUser();
      } catch {
        storage.clear(); // expired or invalid token
      } finally {
        setLoading(false);
      }
    })();
  }, [refreshUser]);

  const signIn = async (token) => {
    storage.set(token);
    await refreshUser();
  };

  const signOut = () => {
    storage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, features, signIn, signOut, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
