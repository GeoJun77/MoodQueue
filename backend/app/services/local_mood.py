"""
Offline mood engine.

A small multilingual (FR / EN / ES / PT) keyword classifier used when no
LLM is configured or when the LLM call fails. It is far less subtle than
Groq/LLaMA, but it needs nothing but Python — it will still run in 20 years.
"""
import random
import re
import unicodedata

from app.services.catalog import CATALOG, all_artists


def normalize(text: str) -> str:
    """lowercase + strip accents: "Énervé" -> "enerve"."""
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


# Word stems per mood. A stem matches the start of a word, so "nostalg"
# matches nostalgie / nostalgique / nostalgic / nostalgia.
# Several entries are multi-word phrases.
MOOD_KEYWORDS: dict[str, list[str]] = {
    "happy": [
        "happy", "joy", "glad", "vacances", "vacation", "holiday", "voyage", "travel", "soleil", "sunny", "great day", "good mood", "smile", "content", "heureu",
        "joie", "joyeu", "bonne humeur", "trop bien", "content", "souri", "feliz",
        "alegr", "contento", "genial", "feel good", "feeling good",
    ],
    "sad": [
        "sad", "cry", "tears", "heartbreak", "broke up", "breakup", "depress", "down",
        "triste", "pleur", "larme", "rupture", "chagrin", "deprim", "mal au coeur",
        "llor", "tristeza", "desamor", "saudade", "chorar", "deuil", "decede", "deces", "passed away", "funeral", "grief", "enterrement", "elle me manque", "il me manque", "coeur brise", "my ex", "mon ex",
    ],
    "angry": [
        "angry", "mad at", "rage", "furious", "pissed", "hate", "unfair", "frustrat",
        "colere", "enerve", "vener", "rageu", "injust", "deteste", "marre", "saoul",
        "enojad", "furia", "odio", "raiva", "chiant",
    ],
    "calm": [
        "calm", "relax", "chill", "peace", "zen", "quiet", "sleep", "lazy sunday",
        "calme", "detente", "repos", "tranquil", "paisible", "dormir", "sieste", "doux",
        "tranquilo", "descanso", "paz", "sossego", "bonne nuit", "good night", "buenas noches",
    ],
    "energetic": [
        "energ", "pumped", "hype", "excited", "ready to go", "dance", "running",
        "excite", "a fond", "danser", "bouger", "courir", "road trip", "roadtrip", "adventure", "aventure",
        "emocionad", "animad", "bailar", "animado",
    ],
    "nostalgic": [
        "nostalg", "childhood", "memories", "remember", "old days", "throwback", "90s",
        "2000s", "enfance", "souvenir", "annees 2000", "annees 90", "quand j'etais petit",
        "avant", "recuerdo", "infancia", "lembranca", "miss the old",
    ],
    "romantic": [
        "love", "crush", "romant", "date", "kiss", "in love", "valentine", "girlfriend",
        "boyfriend", "amour", "amoureu", "crush", "rendez-vous", "bisou", "copine", "copain",
        "mon coeur", "enamorad", "te quiero", "amor", "namorad", "cheri", "pense a elle", "pense a lui", "thinking about her", "thinking about him",
    ],
    "focused": [
        "focus", "study", "work", "concentrat", "exam", "homework", "productiv", "code",
        "coding", "revis", "etudi", "travail", "bosser", "taf", "partiel", "memoire",
        "le bac", "devoirs", "estudi", "trabaj", "concentr", "estudar",
    ],
    "anxious": [
        "anxi", "stress", "worried", "nervous", "panic", "overwhelm", "pressure", "burnout",
        "angoiss", "inquiet", "peur", "panique", "deborde", "epuise", "fatigue", "tired",
        "ansiedad", "nervios", "preocup", "medo", "ansios",
    ],
    "melancholic": [
        "melanchol", "pensive", "rain", "rainy", "gloomy", "grey", "autumn", "bittersweet",
        "melancol", "pensif", "pluie", "pleut", "gris", "automne", "spleen", "nuit",
        "lluvia", "chuva", "3am", "insomni",
    ],
    "spiritual": [
        "god", "jesus", "pray", "faith", "church", "gospel", "worship", "bless", "spiritual",
        "allah", "dieu", "prier", "priere", "foi", "eglise", "seigneur", "louange",
        "dios", "orac", "iglesia", "deus",
    ],
    "party": [
        "party", "celebrat", "birthday", "club", "weekend", "turn up", "drinks", "friends tonight",
        "fete", "soiree", "anniv", "boite", "teuf", "apero", "celebr", "fiesta", "rumba",
        "festa", "balada", "afterwork",
    ],
    "motivated": [
        "motivat", "gym", "workout", "training", "grind", "goal", "hustle", "sport",
        "muscu", "seance", "objectif", "gagner", "determin", "deter", "on lache rien",
        "motivad", "entren", "gimnasio", "treino", "foco total",
    ],
    "lonely": [
        "lonely", "alone", "nobody", "isolat", "empty", "no friends", "by myself",
        "seul", "solitude", "isole", "personne ne", "vide", "abandon",
        "solo", "sola", "soledad", "sozinh", "solidao",
    ],
    "hopeful": [
        "hope", "better", "new start", "fresh start", "optimis", "grateful", "proud",
        "espoir", "espere", "nouveau depart", "optimis", "reconnaissant", "fier",
        "esperanza", "mejor", "esperanca", "orgulh", "tomorrow", "demain",
    ],
    "homesick": [
        "homesick", "home country", "my country", "roots", "africa", "family back home",
        "mal du pays", "mon pays", "chez moi", "racines", "afrique", "bled", "congo",
        "brazzaville", "kinshasa", "antilles", "maghreb", "pays natal", "mi pais", "mi tierra",
        "minha terra",
    ],
}

