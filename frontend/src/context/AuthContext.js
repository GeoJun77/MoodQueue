import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getMe } from '../services/api';

// React Context lets us share auth data globally without prop drilling.
// Any component can access user and auth functions with useAuth().
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // On app start, check if a token was saved from a previous session.
  // If yes, reload the user automatically — no need to log in again.
  useEffect(() => {
    const loadUser = async () => {
      try {
        const savedToken = await AsyncStorage.getItem('access_token');
        if (savedToken) {
          setToken(savedToken);
          const response = await getMe();
          setUser(response.data);
        }
      } catch (error) {
        // Token expired or invalid — clear it
        await AsyncStorage.removeItem('access_token');
      } finally {
        setLoading(false);
      }
    };
    loadUser();
  }, []);

  // Called after login/register — saves token and loads user profile.
  // Automatically triggers navigation to HomeScreen via App.js.
  const signIn = async (newToken) => {
    await AsyncStorage.setItem('access_token', newToken);
    setToken(newToken);
    const response = await getMe();
    setUser(response.data);
  };

  // Called on sign out — clears everything.
  // Navigation stack automatically shows Login screen.
  const signOut = async () => {
    await AsyncStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook — shortcut to access auth context anywhere.
// Usage: const { user, signOut } = useAuth();
export const useAuth = () => useContext(AuthContext);