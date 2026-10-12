// Display config for every mood the backend can return
export const moodConfig = {
  happy:       { emoji: '😊', color: '#f59e0b', label: 'Happy' },
  sad:         { emoji: '😢', color: '#3b82f6', label: 'Sad' },
  angry:       { emoji: '😠', color: '#ef4444', label: 'Angry' },
  calm:        { emoji: '😌', color: '#10b981', label: 'Calm' },
  energetic:   { emoji: '⚡', color: '#f97316', label: 'Energetic' },
  nostalgic:   { emoji: '🌅', color: '#8b5cf6', label: 'Nostalgic' },
  romantic:    { emoji: '❤️', color: '#ec4899', label: 'Romantic' },
  focused:     { emoji: '🎯', color: '#06b6d4', label: 'Focused' },
  anxious:     { emoji: '😰', color: '#94a3b8', label: 'Anxious' },
  melancholic: { emoji: '🌧️', color: '#6366f1', label: 'Melancholic' },
  spiritual:   { emoji: '🙏', color: '#d97706', label: 'Spiritual' },
  party:       { emoji: '🎉', color: '#f43f5e', label: 'Party' },
  motivated:   { emoji: '💪', color: '#dc2626', label: 'Motivated' },
  lonely:      { emoji: '🌑', color: '#64748b', label: 'Lonely' },
  hopeful:     { emoji: '🌟', color: '#eab308', label: 'Hopeful' },
  homesick:    { emoji: '🏠', color: '#14b8a6', label: 'Homesick' },
};

export const getMood = (mood) =>
  moodConfig[mood] || { emoji: '🎵', color: '#1DB954', label: mood || 'Unknown' };
