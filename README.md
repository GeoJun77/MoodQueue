# MoodQueue 🎵

Generate Spotify playlists from your mood

## Tech Stack

**Backend** — Python, FastAPI, PostgreSQL, Redis, Docker  
**AI** — OpenAI API (sentiment analysis)  
**Music** — Spotify Web API  
**Mobile** — React Native (Expo) — iOS & Android  
**Infra** — Docker Compose, GitHub Actions, Railway

## Architecture

User describes mood → NLP analysis → Spotify playlist generated → saved to history

## Getting Started

```bash
git clone https://github.com/TON_USERNAME/moodqueue
cd moodqueue
cp .env.example .env
docker-compose up --build
```

## Project Status

🚧 In development — built step by step as a portfolio project.
