# 🎵 MoodQueue

MoodQueue is a fullstack application that analyzes a user's mood through free-form text (multilingual) and automatically generates a personalized Spotify playlist using AI.

---

## 🧠 How it works

1. The user describes their mood in free-form text (French, English, Spanish, etc.)
2. The backend analyzes the text with **Groq (LLaMA 3.1 8B Instant)** — a free alternative to OpenAI
3. The system detects explicitly mentioned artists and genres
4. A playlist is generated on **Spotify** using a 3-layer search system:
   - **Layer 1**: Explicitly mentioned artists → only their tracks
   - **Layer 2**: Explicitly mentioned genres → genre tracks + mood
   - **Layer 3**: AI-generated mood queries → shuffled results

> ⚠️ Note: This project uses **Groq** (free) instead of OpenAI (paid). The Groq API key is stored in the `OPENAI_API_KEY` environment variable for compatibility reasons.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy async |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| AI / LLM | Groq (LLaMA 3.1 8B Instant) |
| Music | Spotify Web API (OAuth2) |
| Auth | JWT (python-jose + bcrypt) |
| Migrations | Alembic |
| Containerization | Docker + Docker Compose |
| Web Frontend | Vite + React |
| Mobile Frontend | React Native (Expo SDK 51) |
| HTTPS Tunnel | Ngrok (for Spotify OAuth callback) |

---

## 📁 Project Structure

moodqueue/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/routes/       # auth.py, mood.py, playlist.py
│   │   ├── core/             # config, database, security, dependencies
│   │   ├── models/           # user.py, mood_entry.py, playlist.py
│   │   ├── schemas/          # user.py, mood.py
│   │   └── services/         # mood_service.py, spotify_service.py
│   ├── alembic/              # database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Mobile app React Native (Expo)
│   ├── src/
│   │   ├── screens/          # LoginScreen, HomeScreen, HistoryScreen
│   │   ├── services/         # api.js
│   │   └── context/          # AuthContext.js
│   └── App.js
├── web/                      # Web app React (Vite)
│   ├── src/
│   │   ├── pages/            # LoginPage, HomePage, HistoryPage
│   │   ├── services/         # api.js
│   │   └── context/          # AuthContext.jsx
│   └── App.jsx
└── docker-compose.yml

---

## 🚀 Getting Started

### Prerequisites

- Docker Desktop
- Node.js 18+
- Spotify Developer account
- Groq account (groq.com) — free
- Ngrok (for local Spotify OAuth callback)

### 1. Clone the repository

```bash
git clone https://github.com/GeoJun77/moodqueue.git
cd moodqueue

2. Configure environment variables
Create a backend/.env file:
