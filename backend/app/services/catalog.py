"""
Built-in music catalog.

Used when Spotify isn't connected (or is unavailable): MoodQueue still
builds a playlist from these tracks, with search links to Spotify,
YouTube and Deezer. Pure data, no network needed — this part of the app
keeps working forever.

Each mood has ~12 well-known tracks: (title, artist).
"""
from urllib.parse import quote, quote_plus

CATALOG: dict[str, list[tuple[str, str]]] = {
    "happy": [
        ("Happy", "Pharrell Williams"),
        ("Good as Hell", "Lizzo"),
        ("Walking on Sunshine", "Katrina and the Waves"),
        ("Can't Stop the Feeling!", "Justin Timberlake"),
        ("Uptown Funk", "Mark Ronson, Bruno Mars"),
        ("Dancing Queen", "ABBA"),
        ("Mr. Blue Sky", "Electric Light Orchestra"),
        ("Love Nwantiti", "CKay"),
        ("Joro", "Wizkid"),
        ("Djadja", "Aya Nakamura"),
        ("Shut Up and Dance", "WALK THE MOON"),
        ("September", "Earth, Wind & Fire"),
    ],
    "sad": [
        ("Someone Like You", "Adele"),
        ("Fix You", "Coldplay"),
        ("when the party's over", "Billie Eilish"),
        ("Skinny Love", "Bon Iver"),
        ("Formidable", "Stromae"),
        ("Tout oublier", "Angèle, Roméo Elvis"),
        ("Hurt", "Johnny Cash"),
        ("Liability", "Lorde"),
        ("drivers license", "Olivia Rodrigo"),
        ("Ne me quitte pas", "Jacques Brel"),
        ("The Night We Met", "Lord Huron"),
        ("Say Something", "A Great Big World, Christina Aguilera"),
    ],
    "angry": [
        ("Killing in the Name", "Rage Against the Machine"),
        ("Break Stuff", "Limp Bizkit"),
        ("DNA.", "Kendrick Lamar"),
        ("Bodies", "Drowning Pool"),
        ("Numb", "Linkin Park"),
        ("Given Up", "Linkin Park"),
        ("Chop Suey!", "System of a Down"),
        ("No Church in the Wild", "JAY-Z, Kanye West"),
        ("Mo Bamba", "Sheck Wes"),
        ("Smells Like Teen Spirit", "Nirvana"),
        ("Bitch Better Have My Money", "Rihanna"),
        ("Duality", "Slipknot"),
    ],
    "calm": [
        ("Weightless", "Marconi Union"),
        ("Clair de Lune", "Claude Debussy"),
        ("Gymnopédie No. 1", "Erik Satie"),
        ("Sunset Lover", "Petit Biscuit"),
        ("Holocene", "Bon Iver"),
        ("The Girl from Ipanema", "Stan Getz, João Gilberto"),
        ("Banana Pancakes", "Jack Johnson"),
        ("Bloom", "The Paper Kites"),
        ("Pink + White", "Frank Ocean"),
        ("Nuvole Bianche", "Ludovico Einaudi"),
        ("Cherry Wine", "Hozier"),
        ("Better Together", "Jack Johnson"),
    ],
    "energetic": [
        ("Titanium", "David Guetta, Sia"),
        ("Don't Stop Me Now", "Queen"),
        ("Levels", "Avicii"),
        ("Mr. Brightside", "The Killers"),
        ("Blinding Lights", "The Weeknd"),
        ("Wake Me Up", "Avicii"),
        ("Turn Down for What", "DJ Snake, Lil Jon"),
        ("Petit génie", "Jungeli"),
        ("Pump It", "The Black Eyed Peas"),
        ("Can't Hold Us", "Macklemore & Ryan Lewis"),
        ("Tsunami", "DVBBS, Borgeous"),
        ("Physical", "Dua Lipa"),
    ],
    "nostalgic": [
        ("Toxic", "Britney Spears"),
        ("I Want It That Way", "Backstreet Boys"),
        ("Bye Bye Bye", "*NSYNC"),
        ("Hey Ya!", "OutKast"),
        ("Umbrella", "Rihanna"),
        ("Dragostea Din Tei", "O-Zone"),
        ("Wannabe", "Spice Girls"),
        ("Libérée, délivrée", "Anaïs Delva"),
        ("Pokémon Theme", "Jason Paige"),
        ("Mistral gagnant", "Renaud"),
        ("Désenchantée", "Mylène Farmer"),
        ("Last Friday Night (T.G.I.F.)", "Katy Perry"),
    ],
    "romantic": [
        ("Perfect", "Ed Sheeran"),
        ("All of Me", "John Legend"),
        ("At Last", "Etta James"),
        ("La Vie en rose", "Édith Piaf"),
        ("Adorn", "Miguel"),
        ("Essence", "Wizkid, Tems"),
        ("Best Part", "Daniel Caesar, H.E.R."),
        ("Je te promets", "Johnny Hallyday"),
        ("Kiss Me", "Sixpence None the Richer"),
        ("Corazón sin cara", "Prince Royce"),
        ("Can't Help Falling in Love", "Elvis Presley"),
        ("Thinking Out Loud", "Ed Sheeran"),
    ],
    "focused": [
        ("Experience", "Ludovico Einaudi"),
        ("Time", "Hans Zimmer"),
        ("Cornfield Chase", "Hans Zimmer"),
        ("Avril 14th", "Aphex Twin"),
        ("Comptine d'un autre été", "Yann Tiersen"),
        ("Strobe", "deadmau5"),
        ("An Ending (Ascent)", "Brian Eno"),
        ("Aruarian Dance", "Nujabes"),
        ("Feather", "Nujabes"),
        ("Kiara", "Bonobo"),
        ("Says", "Nils Frahm"),
        ("River Flows in You", "Yiruma"),
    ],
    "anxious": [
        ("Breathe (In the Air)", "Pink Floyd"),
        ("Three Little Birds", "Bob Marley & The Wailers"),
        ("Don't Worry Be Happy", "Bobby McFerrin"),
        ("Let It Be", "The Beatles"),
        ("Lean on Me", "Bill Withers"),
        ("breathin", "Ariana Grande"),
        ("Keep Your Head Up", "Andy Grammer"),
        ("Saturn", "Sleeping at Last"),
        ("Put Your Records On", "Corinne Bailey Rae"),
        ("Riverside", "Agnes Obel"),
        ("Weightless", "Marconi Union"),
        ("Here Comes the Sun", "The Beatles"),
    ],
    "melancholic": [
        ("Mad World", "Gary Jules"),
        ("Creep", "Radiohead"),
        ("Nights", "Frank Ocean"),
        ("Je te laisserai des mots", "Patrick Watson"),
        ("Comme d'habitude", "Claude François"),
        ("Space Song", "Beach House"),
        ("Ivy", "Frank Ocean"),
        ("Retrograde", "James Blake"),
        ("Kyoto", "Phoebe Bridgers"),
        ("Avec le temps", "Léo Ferré"),
        ("La Bohème", "Charles Aznavour"),
        ("Lovers Rock", "TV Girl"),
    ],
    "spiritual": [
        ("Oceans (Where Feet May Fail)", "Hillsong UNITED"),
        ("Way Maker", "Sinach"),
        ("Goodness of God", "Bethel Music"),
        ("Oh Happy Day", "The Edwin Hawkins Singers"),
        ("Total Praise", "Richard Smallwood"),
        ("Never Would Have Made It", "Marvin Sapp"),
        ("Graves Into Gardens", "Elevation Worship"),
        ("Reckless Love", "Cory Asbury"),
        ("Excess Love", "Mercy Chinwo"),
        ("Amazing Grace", "Aretha Franklin"),
        ("Jesus Walks", "Kanye West"),
        ("10,000 Reasons (Bless the Lord)", "Matt Redman"),
    ],
    "party": [
        ("Calm Down", "Rema, Selena Gomez"),
        ("Gasolina", "Daddy Yankee"),
        ("Despacito", "Luis Fonsi, Daddy Yankee"),
        ("Waka Waka (This Time for Africa)", "Shakira"),
        ("I Gotta Feeling", "The Black Eyed Peas"),
        ("One Dance", "Drake"),
        ("Pookie", "Aya Nakamura"),
        ("Jerusalema", "Master KG, Nomcebo"),
        ("Unavailable", "Davido, Musa Keys"),
        ("Tití Me Preguntó", "Bad Bunny"),
        ("Lean On", "Major Lazer, DJ Snake"),
        ("Party Rock Anthem", "LMFAO"),
    ],
    "motivated": [
        ("Lose Yourself", "Eminem"),
        ("Eye of the Tiger", "Survivor"),
        ("Stronger", "Kanye West"),
        ("Till I Collapse", "Eminem"),
        ("HUMBLE.", "Kendrick Lamar"),
        ("Remember the Name", "Fort Minor"),
        ("Hall of Fame", "The Script, will.i.am"),
        ("Believer", "Imagine Dragons"),
        ("POWER", "Kanye West"),
        ("Basique", "Orelsan"),
        ("Run This Town", "JAY-Z"),
        ("Can't Be Touched", "Roy Jones Jr."),
    ],
    "lonely": [
        ("Lonely", "Akon"),
        ("Boulevard of Broken Dreams", "Green Day"),
        ("Dancing On My Own", "Robyn"),
        ("All by Myself", "Celine Dion"),
        ("Eleanor Rigby", "The Beatles"),
        ("lovely", "Billie Eilish, Khalid"),
        ("Seul", "Garou"),
        ("Self Control", "Frank Ocean"),
        ("Motion Sickness", "Phoebe Bridgers"),
        ("Linger", "The Cranberries"),
        ("Alone Again (Naturally)", "Gilbert O'Sullivan"),
        ("Ghost", "Justin Bieber"),
    ],
    "hopeful": [
        ("Rise Up", "Andra Day"),
        ("Unwritten", "Natasha Bedingfield"),
        ("Good Days", "SZA"),
        ("A Sky Full of Stars", "Coldplay"),
        ("Beautiful Day", "U2"),
        ("Je vole", "Louane"),
        ("Lovely Day", "Bill Withers"),
        ("What a Wonderful World", "Louis Armstrong"),
        ("Better Days", "OneRepublic"),
        ("Count on Me", "Bruno Mars"),
        ("Heroes", "David Bowie"),
        ("Viva la Vida", "Coldplay"),
    ],
    "homesick": [
        ("Yéké Yéké", "Mory Kanté"),
        ("Premier Gaou", "Magic System"),
        ("Pata Pata", "Miriam Makeba"),
        ("Water No Get Enemy", "Fela Kuti"),
        ("Mario", "Franco & le TPOK Jazz"),
        ("Indépendance Cha Cha", "Le Grand Kallé et l'African Jazz"),
        ("Marie-Louise", "Wendo Kolosoy"),
        ("Eloko Oyo", "Fally Ipupa"),
        ("Sweet Mother", "Prince Nico Mbarga"),
        ("Didi", "Khaled"),
        ("Zouk la sé sèl médikaman nou ni", "Kassav'"),
        ("Fall", "Davido"),
    ],
}

