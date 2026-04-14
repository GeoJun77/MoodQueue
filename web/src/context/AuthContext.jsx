import { createContext, useState, useContext, useEffect } from 'react';
import { getMe } from '../services/api';

// Global auth context — any component can access user and auth functions
// without passing props through every level of the tree
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On app start, check if a token exists in localStorage.
  // If yes, reload the user automatically — no need to log in again.
  useEffect(() => {
    const loadUser = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const response = await getMe();
          setUser(response.data);
        }
      } catch (error) {
        // Token expired or invalid — clear it
        localStorage.removeItem('access_token');
      } finally {
        setLoading(false);
      }
    };
    loadUser();
  }, []);

  // Called after login/register — saves token and loads user
  const signIn = async (token) => {
    localStorage.setItem('access_token', token);
    const response = await getMe();
    setUser(response.data);
  };

  // Called on sign out — clears everything
  const signOut = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook — shortcut to access auth context anywhere
// Usage: const { user, signOut } = useAuth();
export const useAuth = () => useContext(AuthContext);