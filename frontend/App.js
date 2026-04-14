import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View } from 'react-native';

import { AuthProvider, useAuth } from './src/context/AuthContext';
import LoginScreen from './src/screens/LoginScreen';
import HomeScreen from './src/screens/HomeScreen';
import HistoryScreen from './src/screens/HistoryScreen';

// Stack navigator manages screen history.
// Think of it like a stack of cards — you push screens on top
// and pop them to go back.
const Stack = createNativeStackNavigator();

function Navigation() {
  const { user, loading } = useAuth();

  // Show spinner while checking saved token on app start
  // Prevents a flash of the login screen for logged-in users
  if (loading) {
    return (
      <View style={{
        flex: 1, backgroundColor: '#0a0a0f',
        justifyContent: 'center', alignItems: 'center'
      }}>
        <ActivityIndicator size="large" color="#1DB954" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          // Authenticated stack — user is logged in
          <>
            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen
              name="History"
              component={HistoryScreen}
              options={{
                headerShown: true,
                headerStyle: { backgroundColor: '#0a0a0f' },
                headerTintColor: '#fff',
                headerTitle: 'History',
              }}
            />
          </>
        ) : (
          // Unauthenticated stack — user is not logged in
          <Stack.Screen name="Login" component={LoginScreen} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// Root component — wraps everything in AuthProvider
// so every screen has access to the auth context
export default function App() {
  return (
    <AuthProvider>
      <Navigation />
    </AuthProvider>
  );
}