# Explicit genres -> closest mood (used when the user names a genre)
GENRE_MOOD = {
    "lofi": "focused", "lo-fi": "focused", "classical": "focused", "classique": "focused",
    "piano": "calm", "jazz": "calm", "ambient": "calm", "bossa": "calm", "acoustic": "calm",
    "gospel": "spiritual", "worship": "spiritual", "louange": "spiritual",
    "afrobeat": "party", "amapiano": "party", "reggaeton": "party", "dancehall": "party",
    "house": "energetic", "edm": "energetic", "techno": "energetic", "electro": "energetic",
    "rap": "motivated", "hip hop": "motivated", "hip-hop": "motivated", "trap": "motivated",
    "drill": "angry", "metal": "angry", "rock": "angry", "punk": "angry",
    "rnb": "romantic", "r&b": "romantic", "soul": "romantic", "bachata": "romantic",
    "rumba": "homesick", "ndombolo": "homesick", "coupe decale": "homesick", "zouk": "homesick",
    "rai": "homesick", "highlife": "homesick", "pop": "happy", "disco": "happy",
    "indie": "melancholic", "folk": "melancholic",
}

EXPLANATIONS = {
    "fr": "Je ressens {mood_txt} dans ton message (indice : « {cue} »).",
    "en": "I'm sensing {mood_txt} in your words (clue: \"{cue}\").",
    "es": "Percibo {mood_txt} en tu mensaje (pista: «{cue}»).",
}
DEFAULT_EXPLANATIONS = {
    "fr": "Pas d'émotion très marquée : je te propose une ambiance calme.",
    "en": "No strong emotion detected, so here's a calm vibe.",
    "es": "No detecto una emoción fuerte: te propongo un ambiente tranquilo.",
}
MOOD_TEXT = {
    "fr": {
        "happy": "de la joie", "sad": "de la tristesse", "angry": "de la colère",
        "calm": "un besoin de calme", "energetic": "beaucoup d'énergie",
        "nostalgic": "de la nostalgie", "romantic": "de l'amour",
        "focused": "un besoin de concentration", "anxious": "du stress",
        "melancholic": "de la mélancolie", "spiritual": "un élan spirituel",
        "party": "une envie de faire la fête", "motivated": "de la motivation",
        "lonely": "un sentiment de solitude", "hopeful": "de l'espoir",
        "homesick": "le mal du pays",
    },
    "en": {
        "happy": "joy", "sad": "sadness", "angry": "anger", "calm": "a need for calm",
        "energetic": "lots of energy", "nostalgic": "nostalgia", "romantic": "love",
        "focused": "a need to focus", "anxious": "stress", "melancholic": "melancholy",
        "spiritual": "a spiritual mood", "party": "party vibes", "motivated": "motivation",
        "lonely": "loneliness", "hopeful": "hope", "homesick": "homesickness",
    },
    "es": {
        "happy": "alegría", "sad": "tristeza", "angry": "rabia", "calm": "ganas de calma",
        "energetic": "mucha energía", "nostalgic": "nostalgia", "romantic": "amor",
        "focused": "ganas de concentrarte", "anxious": "estrés", "melancholic": "melancolía",
        "spiritual": "un momento espiritual", "party": "ganas de fiesta",
        "motivated": "motivación", "lonely": "soledad", "hopeful": "esperanza",
        "homesick": "nostalgia de tu tierra",
    },
}

