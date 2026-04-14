import React, { useState, useRef } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, Alert, ScrollView, Linking,
  Animated, useColorScheme, Dimensions, Platform
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { analyzeMood, connectSpotify } from '../services/api';
import { useAuth } from '../context/AuthContext';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const { user, signOut } = useAuth();
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const resultAnim = useRef(new Animated.Value(0)).current;
  const resultSlide = useRef(new Animated.Value(30)).current;

  const moodConfig = {
    happy:      { emoji: '😊', color: '#f59e0b', bg: '#fef3c7' },
    sad:        { emoji: '😢', color: '#3b82f6', bg: '#dbeafe' },
    angry:      { emoji: '😠', color: '#ef4444', bg: '#fee2e2' },
    calm:       { emoji: '😌', color: '#10b981', bg: '#d1fae5' },
    energetic:  { emoji: '⚡', color: '#f97316', bg: '#ffedd5' },
    nostalgic:  { emoji: '🌅', color: '#8b5cf6', bg: '#ede9fe' },
    romantic:   { emoji: '❤️', color: '#ec4899', bg: '#fce7f3' },
    focused:    { emoji: '🎯', color: '#06b6d4', bg: '#cffafe' },
    anxious:    { emoji: '😰', color: '#64748b', bg: '#f1f5f9' },
    relieved:   { emoji: '😮‍💨', color: '#1DB954', bg: '#dcfce7' },
    melancholic:{ emoji: '🌧️', color: '#6366f1', bg: '#e0e7ff' },
    spiritual:  { emoji: '🙏', color: '#d97706', bg: '#fef3c7' },
    party:      { emoji: '🎉', color: '#f43f5e', bg: '#ffe4e6' },
    motivated:  { emoji: '💪', color: '#dc2626', bg: '#fee2e2' },
    lonely:     { emoji: '🌑', color: '#475569', bg: '#f8fafc' },
    hopeful:    { emoji: '🌟', color: '#eab308', bg: '#fefce8' },
  };

  const suggestions = [
    "Je suis nostalgique ce soir 🌅",
    "Besoin d'énergie pour bosser ⚡",
    "Mélancolique et pensif 🌧️",
    "Je veux faire la fête 🎉",
    "Moment calme et zen 😌",
  ];

  const handleAnalyze = async () => {
    if (!text.trim()) {
      Alert.alert('', 'Tell me how you feel first 😊');
      return;
    }
    setLoading(true);
    setResult(null);
    resultAnim.setValue(0);
    resultSlide.setValue(30);

    try {
      const response = await analyzeMood(text);
      setResult(response.data);

      // Animate result card in with spring effect
      Animated.parallel([
        Animated.spring(resultAnim, { toValue: 1, useNativeDriver: true, tension: 50, friction: 8 }),
        Animated.spring(resultSlide, { toValue: 0, useNativeDriver: true, tension: 50, friction: 8 }),
      ]).start();
    } catch (error) {
      Alert.alert('Error', 'Could not analyze your mood. Try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectSpotify = async () => {
    try {
      const response = await connectSpotify();
      await Linking.openURL(response.data.auth_url);
    } catch (error) {
      Alert.alert('Error', 'Could not connect to Spotify');
    }
  };

  const mood = result
    ? (moodConfig[result.mood] || { emoji: '🎵', color: '#1DB954', bg: '#dcfce7' })
    : null;

  return (
    <View style={[styles.container, { backgroundColor: theme.bg }]}>
      <ScrollView showsVerticalScrollIndicator={false}>

        {/* Header */}
        <LinearGradient
          colors={isDark ? ['#0d1117', '#0d1117'] : ['#f0f4ff', '#f8faff']}
          style={styles.header}
        >
          <View style={styles.headerTop}>
            <View>
              <Text style={[styles.greeting, { color: theme.textMuted }]}>
                Good {getTimeOfDay()} 👋
              </Text>
              <Text style={[styles.username, { color: theme.text }]}>
                {user?.username}
              </Text>
            </View>
            <View style={styles.headerActions}>
              <TouchableOpacity
                style={[styles.iconButton, { backgroundColor: theme.card, borderColor: theme.border }]}
                onPress={() => navigation.navigate('History')}
              >
                <Ionicons name="time-outline" size={20} color={theme.text} />
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.iconButton, { backgroundColor: theme.card, borderColor: theme.border }]}
                onPress={signOut}
              >
                <Ionicons name="log-out-outline" size={20} color={theme.text} />
              </TouchableOpacity>
            </View>
          </View>

          {/* Spotify banner */}
          {!user?.spotify_connected && (
            <TouchableOpacity style={styles.spotifyBanner} onPress={handleConnectSpotify}>
              <LinearGradient
                colors={['#1DB954', '#17a34a']}
                style={styles.spotifyBannerInner}
                start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
              >
                <Ionicons name="musical-notes" size={18} color="#fff" />
                <Text style={styles.spotifyBannerText}>
                  Connect Spotify to generate playlists
                </Text>
                <Ionicons name="chevron-forward" size={16} color="#fff" />
              </LinearGradient>
            </TouchableOpacity>
          )}

          {user?.spotify_connected && (
            <View style={[styles.spotifyConnected, { backgroundColor: theme.card, borderColor: theme.border }]}>
              <View style={styles.spotifyDot} />
              <Text style={[styles.spotifyConnectedText, { color: theme.text }]}>
                Spotify connected
              </Text>
            </View>
          )}
        </LinearGradient>

        <View style={styles.content}>

          {/* Mood input card */}
          <View style={[styles.card, { backgroundColor: theme.card, borderColor: theme.border }]}>
            <Text style={[styles.cardTitle, { color: theme.text }]}>
              How are you feeling?
            </Text>
            <Text style={[styles.cardSubtitle, { color: theme.textMuted }]}>
              Describe your mood in any language
            </Text>

            <TextInput
              style={[styles.textArea, {
                backgroundColor: theme.inputBg,
                color: theme.text,
                borderColor: theme.border,
              }]}
              placeholder="Je suis nostalgique ce soir... or I feel energetic and ready..."
              placeholderTextColor={theme.placeholder}
              value={text}
              onChangeText={setText}
              multiline
              numberOfLines={4}
              textAlignVertical="top"
            />

            {/* Quick mood suggestions */}
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              style={styles.suggestions}
              contentContainerStyle={{ gap: 8, paddingRight: 4 }}
            >
              {suggestions.map((s, i) => (
                <TouchableOpacity
                  key={i}
                  style={[styles.suggestionChip, { backgroundColor: theme.inputBg, borderColor: theme.border }]}
                  onPress={() => setText(s)}
                >
                  <Text style={[styles.suggestionText, { color: theme.textMuted }]}>{s}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            {/* Generate button */}
            <TouchableOpacity
              onPress={handleAnalyze}
              disabled={loading}
              style={styles.generateButton}
            >
              <LinearGradient
                colors={loading ? ['#64748b', '#475569'] : ['#1DB954', '#17a34a']}
                style={styles.generateGradient}
                start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
              >
                {loading ? (
                  <>
                    <ActivityIndicator color="#fff" size="small" />
                    <Text style={styles.generateText}>Analyzing your mood...</Text>
                  </>
                ) : (
                  <>
                    <Ionicons name="sparkles" size={18} color="#fff" />
                    <Text style={styles.generateText}>Generate my playlist</Text>
                  </>
                )}
              </LinearGradient>
            </TouchableOpacity>
          </View>

          {/* Result card — animated spring entrance */}
          {result && mood && (
            <Animated.View style={{
              opacity: resultAnim,
              transform: [{ translateY: resultSlide }],
            }}>
              <View style={[styles.card, styles.resultCard, {
                backgroundColor: theme.card,
                borderColor: theme.border,
              }]}>
                {/* Mood header with color background */}
                <View style={[styles.moodHeader, {
                  backgroundColor: isDark ? mood.color + '25' : mood.bg,
                }]}>
                  <Text style={styles.moodEmoji}>{mood.emoji}</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.moodLabel, { color: theme.textMuted }]}>
                      Detected mood
                    </Text>
                    <Text style={[styles.moodValue, { color: mood.color }]}>
                      {result.mood}
                    </Text>
                  </View>
                  {/* Confidence ring */}
                  <View style={[styles.confidenceRing, { borderColor: mood.color }]}>
                    <Text style={[styles.confidenceNumber, { color: mood.color }]}>
                      {Math.round(result.confidence * 100)}
                    </Text>
                    <Text style={[styles.confidencePercent, { color: mood.color }]}>%</Text>
                  </View>
                </View>

                {/* AI explanation */}
                <View style={styles.explanationBox}>
                  <Ionicons name="bulb-outline" size={14} color={theme.textMuted} />
                  <Text style={[styles.explanation, { color: theme.textMuted }]}>
                    {result.explanation}
                  </Text>
                </View>

                {/* Playlist result */}
                {result.playlist_generated ? (
                  <View style={[styles.playlistSection, { borderTopColor: theme.border }]}>
                    <View style={styles.playlistInfo}>
                      <LinearGradient
                        colors={['#1DB954', '#17a34a']}
                        style={styles.playlistIcon}
                      >
                        <Ionicons name="musical-notes" size={20} color="#fff" />
                      </LinearGradient>
                      <View style={{ flex: 1 }}>
                        <Text style={[styles.playlistLabel, { color: theme.textMuted }]}>
                          Your playlist is ready
                        </Text>
                        <Text style={[styles.playlistName, { color: theme.text }]} numberOfLines={2}>
                          {result.playlist_name}
                        </Text>
                      </View>
                    </View>
                    <TouchableOpacity
                      style={styles.openSpotifyButton}
                      onPress={() => Linking.openURL(result.playlist_url)}
                    >
                      <LinearGradient
                        colors={['#1DB954', '#17a34a']}
                        style={styles.openSpotifyGradient}
                        start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
                      >
                        <Ionicons name="play" size={16} color="#fff" />
                        <Text style={styles.openSpotifyText}>Open in Spotify</Text>
                      </LinearGradient>
                    </TouchableOpacity>
                  </View>
                ) : (
                  <View style={[styles.noPlaylist, {
                    backgroundColor: theme.inputBg,
                    borderColor: theme.border,
                    margin: 16,
                  }]}>
                    <Ionicons name="musical-note-outline" size={20} color={theme.textMuted} />
                    <Text style={[styles.noPlaylistText, { color: theme.textMuted }]}>
                      {user?.spotify_connected
                        ? 'Playlist generation failed. Try again.'
                        : 'Connect Spotify to generate a playlist'}
                    </Text>
                  </View>
                )}
              </View>
            </Animated.View>
          )}

          <View style={{ height: 40 }} />
        </View>
      </ScrollView>
    </View>
  );
}

