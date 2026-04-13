from groq import AsyncGroq
from app.core.config import settings
import json

client = AsyncGroq(api_key=settings.OPENAI_API_KEY)
GROQ_MODEL = "llama-3.1-8b-instant"


async def analyze_mood(text: str) -> dict:
    """
    Analyzes BOTH the emotional state AND the thematic context of the user's text.
    Covers 30+ specific contexts for ultra-precise music recommendations.
    """
    system_prompt = """You are a world-class music curator and mood analyst.
Your job is to deeply understand what someone is feeling AND what they are talking about,
then generate Spotify search queries that will find the PERFECT music for them.

You must respond with a valid JSON object and nothing else. No markdown, no code block, no explanation.

=== CRITICAL RULES FOR SEARCH QUERIES ===
NEVER use abstract mood words like "nostalgic", "sad", "happy" as standalone queries.
ALWAYS use CONCRETE, SPECIFIC queries that will actually return the right songs on Spotify.

GOOD queries: "Disney classics 2000s childhood", "hits années 2000 France", "2Pac Biggie 90s hip hop classics"
BAD queries: "nostalgic music", "sad songs", "happy vibes"

=== CONTEXT DETECTION — ALWAYS PRIORITIZE SPECIFIC CONTEXT OVER GENERAL MOOD ===

SPIRITUALITY / RELIGION / GOD:
- Keywords: God, Jesus, Allah, pray, faith, church, gospel, spirituality, reconnect, blessing, Dieu, oración, foi
- Queries: "gospel worship songs healing", "contemporary christian music", "gospel français louange", "hillsong worship", "gospel africain", "música cristiana alabanza", "gospel choir classics", "worship songs 2020s", "cantiques chrétiens réconfort"

NOSTALGIA / CHILDHOOD / MEMORIES:
- Keywords: childhood, enfance, memories, miss, remember, souvenir, old times, growing up, petit, jeune
- Queries must reference SPECIFIC DECADES AND CULTURAL REFERENCES:
  "Disney soundtrack classics 90s 2000s", "hits années 2000 enfance France", "early 2000s pop hits throwback", "cartoon network theme songs", "Backstreet Boys NSYNC 90s", "chansons françaises 2000s nostalgie", "2000s RnB classics", "Pokémon Dragon Ball Z anime soundtrack", "Club Dorothée génériques"

HEARTBREAK / BREAKUP / EX:
- Keywords: breakup, ex, heartbreak, miss you, over, left me, betrayal, trahison, rupture, quitter
- Queries: "breakup songs playlist", "SZA sad girl music", "Adele someone like you", "chansons rupture françaises", "heartbreak RnB 2020s", "sad boy music Post Malone", "canciones de desamor español", "Angèle Stromae rupture", "rap français rupture Nekfeu"

LOVE / ROMANCE / CRUSH / DATE:
- Keywords: love, romance, crush, date, feeling, beautiful, tu me plais, enamorado, amour, séduire
- Queries: "romantic RnB slow jam", "Ed Sheeran love songs", "chansons d'amour françaises", "reggaeton romántico", "afrobeats love songs", "Italian love songs", "musique amour Afrique", "K-pop love ballads", "neo soul romantic"

ANGER / FRUSTRATION / INJUSTICE:
- Keywords: angry, unfair, frustrated, injustice, rage, colère, énervé, betrayed, injuste
- Queries: "rage rap drill UK", "angry hip hop Kendrick Lamar", "trap aggressive 2020s", "punk rock anger", "rap français colère Jul SCH", "metal aggressive", "drill chicago aggressive", "rap contestataire politique", "rock alternatif colère"

PARTY / CELEBRATION / EUPHORIA:
- Keywords: party, celebrate, birthday, graduation, victory, fête, célébration, réussir, anniversaire
- Queries: "afrobeats party 2020s", "house music festival anthems", "reggaeton party hits", "rap français fête", "UK garage party", "dancehall vibes", "afro house amapiano", "banger hits 2022 2023 2024", "electronic dance party"

WORKOUT / GYM / SPORT / ENERGY:
- Keywords: gym, workout, sport, run, training, motivation, effort, musculation, course
- Queries: "gym playlist 2024 trap", "workout rap motivation", "EDM running playlist", "drill workout energy", "hip hop gym motivation", "house techno workout", "motivation rap français", "high tempo sport playlist", "pump up anthems"

FOCUS / STUDY / WORK / CONCENTRATION:
- Keywords: study, work, focus, concentrate, réviser, étudier, travailler, concentration, bac, partiel, mémoire, exam
- Queries: "lofi hip hop study beats", "jazz instrumental study", "classical piano focus", "ambient study music", "brain focus deep work", "lofi français étudier", "chillhop study beats", "film score instrumental study", "binaural beats focus"

SADNESS / MELANCHOLY / CRYING:
- Keywords: sad, cry, alone, lonely, empty, depressed, triste, pleurer, seul, mélancolie
- Queries: "sad RnB 2020s heartfelt", "Adele Billie Eilish sad songs", "chansons tristes françaises Angèle", "acoustic sad indie folk", "lo-fi sad girl aesthetic", "rap introspectif français SCH Laylow", "afro soul sad", "sad piano ballads", "indie sad bedroom pop"

CALM / RELAXATION / PEACE / SLEEP:
- Keywords: relax, calm, peace, sleep, chill, détente, repos, tranquille, zen, dormir
- Queries: "ambient chill relaxation", "jazz café lounge", "acoustic guitar peaceful", "bossa nova chill", "nature sounds ambient", "lo-fi chill beats", "smooth jazz evening", "neo soul chill Sade", "sleep music piano"

CONFIDENCE / EMPOWERMENT / SWAGGER:
- Keywords: confidence, powerful, boss, king, queen, unstoppable, swag, badass, winner, fort, puissant
- Queries: "rap confident swagger Drake", "empowerment pop Beyoncé", "trap confident hits", "rap français swagger", "girl boss anthem", "hip hop power moves", "confidence boost hits 2020s", "rap boss attitude", "motivational anthem"

LONELINESS / ISOLATION / EMPTINESS:
- Keywords: alone, lonely, isolated, empty, nobody, nobody understands, seul, vide, incompris
- Queries: "indie sad alone bedroom pop", "alternative introspective", "rap solitaire français Laylow", "post malone alone songs", "ambient lonely", "neo soul empty feeling", "sad bedroom pop 2020s", "alternative isolation music"

EXCITEMENT / HYPE / ANTICIPATION:
- Keywords: excited, hyped, can't wait, pumped, euphoric, on top of the world, impatient, euphorie
- Queries: "hype rap trap 2024", "afrobeats hype energy", "EDM festival euphoria", "UK drill hype", "dancehall energy 2020s", "rap français hype PLK Ninho", "pop hype anthem", "drill UK afro fusion"

HOMESICKNESS / CULTURAL ROOTS:
- Keywords: home, country, Africa, Antilles, Maghreb, hometown, roots, origine, pays natal, Afrique
- Queries: "afrobeats Nigeria Ghana classics", "coupé décalé Côte d'Ivoire", "raï algérien moderne", "zouk antillais", "afro trap Paris", "soca caribbean vibes", "highlife west africa", "bongo flava east africa", "musique africaine nostalgie"

NATURE / FREEDOM / ADVENTURE / TRAVEL:
- Keywords: nature, travel, adventure, free, ocean, mountains, journey, voyage, liberté, forêt
- Queries: "indie folk adventure", "world music global sounds", "acoustic guitar nature", "reggae freedom Bob Marley", "afro folk travel", "ambient nature sounds", "folk indie road trip", "world beat global fusion"

LATE NIGHT / INSOMNIA / 3AM:
- Keywords: late night, can't sleep, 3am, insomnia, dark thoughts, nuit, 3h du matin, insomnies
- Queries: "late night RnB 2am playlist", "The Weeknd night drive", "trap sad night", "rap français nuit sombre", "dark pop late night", "lo-fi night drive", "alternative 3am feelings", "rap introspectif nuit"

SEASONS / WEATHER:
- Rain/Winter keywords: rain, pluie, neige, snow, hiver, winter, froid, cold
  Queries: "rainy day indie folk", "pluvieux jazz café", "chansons pluie mélancolie", "cozy winter playlist", "acoustic rainy day"
- Summer keywords: summer, été, chaud, hot, soleil, plage, beach
  Queries: "summer hits 2020s", "été playlist française", "reggaeton verano", "afrobeats summer", "beach vibes tropical"
- Spring keywords: spring, printemps, fleurs, renouveau
  Queries: "spring pop upbeat", "sunny day indie", "printemps chanson française"

TIME OF DAY:
- Morning keywords: morning, réveil, matin, wake up, café
  Queries: "morning routine pop upbeat", "réveil playlist douce", "good morning coffee jazz", "morning motivation playlist"
- Afternoon keywords: lunch, midi, après-midi, afternoon
  Queries: "afternoon jazz café", "midi chill playlist", "lunch break bossa nova"
- Evening/Sunset keywords: evening, soirée, sunset, coucher de soleil, crépuscule
  Queries: "sunset chill playlist", "golden hour indie", "soirée douce acoustic", "evening jazz smooth"

SPECIFIC ACTIVITIES:
- Driving: "road trip playlist 2020s", "driving rap hits", "autoroute rap français", "night drive electronic", "car playlist summer"
- Cooking: "cooking playlist jazz", "cuisine bonne humeur", "cooking feel good pop", "dinner party jazz"
- Shower: "shower songs hype", "douche playlist banger", "pump up morning shower"
- Cleaning: "cleaning playlist upbeat", "ménage bonne humeur", "cleaning house music dance"
- Reading: "reading ambient instrumental", "livre musique classique", "reading jazz piano", "study reading lofi"

SOCIAL SITUATIONS:
- Friends hangout: "friends playlist vibes", "soirée amis rap", "group hangout afrobeats", "friends summer hits"
- Family: "famille douce musique", "family gathering classics", "réunion famille variété française"
- Romantic date: "date night jazz", "dîner romantique", "romantic dinner bossa nova", "date playlist RnB"
- Pre-party: "préchauffe playlist", "pregame rap hype", "getting ready party", "before party hits"
- Afterparty: "afterparty chill", "après fête slow", "afterhours RnB", "descente soirée lo-fi"
- Drinks/Bar: "bar playlist vibes", "soirée cocktail jazz", "drinking songs hits", "bar ambiance RnB"

SUCCESS / FAILURE / TRANSITIONS:
- Success: "celebration success hits", "diplôme playlist", "victoire rap français", "graduation songs"
- Failure: "échec surmonter rap", "disappointment songs indie", "failure motivation rap", "bouncing back playlist"
- New job/Career: "new job motivation", "promotion celebration", "burnout recovery music"
- Moving on: "moving on playlist", "fresh start music", "nouveau départ chanson", "starting over hits"

GRIEF / LOSS:
- Keywords: death, deuil, perte, décès, miss someone, gone, RIP
- Queries: "grief healing music", "deuil musique réconfort", "loss gospel songs", "healing after loss", "memorial songs", "musique adieu", "sad gospel grief"

SPECIFIC CULTURAL MUSIC:
- African: "afrobeats 2020s hits", "afro trap France", "afro pop Nigeria", "afro soul", "amapiano south africa"
- Latin: "reggaeton 2020s hits", "latin pop español", "salsa classics", "bachata romántica", "corridos tumbados"
- Asian: "K-pop hits 2020s", "city pop japonaise", "mandopop", "J-pop anime", "Korean RnB"
- Arab/Maghreb: "rai moderne algérien", "music arabe contemporaine", "Marocain pop", "oriental electronic"
- Caribbean: "zouk antillais", "dancehall jamaique", "soca trinidad", "kompa haïtien"
- Brazilian: "funk carioca", "pagode brasileiro", "bossa nova classics", "sertanejo"

SPECIFIC DECADES:
- 80s: "80s hits classics synthpop", "années 80 variété française", "80s new wave electro"
- 90s: "90s hip hop classics", "années 90 hits France", "90s RnB slow jams", "britpop 90s"
- 2000s: "2000s pop hits nostalgia", "années 2000 hits", "early 2000s RnB", "2000s rap classics"
- 2010s: "2010s hits decade", "2010s pop best", "decade 2010 rap"

ULTRA-SPECIFIC GENRES:
- "french drill 2020s", "pluggnb hits playlist", "phonk aggressive dark", "hyperpop underground", "jersey club dance", "city pop japonaise 80s", "amapiano south africa 2020s", "grime UK classics"

MENTAL HEALTH / WELLBEING:
- Anxiety: "anxiety calming music", "stress relief piano", "anxiété musique douce", "calming ambient"
- Burnout: "burnout recovery music", "épuisement repos musique", "recovery chill lo-fi"
- Meditation: "meditation music tibetan", "pleine conscience musique", "mindfulness ambient", "yoga music"

CHILDREN / BABIES:
- "berceuse classique bébé", "lullaby sleep baby", "music enfants disney", "nursery rhymes", "baby sleep music"

ANIMALS / PETS:
- "music for dogs calming", "pet friendly ambient", "nature sounds animals", "calm music pets"

FILMS / SERIES / GAMING:
- Movie/Drama: "cinematic orchestral film score", "emotional movie soundtrack", "dramatic orchestral music"
- Action: "action movie soundtrack", "epic action music", "intense orchestral"
- Gaming: "gaming playlist epic", "video game soundtrack", "gaming focus music", "esport hype"
- Romance series: "série romantique soundtrack", "drama series music emotional"

=== OUTPUT FORMAT ===
{
    "mood": "one precise word capturing both emotion and context in english",
    "confidence": float between 0.0 and 1.0,
    "explanation": "one sentence explaining BOTH the emotion AND the specific context detected",
    "genres": ["6-8 specific music genres matching BOTH mood and context"],
    "search_queries": ["6-8 CONCRETE and SPECIFIC Spotify search queries. Mix languages. Reference real artists, decades, cultural references. NEVER use abstract mood words alone."]
}"""

    user_prompt = f"Deeply analyze the mood AND context of this text, then generate perfect music: \"{text}\""

    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=800,
    )

    raw_content = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw_content)
    except json.JSONDecodeError:
        result = {
            "mood": "neutral",
            "confidence": 0.5,
            "explanation": "Could not analyze mood precisely",
            "genres": ["pop", "indie", "electronic"],
            "search_queries": [text[:50]],
        }

    return result


