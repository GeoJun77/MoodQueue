from groq import AsyncGroq
from app.core.config import settings

# Initialize the Groq client with our API key.
# We reuse the OPENAI_API_KEY variable — it contains our Groq key.
client = AsyncGroq(api_key=settings.OPENAI_API_KEY)

# The model we use — LLaMA3 8B is free, fast and accurate enough
# for sentiment analysis tasks like mood detection
# Updated model — llama3-8b-8192 was decommissioned by Groq
GROQ_MODEL = "llama-3.1-8b-instant"


async def analyze_mood(text: str) -> dict:
    """
    Analyzes the user's text and extracts their current mood.
    Returns a structured dict with the mood label, confidence score,
    a short explanation, and Spotify search keywords.

    Example input:  "I just finished my exams, feeling relieved and free"
    Example output: {
        "mood": "relieved",
        "confidence": 0.92,
        "explanation": "The user expresses relief after a stressful period",
        "spotify_keywords": "relieved peaceful free uplifting indie"
    }
    """

    # We use a structured prompt to force the model to return clean JSON.
    # The system prompt defines the role and the exact output format expected.
    system_prompt = """You are a mood analysis expert. 
Your job is to analyze the emotional state of a user based on their text.

You must respond with a valid JSON object and nothing else. No explanation, no markdown, no code block.

The JSON must have exactly these fields:
{
    "mood": "one word mood label in english (e.g. happy, sad, nostalgic, energetic, calm, anxious, romantic, focused, angry, melancholic, excited, lonely, grateful, hopeful, confident)",
    "confidence": a float between 0.0 and 1.0 representing how confident you are,
    "explanation": "one short sentence explaining why you detected this mood",
    "spotify_keywords": "4 to 6 keywords to search on Spotify that match this mood perfectly"
}"""

    user_prompt = f"Analyze the mood of this text: \"{text}\""

    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        # Low temperature = more consistent, predictable outputs.
        # High temperature = more creative but less reliable.
        # 0.3 is a good balance for structured data extraction.
        temperature=0.3,
        max_tokens=300,
    )

    # Extract the text content from the response
    raw_content = response.choices[0].message.content.strip()

    # Parse the JSON response from the model
    import json
    try:
        result = json.loads(raw_content)
    except json.JSONDecodeError:
        # If the model didn't return valid JSON despite our instructions,
        # fall back to a default response rather than crashing
        result = {
            "mood": "neutral",
            "confidence": 0.5,
            "explanation": "Could not analyze mood precisely",
            "spotify_keywords": text[:50],
        }

    return result


async def generate_playlist_name(mood: str, explanation: str) -> str:
    """
    Generates a creative playlist name based on the detected mood.
    Called after mood analysis to give each playlist a unique name.

    Example: mood="nostalgic" → "Drifting through golden memories 🌅"
    """

    prompt = f"""Generate a creative and poetic playlist name for someone feeling {mood}.
Context: {explanation}

Rules:
- Maximum 6 words
- Add one relevant emoji at the end
- Make it feel personal and evocative
- No quotes around the name

Respond with just the playlist name, nothing else."""

    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=50,
    )

    return response.choices[0].message.content.strip()