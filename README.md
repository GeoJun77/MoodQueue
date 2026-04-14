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
``` bash
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
```
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
```

### 2. Configure environment variables
Create a backend/.env file:
```bash
DATABASE_URL=postgresql+asyncpg://moodqueue:moodqueue@db:5432/moodqueue
REDIS_URL=redis://redis:6379
SECRET_KEY=your_secret_key_here
OPENAI_API_KEY=gsk_your_groq_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=https://your-ngrok-url.ngrok-free.dev/api/playlist/callback
```
### 3. Start the backend
```bash
docker-compose up -d
```

The backend will be available at http://localhost:8000
Swagger documentation at http://localhost:8000/docs

### 4. Start the Ngrok tunnel
In a separate terminal:
Copy the generated HTTPS URL and update:

	•	backend/.env → SPOTIFY_REDIRECT_URI
	•	Spotify Developer Dashboard → Redirect URIs
   
### 5. Start the web frontend
```bash
cd web
npm install
npm run dev
```

### 6. Start the mobile frontend
```bash
cd frontend
npm install
npx expo start
```

Scan the QR code with Expo Go (available on App Store and Google Play).
⚠️ Update frontend/src/services/api.js with your local IP:
const BASE_URL = 'http://YOUR_LOCAL_IP:8000';

🎯 Features
	•	✅ JWT Authentication (register / login)
	•	✅ Multilingual mood analysis via Groq LLaMA3
	•	✅ Explicit artist and genre detection from text
	•	✅ Automatic Spotify playlist generation
	•	✅ 3-layer smart search system (artists → genres → AI mood)
	•	✅ 30+ detected contexts (nostalgia, spirituality, workout, study, weather, etc.)
	•	✅ Mood and playlist history
	•	✅ Automatic light / dark mode
	•	✅ Responsive web interface (Vite + React)
	•	✅ iOS and Android mobile app (Expo)

🔌 Main API Endpoints
## 🔌 Main API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Create an account |
| POST | /api/auth/login | Log in |
| GET | /api/auth/me | User profile |
| POST | /api/mood/analyze | Analyze mood + generate playlist |
| GET | /api/mood/history | Mood history |
| GET | /api/playlist/connect | Spotify OAuth URL |
| GET | /api/playlist/callback | Spotify callback |
| GET | /api/playlist/history | Playlist history |

🧩 Context Detection System
The Groq prompt covers more than 30 specific contexts:
	•	Emotions: sadness, joy, anger, nostalgia, melancholy…
	•	Activities: workout, studying, driving, cooking, reading…
	•	Moments: morning, evening, late night, sunset…
	•	Seasons / Weather: rain, summer, winter, sunshine…
	•	Social: friends hangout, romantic date, family gathering, pregame, afterparty…
	•	Cultural roots: African, Latin, Asian, Caribbean music…
	•	Decades: 80s, 90s, 2000s, 2010s…
	•	Specific genres: drill, phonk, amapiano, hyperpop, city pop…
	•	Mental health: anxiety, meditation, burnout, grief…

👤 Author
Geoffroy GANKOUE
Fullstack project — Master Data Science

   
