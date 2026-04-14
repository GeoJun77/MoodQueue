import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, FlatList, ActivityIndicator,
  TouchableOpacity, Linking, useColorScheme
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { getMoodHistory, getPlaylistHistory } from '../services/api';

export default function HistoryScreen() {
  const [moodHistory, setMoodHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const theme = isDark ? darkTheme : lightTheme;

  const moodConfig = {
    happy:      { emoji: '😊', color: '#f59e0b' },
    sad:        { emoji: '😢', color: '#3b82f6' },
    angry:      { emoji: '😠', color: '#ef4444' },
    calm:       { emoji: '😌', color: '#10b981' },
    energetic:  { emoji: '⚡', color: '#f97316' },
    nostalgic:  { emoji: '🌅', color: '#8b5cf6' },
    romantic:   { emoji: '❤️', color: '#ec4899' },
    focused:    { emoji: '🎯', color: '#06b6d4' },
    anxious:    { emoji: '😰', color: '#64748b' },
    relieved:   { emoji: '😮‍💨', color: '#1DB954' },
    melancholic:{ emoji: '🌧️', color: '#6366f1' },
    spiritual:  { emoji: '🙏', color: '#d97706' },
    party:      { emoji: '🎉', color: '#f43f5e' },
    motivated:  { emoji: '💪', color: '#dc2626' },
    lonely:     { emoji: '🌑', color: '#475569' },
    hopeful:    { emoji: '🌟', color: '#eab308' },
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      // Fetch both lists in parallel then merge them by mood_entry_id
      const [moodRes, playlistRes] = await Promise.all([
        getMoodHistory(),
        getPlaylistHistory(),
      ]);
      const merged = moodRes.data.map(entry => ({
        ...entry,
        playlist: playlistRes.data.find(p => p.mood_entry_id === entry.id),
      }));
      setMoodHistory(merged);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric', month: 'short',
      hour: '2-digit', minute: '2-digit',
    });
  };

  const renderItem = ({ item }) => {
    const mood = moodConfig[item.detected_mood] || { emoji: '🎵', color: '#1DB954' };

    return (
      <View style={[styles.card, { backgroundColor: theme.card, borderColor: theme.border }]}>
        {/* Left accent bar colored by mood */}
        <View style={[styles.accentBar, { backgroundColor: mood.color }]} />

        <View style={styles.cardContent}>
          <View style={styles.cardHeader}>
            <Text style={styles.moodEmoji}>{mood.emoji}</Text>
            <View style={{ flex: 1 }}>
              <Text style={[styles.moodName, { color: mood.color }]}>
                {item.detected_mood}
              </Text>
              <Text style={[styles.date, { color: theme.textMuted }]}>
                {formatDate(item.created_at)}
              </Text>
            </View>
            <View style={[styles.badge, { backgroundColor: mood.color + '20' }]}>
              <Text style={[styles.badgeText, { color: mood.color }]}>
                {Math.round((item.confidence_score || 0) * 100)}%
              </Text>
            </View>
          </View>

          {/* Original text the user typed */}
          <Text style={[styles.rawText, { color: theme.textMuted }]} numberOfLines={2}>
            "{item.raw_text}"
          </Text>

          {/* Playlist chip — tapping opens Spotify */}
          {item.playlist && (
            <TouchableOpacity
              style={[styles.playlistChip, { backgroundColor: theme.inputBg, borderColor: theme.border }]}
              onPress={() => Linking.openURL(item.playlist.spotify_playlist_url)}
            >
              <LinearGradient colors={['#1DB954', '#17a34a']} style={styles.playlistChipIcon}>
                <Ionicons name="musical-notes" size={12} color="#fff" />
              </LinearGradient>
              <Text style={[styles.playlistChipText, { color: theme.text }]} numberOfLines={1}>
                {item.playlist.name}
              </Text>
              <Ionicons name="open-outline" size={14} color={theme.textMuted} />
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={[styles.loading, { backgroundColor: theme.bg }]}>
        <ActivityIndicator size="large" color="#1DB954" />
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.bg }]}>
      {/* Stats bar — shows total moods, playlists, and top mood */}
      <View style={[styles.statsBar, { backgroundColor: theme.card, borderColor: theme.border }]}>
        <View style={styles.stat}>
          <Text style={[styles.statNumber, { color: '#1DB954' }]}>{moodHistory.length}</Text>
          <Text style={[styles.statLabel, { color: theme.textMuted }]}>Moods</Text>
        </View>
        <View style={[styles.statDivider, { backgroundColor: theme.border }]} />
        <View style={styles.stat}>
          <Text style={[styles.statNumber, { color: '#1DB954' }]}>
            {moodHistory.filter(m => m.playlist).length}
          </Text>
          <Text style={[styles.statLabel, { color: theme.textMuted }]}>Playlists</Text>
        </View>
        <View style={[styles.statDivider, { backgroundColor: theme.border }]} />
        <View style={styles.stat}>
          <Text style={[styles.statNumber, { color: '#1DB954' }]}>
            {moodHistory.length > 0
              ? (moodConfig[getMostFrequentMood(moodHistory)]?.emoji || '🎵')
              : '—'}
          </Text>
          <Text style={[styles.statLabel, { color: theme.textMuted }]}>Top mood</Text>
        </View>
      </View>

      {/* FlatList — virtualized for performance on long lists */}
      <FlatList
        data={moodHistory}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyEmoji}>🎵</Text>
            <Text style={[styles.emptyTitle, { color: theme.text }]}>No mood entries yet</Text>
            <Text style={[styles.emptyText, { color: theme.textMuted }]}>
              Describe your mood on the home screen to get started
            </Text>
          </View>
        }
      />
    </View>
  );
}

// Returns the most frequently occurring mood in history
function getMostFrequentMood(history) {
  const counts = {};
  history.forEach(m => { counts[m.detected_mood] = (counts[m.detected_mood] || 0) + 1; });
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0];
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  statsBar: {
    flexDirection: 'row', alignItems: 'center',
    marginHorizontal: 20, marginTop: 16, marginBottom: 8,
    borderRadius: 16, borderWidth: 1, paddingVertical: 14,
  },
  stat: { flex: 1, alignItems: 'center' },
  statNumber: { fontSize: 22, fontWeight: '800', letterSpacing: -0.5 },
  statLabel: { fontSize: 11, marginTop: 2 },
  statDivider: { width: 1, height: 32 },
  list: { padding: 20, gap: 12, paddingTop: 8 },
  card: {
    borderRadius: 16, borderWidth: 1, flexDirection: 'row',
    overflow: 'hidden', shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
  },
  accentBar: { width: 4 },
  cardContent: { flex: 1, padding: 16 },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 10 },
  moodEmoji: { fontSize: 28 },
  moodName: { fontSize: 15, fontWeight: '700', textTransform: 'capitalize' },
  date: { fontSize: 11, marginTop: 1 },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
  badgeText: { fontSize: 12, fontWeight: '700' },
  rawText: { fontSize: 12, fontStyle: 'italic', lineHeight: 17, marginBottom: 12 },
  playlistChip: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    padding: 10, borderRadius: 10, borderWidth: 1,
  },
  playlistChipIcon: {
    width: 22, height: 22, borderRadius: 6,
    justifyContent: 'center', alignItems: 'center',
  },
  playlistChipText: { flex: 1, fontSize: 12, fontWeight: '500' },
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  empty: { alignItems: 'center', paddingTop: 60 },
  emptyEmoji: { fontSize: 48, marginBottom: 16 },
  emptyTitle: { fontSize: 18, fontWeight: '700', marginBottom: 8 },
  emptyText: { fontSize: 14, textAlign: 'center', lineHeight: 20, maxWidth: 260 },
});

const darkTheme = {
  bg: '#0a0a0f', text: '#f1f5f9', textMuted: '#64748b',
  card: '#0f172a', border: 'rgba(255,255,255,0.08)',
  inputBg: 'rgba(255,255,255,0.04)',
};

const lightTheme = {
  bg: '#f8faff', text: '#0f172a', textMuted: '#64748b',
  card: '#ffffff', border: 'rgba(0,0,0,0.07)', inputBg: '#f8fafc',
};