PLAYLIST_NAMES = {
    "happy": ["Sunshine State of Mind ☀️", "Good Vibes Only 😊", "Smile On Repeat 😁"],
    "sad": ["Tears In The Rain 💧", "Heavy Heart Hours 💔", "Let It Out 🥀"],
    "angry": ["Burn It Down 🔥", "Rage Mode On 😤", "Let Off Steam 💢"],
    "calm": ["Slow Breathing Room 🌿", "Quiet Hours 😌", "Soft Landing ☁️"],
    "energetic": ["Full Throttle ⚡", "No Brakes Tonight 🚀", "Volume To Max 🔊"],
    "nostalgic": ["Back In The Day 📼", "Golden Years Rewind 🌅", "Childhood Replay 🎞️"],
    "romantic": ["Hearts In Slow Motion ❤️", "Candlelight Hours 🕯️", "Falling For You 💘"],
    "focused": ["Deep Work Mode 🎯", "Brain On Focus 🧠", "Silent Grind 📚"],
    "anxious": ["Breathe In, Breathe Out 🌬️", "Calm The Storm 🌊", "One Step At A Time 🫶"],
    "melancholic": ["Rainy Window Thoughts 🌧️", "Blue Hour Feelings 🌒", "Bittersweet Nights 🍂"],
    "spiritual": ["Grace & Light 🙏", "Higher Ground ✨", "Faith Frequencies 🕊️"],
    "party": ["Turn Up Tonight 🎉", "Dancefloor Royalty 🪩", "Weekend Fuel 🍾"],
    "motivated": ["Beast Mode On 💪", "Grind Never Stops 🏆", "Built Different 🔥"],
    "lonely": ["Party Of One 🌑", "Empty Room Echoes 🕯️", "Alone, Not Lost 🌌"],
    "hopeful": ["Brighter Days Ahead 🌟", "New Chapter Begins 🌱", "Sunrise Again 🌄"],
    "homesick": ["Back To The Roots 🏠", "Sounds Of Home 🌍", "Le Pays Me Manque 🥁"],
}

_LANG_HINTS = {
    "fr": ["je ", "j'", "suis", " pas ", " moi", " ce soir", " tres", " envie", " mon ", " ma ", " mes ", " c'est", " avec "],
    "es": ["estoy", " muy ", " yo ", " quiero", " tengo", " pero ", " mi ", " esta "],
    "en": ["i'm", " i ", "feel", " my ", " the ", " want", " and ", " today", " tonight"],
}


def detect_language(text: str) -> str:
    t = " " + normalize(text) + " "
    scores = {lang: sum(t.count(h) for h in hints) for lang, hints in _LANG_HINTS.items()}
    lang = max(scores, key=scores.get)
    return lang if scores[lang] > 0 else "en"


def _find(stem: str, text: str) -> bool:
    # Single words are stems ("nostalg" matches "nostalgique"); multi-word
    # phrases must match whole ("my ex" must not match "my exam").
    end = r"(?![a-z])" if " " in stem else ""
    return re.search(r"(?<![a-z])" + re.escape(stem) + end, text) is not None


def analyze_mood_local(text: str) -> dict:
    t = normalize(text)
    scores: dict[str, int] = {}
    cues: dict[str, str] = {}
    for mood, stems in MOOD_KEYWORDS.items():
        for stem in stems:
            if _find(stem.strip(), t):
                # multi-word phrases are stronger signals
                scores[mood] = scores.get(mood, 0) + (2 if " " in stem.strip() else 1)
                cues.setdefault(mood, stem.strip())

    for genre, mood in GENRE_MOOD.items():
        if _find(genre, t):
            scores[mood] = scores.get(mood, 0) + 1
            cues.setdefault(mood, genre)

    lang = detect_language(text)
    if not scores:
        mood, confidence = "calm", 0.35
        explanation = DEFAULT_EXPLANATIONS.get(lang, DEFAULT_EXPLANATIONS["en"])
    else:
        mood = max(scores, key=lambda m: (scores[m], -list(MOOD_KEYWORDS).index(m)))
        total = sum(scores.values())
        confidence = round(min(0.9, 0.45 + 0.1 * scores[mood] + 0.15 * scores[mood] / total), 2)
        lang = lang if lang in EXPLANATIONS else "en"
        explanation = EXPLANATIONS[lang].format(cue=cues[mood], mood_txt=MOOD_TEXT[lang][mood])

    return {
        "mood": mood,
        "confidence": confidence,
        "explanation": explanation,
        "genres": [g for g, m in GENRE_MOOD.items() if m == mood][:6],
        "search_queries": [f"{title} {artist}" for title, artist in CATALOG[mood][:6]],
        "source": "local",
    }


_ARTISTS = all_artists()


def extract_preferences_local(text: str) -> dict:
    t = text.lower()
    artists = [name for key, name in _ARTISTS.items() if re.search(r"(?<!\w)" + re.escape(key) + r"(?!\w)", t)]
    nt = normalize(text)
    genres = [g for g in GENRE_MOOD if _find(g, nt)]
    return {"artists": artists, "genres": genres}


def playlist_name_local(mood: str) -> str:
    return random.choice(PLAYLIST_NAMES.get(mood, ["Your Mood, Your Soundtrack 🎵"]))