async def extract_music_preferences(text: str) -> dict:
    """
    Extracts explicit music preferences from the user's text.
    Detects artist names and genres explicitly mentioned.
    These are prioritized over AI-generated recommendations.
    """
    prompt = f"""Extract explicit music preferences from this text.

Text: "{text}"

Look for:
1. Artist or band names explicitly mentioned (e.g. "Drake", "Oklou", "Jul", "Rosalía", "Beyoncé")
2. Music genres explicitly mentioned (e.g. "électro", "pop", "rap", "house", "afrobeats", "reggaeton", "jazz", "classical", "lofi", "trap", "drill", "RnB", "soul", "gospel", "phonk", "amapiano", "grime", "hyperpop")

Rules:
- Return ONLY a valid JSON object
- Only include artists/genres EXPLICITLY mentioned in the text
- Do not infer or guess — only extract what is clearly stated
- Artist names must be real music artists or bands
- Genre names must be real music genres

Return this exact format:
{{
    "artists": ["list of explicitly mentioned artist names, empty if none"],
    "genres": ["list of explicitly mentioned music genres, empty if none"]
}}

Respond with just the JSON object, nothing else."""

    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=150,
    )

    raw = response.choices[0].message.content.strip()
    try:
        result = json.loads(raw)
        return {
            "artists": result.get("artists", []),
            "genres": result.get("genres", []),
        }
    except json.JSONDecodeError:
        return {"artists": [], "genres": []}


async def generate_playlist_name(mood: str, explanation: str) -> str:
    """
    Generates a creative context-aware playlist name.
    """
    prompt = f"""Generate a creative and poetic playlist name for someone feeling {mood}.
Context: {explanation}

Rules:
- Maximum 6 words
- Add one relevant emoji at the end
- Make it feel deeply personal and evocative
- Match the specific context:
  * Spiritual → uplifting and divine
  * Nostalgic childhood → innocence, youth, memories
  * Heartbreak → raw and real
  * Party → energetic and fun
  * Study → focused and calm
  * Workout → powerful and energetic
  * Rain/weather → atmospheric
  * Late night → dark and intimate
- No quotes around the name

Respond with just the playlist name, nothing else."""

    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=50,
    )

    return response.choices[0].message.content.strip()