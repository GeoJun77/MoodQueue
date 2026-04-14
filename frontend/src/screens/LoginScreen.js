import React, { useState, useRef } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  Alert, ActivityIndicator, KeyboardAvoidingView, Platform,
  ScrollView, Animated, useColorScheme, Dimensions
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { login, register } from '../services/api';
import { useAuth } from '../context/AuthContext';

const { height } = Dimensions.get('window');

export default function LoginScreen() {
  const { signIn } = useAuth();
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [focusedInput, setFocusedInput] = useState(null);

  // Animate the card sliding up on mount
  const slideAnim = useRef(new Animated.Value(50)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    Animated.parallel([
      Animated.timing(slideAnim, { toValue: 0, duration: 600, useNativeDriver: true }),
      Animated.timing(fadeAnim, { toValue: 1, duration: 600, useNativeDriver: true }),
    ]).start();
  }, []);

  const handleSubmit = async () => {
    if (!email || !password || (!isLogin && !username)) {
      Alert.alert('Missing fields', 'Please fill in all fields');
      return;
    }
    setLoading(true);
    try {
      let response;
      if (isLogin) {
        response = await login(email, password);
      } else {
        response = await register(email, username, password);
      }
      // Save token — triggers automatic navigation to HomeScreen
      await signIn(response.data.access_token);
    } catch (error) {
      const message = error.response?.data?.detail || 'Something went wrong';
      Alert.alert('Error', message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* Gradient background */}
      <LinearGradient
        colors={isDark ? ['#0a0a0f', '#0d1117', '#111827'] : ['#f0f4ff', '#e8f0fe', '#f8faff']}
        style={StyleSheet.absoluteFill}
      />

      {/* Decorative blobs */}
      <View style={[styles.blob1, { backgroundColor: isDark ? '#1DB95430' : '#1DB95420' }]} />
      <View style={[styles.blob2, { backgroundColor: isDark ? '#7c3aed30' : '#7c3aed15' }]} />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* Logo */}
        <Animated.View style={[
          styles.logoSection,
          { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }
        ]}>
          <LinearGradient colors={['#1DB954', '#17a34a']} style={styles.logoCircle}>
            <Ionicons name="musical-notes" size={32} color="#fff" />
          </LinearGradient>
          <Text style={[styles.appName, { color: theme.text }]}>MoodQueue</Text>
          <Text style={[styles.tagline, { color: theme.textMuted }]}>
            Your mood, your soundtrack
          </Text>
        </Animated.View>

        {/* Auth card */}
        <Animated.View style={[
          styles.card,
          { backgroundColor: theme.card, borderColor: theme.border, opacity: fadeAnim, transform: [{ translateY: slideAnim }] }
        ]}>
          {/* Tab switcher */}
          <View style={[styles.tabSwitcher, { backgroundColor: theme.tabBg }]}>
            <TouchableOpacity
              style={[styles.tab, isLogin && { backgroundColor: theme.tabActive }]}
              onPress={() => setIsLogin(true)}
            >
              <Text style={[styles.tabText, {
                color: isLogin ? theme.tabActiveText : theme.textMuted,
                fontWeight: isLogin ? '700' : '400',
              }]}>Sign In</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.tab, !isLogin && { backgroundColor: theme.tabActive }]}
              onPress={() => setIsLogin(false)}
            >
              <Text style={[styles.tabText, {
                color: !isLogin ? theme.tabActiveText : theme.textMuted,
                fontWeight: !isLogin ? '700' : '400',
              }]}>Sign Up</Text>
            </TouchableOpacity>
          </View>

          {/* Form */}
          <View style={styles.form}>
            {/* Email */}
            <View style={[styles.inputWrapper, {
              backgroundColor: theme.inputBg,
              borderColor: focusedInput === 'email' ? '#1DB954' : theme.border,
            }]}>
              <Ionicons
                name="mail-outline" size={18}
                color={focusedInput === 'email' ? '#1DB954' : theme.textMuted}
                style={styles.inputIcon}
              />
              <TextInput
                style={[styles.input, { color: theme.text }]}
                placeholder="Email address"
                placeholderTextColor={theme.placeholder}
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                onFocus={() => setFocusedInput('email')}
                onBlur={() => setFocusedInput(null)}
              />
            </View>

            {/* Username — register only */}
            {!isLogin && (
              <View style={[styles.inputWrapper, {
                backgroundColor: theme.inputBg,
                borderColor: focusedInput === 'username' ? '#1DB954' : theme.border,
              }]}>
                <Ionicons
                  name="person-outline" size={18}
                  color={focusedInput === 'username' ? '#1DB954' : theme.textMuted}
                  style={styles.inputIcon}
                />
                <TextInput
                  style={[styles.input, { color: theme.text }]}
                  placeholder="Username"
                  placeholderTextColor={theme.placeholder}
                  value={username}
                  onChangeText={setUsername}
                  autoCapitalize="none"
                  onFocus={() => setFocusedInput('username')}
                  onBlur={() => setFocusedInput(null)}
                />
              </View>
            )}

            {/* Password */}
            <View style={[styles.inputWrapper, {
              backgroundColor: theme.inputBg,
              borderColor: focusedInput === 'password' ? '#1DB954' : theme.border,
            }]}>
              <Ionicons
                name="lock-closed-outline" size={18}
                color={focusedInput === 'password' ? '#1DB954' : theme.textMuted}
                style={styles.inputIcon}
              />
              <TextInput
                style={[styles.input, { color: theme.text }]}
                placeholder="Password"
                placeholderTextColor={theme.placeholder}
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                onFocus={() => setFocusedInput('password')}
                onBlur={() => setFocusedInput(null)}
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                <Ionicons
                  name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                  size={18} color={theme.textMuted}
                />
              </TouchableOpacity>
            </View>

            {/* Submit */}
            <TouchableOpacity onPress={handleSubmit} disabled={loading} style={styles.submitButton}>
              <LinearGradient
                colors={loading ? ['#aaa', '#888'] : ['#1DB954', '#17a34a']}
                style={styles.submitGradient}
                start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
              >
                {loading
                  ? <ActivityIndicator color="#fff" />
                  : <>
                      <Text style={styles.submitText}>
                        {isLogin ? 'Sign In' : 'Create Account'}
                      </Text>
                      <Ionicons name="arrow-forward" size={18} color="#fff" />
                    </>
                }
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </Animated.View>

        {/* Footer */}
        <Text style={[styles.footerText, { color: theme.textMuted }]}>
          {isLogin ? 'New to MoodQueue? ' : 'Already have an account? '}
          <Text
            style={{ color: '#1DB954', fontWeight: '700' }}
            onPress={() => setIsLogin(!isLogin)}
          >
            {isLogin ? 'Sign up free' : 'Sign in'}
          </Text>
        </Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  scrollContent: {
    flexGrow: 1, justifyContent: 'center',
    alignItems: 'center', padding: 24, minHeight: height,
  },
  blob1: {
    position: 'absolute', width: 300, height: 300,
    borderRadius: 150, top: -50, right: -80,
  },
  blob2: {
    position: 'absolute', width: 250, height: 250,
    borderRadius: 125, bottom: 100, left: -60,
  },
  logoSection: { alignItems: 'center', marginBottom: 40 },
  logoCircle: {
    width: 72, height: 72, borderRadius: 24,
    justifyContent: 'center', alignItems: 'center', marginBottom: 16,
  },
  appName: { fontSize: 32, fontWeight: '800', letterSpacing: -0.5, marginBottom: 6 },
  tagline: { fontSize: 15, letterSpacing: 0.2 },
  card: {
    width: '100%', maxWidth: 420, borderRadius: 24,
    borderWidth: 1, padding: 24,
    shadowColor: '#000', shadowOffset: { width: 0, height: 20 },
    shadowOpacity: 0.15, shadowRadius: 40, elevation: 10,
  },
  tabSwitcher: {
    flexDirection: 'row', borderRadius: 14,
    padding: 4, marginBottom: 28,
  },
  tab: { flex: 1, paddingVertical: 10, borderRadius: 11, alignItems: 'center' },
  tabText: { fontSize: 14, letterSpacing: 0.1 },
  form: { gap: 12 },
  inputWrapper: {
    flexDirection: 'row', alignItems: 'center',
    borderRadius: 14, borderWidth: 1.5,
    paddingHorizontal: 16, paddingVertical: 14,
  },
  inputIcon: { marginRight: 10 },
  input: { flex: 1, fontSize: 15 },
  submitButton: {
    marginTop: 8, borderRadius: 14, overflow: 'hidden',
    shadowColor: '#1DB954', shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.35, shadowRadius: 16, elevation: 8,
  },
  submitGradient: {
    flexDirection: 'row', alignItems: 'center',
    justifyContent: 'center', paddingVertical: 16, gap: 8,
  },
  submitText: { color: '#fff', fontSize: 16, fontWeight: '700', letterSpacing: 0.2 },
  footerText: { marginTop: 28, fontSize: 14, textAlign: 'center' },
});

const darkTheme = {
  text: '#f1f5f9', textMuted: '#64748b', placeholder: '#475569',
  card: 'rgba(15, 23, 42, 0.8)', border: 'rgba(255,255,255,0.08)',
  inputBg: 'rgba(255,255,255,0.05)', tabBg: 'rgba(255,255,255,0.05)',
  tabActive: 'rgba(255,255,255,0.1)', tabActiveText: '#f1f5f9',
};

const lightTheme = {
  text: '#0f172a', textMuted: '#64748b', placeholder: '#94a3b8',
  card: 'rgba(255,255,255,0.9)', border: 'rgba(0,0,0,0.08)',
  inputBg: '#f8fafc', tabBg: '#f1f5f9',
  tabActive: '#ffffff', tabActiveText: '#0f172a',
};