function getTimeOfDay() {
  const h = new Date().getHours();
  if (h < 12) return 'morning';
  if (h < 17) return 'afternoon';
  return 'evening';
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: {
    paddingTop: Platform.OS === 'ios' ? 60 : 40,
    paddingHorizontal: 20, paddingBottom: 20,
  },
  headerTop: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'flex-start', marginBottom: 16,
  },
  greeting: { fontSize: 13, marginBottom: 2 },
  username: { fontSize: 24, fontWeight: '800', letterSpacing: -0.5 },
  headerActions: { flexDirection: 'row', gap: 8 },
  iconButton: {
    width: 40, height: 40, borderRadius: 12,
    justifyContent: 'center', alignItems: 'center', borderWidth: 1,
  },
  spotifyBanner: { borderRadius: 14, overflow: 'hidden', marginTop: 4 },
  spotifyBannerInner: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 16, paddingVertical: 12, gap: 8,
  },
  spotifyBannerText: { flex: 1, color: '#fff', fontSize: 14, fontWeight: '600' },
  spotifyConnected: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    paddingHorizontal: 14, paddingVertical: 10,
    borderRadius: 12, borderWidth: 1, marginTop: 4,
  },
  spotifyDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#1DB954' },
  spotifyConnectedText: { fontSize: 13, fontWeight: '500' },
  content: { padding: 20, gap: 16 },
  card: {
    borderRadius: 20, borderWidth: 1, padding: 20,
    shadowColor: '#000', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06, shadowRadius: 16, elevation: 4,
  },
  resultCard: { padding: 0, overflow: 'hidden' },
  cardTitle: { fontSize: 20, fontWeight: '800', letterSpacing: -0.3, marginBottom: 4 },
  cardSubtitle: { fontSize: 13, marginBottom: 16 },
  textArea: {
    borderRadius: 14, borderWidth: 1.5, padding: 14,
    fontSize: 15, minHeight: 110, lineHeight: 22, marginBottom: 12,
  },
  suggestions: { marginBottom: 16 },
  suggestionChip: {
    paddingHorizontal: 12, paddingVertical: 8,
    borderRadius: 20, borderWidth: 1,
  },
  suggestionText: { fontSize: 12 },
  generateButton: {
    borderRadius: 14, overflow: 'hidden',
    shadowColor: '#1DB954', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 12, elevation: 6,
  },
  generateGradient: {
    flexDirection: 'row', alignItems: 'center',
    justifyContent: 'center', paddingVertical: 16, gap: 8,
  },
  generateText: { color: '#fff', fontSize: 15, fontWeight: '700' },
  moodHeader: {
    flexDirection: 'row', alignItems: 'center', padding: 20, gap: 12,
  },
  moodEmoji: { fontSize: 44 },
  moodLabel: { fontSize: 11, marginBottom: 2, textTransform: 'uppercase', letterSpacing: 0.5 },
  moodValue: { fontSize: 22, fontWeight: '800', textTransform: 'capitalize', letterSpacing: -0.3 },
  confidenceRing: {
    width: 52, height: 52, borderRadius: 26,
    borderWidth: 2.5, justifyContent: 'center', alignItems: 'center',
  },
  confidenceNumber: { fontSize: 16, fontWeight: '800', lineHeight: 18 },
  confidencePercent: { fontSize: 9, fontWeight: '600' },
  explanationBox: {
    flexDirection: 'row', gap: 8, alignItems: 'flex-start',
    paddingHorizontal: 20, paddingBottom: 16,
  },
  explanation: { flex: 1, fontSize: 13, lineHeight: 18, fontStyle: 'italic' },
  playlistSection: {
    borderTopWidth: 1, padding: 20, gap: 14,
  },
  playlistInfo: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  playlistIcon: {
    width: 44, height: 44, borderRadius: 12,
    justifyContent: 'center', alignItems: 'center',
  },
  playlistLabel: { fontSize: 11, marginBottom: 3, textTransform: 'uppercase', letterSpacing: 0.5 },
  playlistName: { fontSize: 15, fontWeight: '700', letterSpacing: -0.2 },
  openSpotifyButton: { borderRadius: 12, overflow: 'hidden' },
  openSpotifyGradient: {
    flexDirection: 'row', alignItems: 'center',
    justifyContent: 'center', paddingVertical: 13, gap: 8,
  },
  openSpotifyText: { color: '#fff', fontSize: 14, fontWeight: '700' },
  noPlaylist: {
    borderRadius: 12, padding: 16, borderWidth: 1,
    flexDirection: 'row', alignItems: 'center', gap: 10,
  },
  noPlaylistText: { fontSize: 13, flex: 1 },
});

const darkTheme = {
  bg: '#0a0a0f', text: '#f1f5f9', textMuted: '#64748b',
  placeholder: '#475569', card: '#0f172a',
  border: 'rgba(255,255,255,0.08)', inputBg: 'rgba(255,255,255,0.04)',
};

const lightTheme = {
  bg: '#f8faff', text: '#0f172a', textMuted: '#64748b',
  placeholder: '#94a3b8', card: '#ffffff',
  border: 'rgba(0,0,0,0.07)', inputBg: '#f8fafc',
};