# Display info shared with the frontends
MOOD_EMOJI = {
    "happy": "😊", "sad": "😢", "angry": "😠", "calm": "😌",
    "energetic": "⚡", "nostalgic": "🌅", "romantic": "❤️", "focused": "🎯",
    "anxious": "😰", "melancholic": "🌧️", "spiritual": "🙏", "party": "🎉",
    "motivated": "💪", "lonely": "🌑", "hopeful": "🌟", "homesick": "🏠",
}

MOODS = list(CATALOG.keys())


def track_links(title: str, artist: str) -> dict:
    """Search links on the big streaming platforms — no API key needed."""
    query = f"{title} {artist}"
    return {
        "spotify_url": f"https://open.spotify.com/search/{quote(query)}",
        "youtube_url": f"https://www.youtube.com/results?search_query={quote_plus(query)}",
        "deezer_url": f"https://www.deezer.com/search/{quote(query)}",
    }


def make_track(title: str, artist: str, uri: str | None = None, url: str | None = None) -> dict:
    track = {"title": title, "artist": artist, "uri": uri, **track_links(title, artist)}
    if url:  # direct Spotify link when we have the real track
        track["spotify_url"] = url
    return track


def all_artists() -> dict[str, str]:
    """lowercased single artist name -> display name, for local detection."""
    out = {}
    for tracks in CATALOG.values():
        for _, artists in tracks:
            for name in artists.replace(" & ", ", ").split(", "):
                name = name.strip()
                if len(name) >= 3:
                    out[name.lower()] = name
    return out
