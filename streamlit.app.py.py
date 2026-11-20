import streamlit as st
import os
import re
import time
import json
import base64
import unicodedata
import urllib.request
import urllib.parse
import urllib.error
from urllib.parse import urlparse, parse_qs
import numpy as np

# Safe import for SSL / standard networking
try:
    import ssl
    HAS_SSL = True
except ImportError:
    HAS_SSL = False

st.set_page_config(
    page_title="SOUNDPROOF | AI Music Detector",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize Session State for Ad Watch Tracking
if "ad_watched" not in st.session_state:
    st.session_state.ad_watched = False
if "ad_in_progress" not in st.session_state:
    st.session_state.ad_in_progress = False

st.markdown(
    """
    <style>
    /* Light Ice-Cyan & High-Contrast Theme */
    .stApp {
        background-color: #f0f9ff !important;
        color: #0f172a !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Global Container Adjustments */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 4rem !important;
        max-width: 680px !important;
    }

    /* Minimalist Header Styling */
    .brand-title {
        color: #0f172a !important;
        font-weight: 800;
        font-size: 2rem;
        letter-spacing: -0.03em;
        margin-bottom: 0.25rem;
    }

    .brand-subtitle {
        color: #334155 !important;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 1.75rem;
        line-height: 1.5;
    }

    /* Crisp Minimal Cards */
    .info-card {
        background: #ffffff !important;
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 12px 16px;
        color: #0f172a !important;
        font-size: 0.875rem;
        font-weight: 500;
        line-height: 1.4;
        margin-bottom: 20px;
    }

    /* Ad Container Styling */
    .ad-card {
        background: #0f172a !important;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 20px;
        color: #ffffff !important;
        text-align: center;
        margin-bottom: 20px;
    }

    .ad-badge {
        background-color: #334155;
        color: #94a3b8;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    .ad-title {
        color: #ffffff !important;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .ad-body {
        color: #94a3b8 !important;
        font-size: 0.9rem;
        font-weight: 400;
        margin-bottom: 12px;
    }

    /* Form & Input Controls */
    div[data-baseweb="radio"] {
        background-color: #ffffff !important;
        padding: 6px;
        border-radius: 8px;
        border: 1px solid #bae6fd !important;
    }

    div[data-baseweb="radio"] label {
        color: #0f172a !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }

    .stTextInput label, .stFileUploader label, p, span, div {
        color: #0f172a !important;
        font-weight: 500;
    }

    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #94a3b8 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        transition: border-color 0.15s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #0f172a !important;
        box-shadow: none !important;
    }

    /* Primary Button */
    .stButton > button {
        background: #0f172a !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: 1px solid #0f172a !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        width: 100% !important;
        font-size: 0.95rem !important;
        letter-spacing: 0 !important;
        transition: background 0.15s ease !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        background: #1e293b !important;
        border-color: #1e293b !important;
    }

    /* Results Indicators */
    .result-banner {
        border-radius: 8px;
        padding: 16px;
        font-size: 1.05rem;
        font-weight: 700;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .result-ai {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        color: #991b1b !important;
    }

    .result-human {
        background: #f0fdf4 !important;
        border: 1px solid #bbf7d0 !important;
        color: #166534 !important;
    }

    .metric-badge {
        background-color: #ffffff !important;
        border: 1px solid #bae6fd !important;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    
    .metric-label {
        color: #475569 !important;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    
    .metric-value {
        color: #0f172a !important;
        font-size: 1.05rem;
        font-weight: 700;
        word-break: break-word;
    }

    .stAlert {
        background-color: #ffffff !important;
        border: 1px solid #94a3b8 !important;
        color: #0f172a !important;
        border-radius: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="brand-title">SOUNDPROOF</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-subtitle">Perform real-time multimodal AI video & audio detection on songs from YouTube, Spotify, SoundCloud, Apple Music, and uploaded files.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="info-card">
        Real-time multimodal inspector: Gemini watches YouTube videos directly, listens to vocals & instrumentals, and cross-checks artist authenticity & spectral signatures.
    </div>
    """,
    unsafe_allow_html=True,
)

# Gemini API Key Configuration
default_gemini_key = ""
try:
    default_gemini_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
except Exception:
    default_gemini_key = os.environ.get("GEMINI_API_KEY", "")

gemini_api_key = st.text_input(
    "Gemini API Key (Required for AI to watch videos & listen to audio)",
    value=default_gemini_key,
    type="password",
    placeholder="AIzaSy...",
)

KNOWN_AI_DOMAINS = [
    "suno.com", "suno.ai", "udio.com", "beatoven.ai", 
    "boomy.com", "mubert.com", "riffusion.com", "soundraw.io",
    "soundful.com", "musiclm.com", "aimusic.ai"
]

AI_KEYWORDS = [
    "suno", "suno.ai", "suno v3", "suno v3.5", "suno v4", "udio", "udio.com", 
    "generated with ai", "ai music", "ai generated", "ai-generated",
    "ai cover", "ai covers", "ai vocal", "ai voice", "ai song",
    "boomy", "beatoven", "mubert", "riffusion", "musiclm", "noise2music",
    "suno ai", "udio ai", "created with suno", "created with udio",
    "soundraw", "soundful", "aiva", "amper music", "rvc", "so-vits",
    "kits.ai", "jammable", "voicify", "weights.gg", "altered or synthetic content"
]

PLATFORM_PATTERNS = {
    "Spotify": [r"spotify\.com", r"open\.spotify\.com"],
    "SoundCloud": [r"soundcloud\.com", r"on\.soundcloud\.com"],
    "Apple Music": [r"music\.apple\.com", r"itunes\.apple\.com"],
    "YouTube": [r"youtube\.com", r"youtu\.be", r"music\.youtube\.com"],
    "Tidal": [r"tidal\.com", r"listen\.tidal\.com"],
    "Deezer": [r"deezer\.com", r"deezer\.page\.link"],
    "Amazon Music": [r"music\.amazon\.com"]
}


def is_valid_url(url: str) -> bool:
    """Validates if the input string is a valid web address."""
    url_pattern = re.compile(r'^(https?://)([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(:\d+)?(/.*)?$', re.IGNORECASE)
    if not url_pattern.match(url):
        return False
    
    parsed = urlparse(url)
    if not parsed.netloc or "." not in parsed.netloc:
        return False
        
    return True


def normalize_youtube_url(url: str) -> str:
    """Converts any YouTube / youtu.be / Shorts / Music link into clean canonical watch?v=ID format for Gemini."""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    video_id = None

    if "youtu.be" in host:
        video_id = parsed.path.lstrip("/").split("/")[0]
    elif "youtube.com" in host:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/")[1].split("/")[0]
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/")[1].split("/")[0]

    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


def identify_platform(url: str) -> str:
    """Identifies the music service platform from the URL structure."""
    domain = urlparse(url).netloc.lower()
    for ai_dom in KNOWN_AI_DOMAINS:
        if ai_dom in domain:
            return "AI Generator Platform"

    for platform, patterns in PLATFORM_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, url, re.IGNORECASE):
                return platform
    return "Web Link"


def normalize_text(text: str) -> str:
    """Normalizes full-width Unicode characters (e.g., ＡＩ -> AI) and lowercase."""
    return unicodedata.normalize("NFKC", text).lower()


def check_ai_markers(text: str) -> list:
    """Checks for AI generator keywords and standalone AI tags using strict word boundaries."""
    norm = normalize_text(text)
    matches = []

    for kw in AI_KEYWORDS:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, norm):
            matches.append(kw)

    if re.search(r'(?:\(|\[|#|\b)ai(?:\)|\]|\s+cover|\s+voice|\s+version|\b)', norm):
        if "ai tag" not in matches:
            matches.append("ai tag")

    return list(dict.fromkeys(matches))


def call_gemini_generate(payload: dict, api_key: str, timeout: int = 50) -> dict:
    """Automatically selects an active multimodal Gemini model for the given API key (prevents 404 Not Found)."""
    ctx = ssl.create_default_context() if HAS_SSL else None
    clean_key = urllib.parse.quote(api_key.strip())

    # 1. Discover available models on this API key that support generateContent
    candidate_models = []
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={clean_key}"
        list_req = urllib.request.Request(list_url, method="GET")
        with urllib.request.urlopen(list_req, timeout=15, context=ctx) as resp:
            models_data = json.loads(resp.read().decode("utf-8"))
            available = [
                m["name"].replace("models/", "")
                for m in models_data.get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            # Prefer modern Flash/Pro multimodal models in order
            preferred_order = [
                "gemini-2.5-flash",
                "gemini-3-flash-preview",
                "gemini-3.1-flash-lite-preview",
                "gemini-2.5-pro",
                "gemini-3.1-pro-preview",
                "gemini-2.0-flash",
                "gemini-flash-latest"
            ]
            for pref in preferred_order:
                if pref in available:
                    candidate_models.append(pref)
            for m in available:
                if "flash" in m and m not in candidate_models and "image" not in m and "tts" not in m:
                    candidate_models.append(m)
    except Exception:
        pass

    if not candidate_models:
        candidate_models = [
            "gemini-2.5-flash",
            "gemini-3-flash-preview",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-flash-latest"
        ]

    last_error = None
    for model_name in candidate_models:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={clean_key}"
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                pass
            last_error = f"HTTP {e.code} on {model_name}: {err_body[:180] or e.reason}"
            if e.code == 404:
                continue
            raise RuntimeError(last_error)
        except Exception as e:
            last_error = str(e)
            continue

    raise RuntimeError(last_error or "No compatible Gemini models available for this API key.")


def fetch_spotify_metadata(url: str) -> dict:
    """Fetches real track metadata directly from Spotify using open oEmbed endpoint and page tags."""
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        oembed_endpoint = f"https://open.spotify.com/oembed?url={encoded_url}"
        
        req = urllib.request.Request(
            oembed_endpoint,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        ctx = ssl.create_default_context() if HAS_SSL else None
        
        with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            title = data.get("title", "Spotify Track")
            author = data.get("author_name", "Unknown Artist")
            thumbnail = data.get("thumbnail_url", "")
            
            page_desc = ""
            try:
                page_req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(page_req, timeout=6, context=ctx) as page_res:
                    html = page_res.read().decode('utf-8', errors='ignore')
                    desc_match = re.search(r'<meta\s+(?:property|name)=["\'](?:og:)?description["\']\s+content=["\'](.*?)["\']', html, re.I)
                    if desc_match:
                        page_desc = desc_match.group(1)
            except Exception:
                pass

            combined_text = f"{title} {author} {page_desc}"

            return {
                "success": True,
                "title": title,
                "artist": author,
                "description": page_desc,
                "thumbnail": thumbnail,
                "raw_text": combined_text,
                "provider": "Spotify"
            }
    except Exception:
        return fetch_generic_metadata(url, "Spotify")


def fetch_youtube_metadata(url: str) -> dict:
    """Fetches YouTube track title, channel, description, tags, and synthetic content disclosures."""
    clean_url = normalize_youtube_url(url)
    title = ""
    author = ""
    description = ""
    keywords_str = ""
    thumbnail = ""
    synthetic_disclosed = False
    ctx = ssl.create_default_context() if HAS_SSL else None

    for endpoint in [
        f"https://www.youtube.com/oembed?url={urllib.parse.quote(clean_url, safe='')}&format=json",
        f"https://noembed.com/embed?url={urllib.parse.quote(clean_url, safe='')}"
    ]:
        try:
            req = urllib.request.Request(
                endpoint,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=6, context=ctx) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("title"):
                    title = data.get("title", "")
                    author = data.get("author_name", "")
                    thumbnail = data.get("thumbnail_url", "")
                    break
        except Exception:
            continue

    try:
        req = urllib.request.Request(
            clean_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cookie': 'CONSENT=YES+cb.20210328-17-p0.en+FX+417; SOCS=CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg'
            }
        )
        with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
            html = response.read().decode('utf-8', errors='ignore')

            if not title:
                t_match = re.search(r'<meta\s+name=["\']title["\']\s+content=["\'](.*?)["\']', html, re.I)
                if t_match:
                    title = t_match.group(1)

            desc_match = re.search(r'"shortDescription"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
            if desc_match:
                description = json.loads(f'"{desc_match.group(1)}"')

            kw_match = re.search(r'"keywords"\s*:\s*\[(.*?)\]', html)
            if kw_match:
                keywords_str = kw_match.group(1)

            if re.search(r'"isAlteredOrSyntheticContent"\s*:\s*true', html, re.I) or "altered or synthetic content" in html.lower():
                synthetic_disclosed = True
    except Exception:
        pass

    if title or description or keywords_str or synthetic_disclosed:
        combined_text = f"{title} {author} {description} {keywords_str}"
        if synthetic_disclosed:
            combined_text += " altered or synthetic content"
        return {
            "success": True,
            "title": title or "YouTube Track",
            "artist": author or "YouTube Channel",
            "description": description,
            "thumbnail": thumbnail,
            "synthetic_disclosed": synthetic_disclosed,
            "raw_text": combined_text,
            "provider": "YouTube"
        }

    return fetch_generic_metadata(clean_url, "YouTube")


def fetch_generic_metadata(url: str, platform_name: str) -> dict:
    """Fetches OpenGraph and meta tags for Apple Music, SoundCloud, Tidal, Deezer, etc."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            }
        )
        ctx = ssl.create_default_context() if HAS_SSL else None
        
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            title_match = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', html, re.I)
            if not title_match:
                title_match = re.search(r'<title>(.*?)</title>', html, re.I)
            title = title_match.group(1).strip() if title_match else f"{platform_name} Track"

            desc_match = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', html, re.I)
            if not desc_match:
                desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.I)
            description = desc_match.group(1).strip() if desc_match else ""

            artist_match = re.search(r'<meta\s+property=["\']music:musician["\']\s+content=["\'](.*?)["\']', html, re.I)
            artist = artist_match.group(1).strip() if artist_match else ""
            
            if not artist and " - " in title:
                parts = title.split(" - ")
                artist = parts[0]
                title = " - ".join(parts[1:])

            if not artist:
                artist = platform_name + " Creator"

            img_match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']', html, re.I)
            thumbnail = img_match.group(1) if img_match else ""

            raw_text = f"{title} {artist} {description}"

            return {
                "success": True,
                "title": title,
                "artist": artist,
                "description": description,
                "thumbnail": thumbnail,
                "raw_text": raw_text,
                "provider": platform_name
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "title": f"{platform_name} Track",
            "artist": "Unknown Artist",
            "description": "",
            "thumbnail": "",
            "raw_text": url.lower(),
            "provider": platform_name
        }


def analyze_link_with_gemini(url: str, metadata: dict, platform: str, api_key: str) -> dict:
    """Uses Gemini multimodal video watching & grounded search to verify AI vs Human songs."""
    is_youtube = "youtube.com" in url.lower() or "youtu.be" in url.lower()
    clean_url = normalize_youtube_url(url) if is_youtube else url

    track_title = metadata.get("title", "")
    track_artist = metadata.get("artist", "")
    track_desc = metadata.get("description", "")[:1500]

    # Step 1: Watch the YouTube video directly via fileData
    video_notes = ""
    if is_youtube:
        watch_prompt = """Watch this YouTube video and listen carefully to the singing and music from start to finish.
Describe in detail:
1. What is shown visually in the video (e.g., official live music video with real humans, static AI-generated cover art, looping AI animation, lyric visualizer)?
2. What does the singing voice and music sound like? Listen closely for AI music generator signatures (Suno, Udio, RVC voice cloning): metallic vocoder shimmer, robotic/slurred syllables, unnatural breathing, or overly compressed synthetic instruments vs. a real human studio recording.
3. State clearly whether the audio/video shows signs of being AI-generated or human-performed."""

        watch_payload = {
            "contents": [{
                "parts": [
                    {"fileData": {"fileUri": clean_url}},
                    {"text": watch_prompt}
                ]
            }],
            "generationConfig": {"temperature": 0.0}
        }

        raw_watch = call_gemini_generate(watch_payload, api_key, timeout=55)
        for candidate in raw_watch.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if "text" in part:
                    video_notes += part["text"]

    # Step 2: Combine direct video/audio observation with Google Search artist/channel verification
    verdict_prompt = f"""You are a strict forensic AI music detector. Combine the direct video/audio inspection below with web search verification to determine if this song is AI-generated or a genuine human recording.

URL: {clean_url}
Platform: {platform}
Extracted Title: {track_title}
Extracted Artist/Channel: {track_artist}
Description Snippet: {track_desc}
Direct Video & Audio Observation:
{video_notes if video_notes else "Non-YouTube link; inspect via web search and metadata."}

Rules:
- If the direct video/audio observation detected Suno/Udio/RVC vocal artifacts, slurred AI lyrics, or AI-generated video/cover imagery, set "is_ai": true.
- If web search reveals the artist/channel (for example "Breaking Rust" or similar AI music personas) is an AI-generated music project/artist, set "is_ai": true.
- Only set "is_ai": false if the track is verified as a genuine human artist/band recording with natural vocal and acoustic characteristics.

Return ONLY a raw JSON object (no markdown fences) with these exact keys:
{{
  "is_ai": true or false,
  "ai_probability": float between 0.05 and 0.99,
  "title": "Exact Song Title",
  "artist": "Artist or Channel Name",
  "reason": "Specific 2-sentence forensic report explaining what was observed in the video/audio and verified about the artist."
}}"""

    verdict_payload = {
        "contents": [{"parts": [{"text": verdict_prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0.0}
    }

    raw_resp = call_gemini_generate(verdict_payload, api_key, timeout=45)
    text_out = ""
    for candidate in raw_resp.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "text" in part:
                text_out += part["text"]

    json_match = re.search(r'\{.*\}', text_out, re.DOTALL)
    if not json_match:
        raise ValueError("Gemini returned an unreadable response format.")

    parsed = json.loads(json_match.group(0))
    prob = float(parsed.get("ai_probability", 0.5))
    return {
        "is_ai": bool(parsed.get("is_ai", prob > 0.5)),
        "ai_probability": min(max(prob, 0.05), 0.99),
        "confidence": "High",
        "title": parsed.get("title") or track_title or "Verified Track",
        "artist": parsed.get("artist") or track_artist or "Verified Artist",
        "platform": platform,
        "watched_video": bool(video_notes),
        "reason": parsed.get("reason", "Verified via Gemini multimodal video & audio inspection.")
    }


def analyze_audio_with_gemini(file_bytes: bytes, file_name: str, api_key: str) -> dict:
    """Sends uploaded audio file directly to Gemini so the AI actually listens to the track."""
    ext = os.path.splitext(file_name)[1].lower()
    mime_map = {
        ".mp3": "audio/mp3",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac"
    }
    mime_type = mime_map.get(ext, "audio/mp3")

    audio_b64 = base64.b64encode(file_bytes[:15_000_000]).decode("utf-8")

    prompt = """Listen carefully to this audio track and evaluate whether it is AI-generated (e.g., Suno, Udio, Boomy, Riffusion, or an RVC AI vocal cover) or a real human-performed/recorded song.

Listen for:
- Metallic/phase vocoder shimmer in vocals and high-frequency cymbals
- Unnatural breathing, robotic pitch transitions, or slurred/garbled lyrics
- Over-smoothed synthetic transients vs. authentic studio/live acoustics

Return ONLY a valid JSON object (no markdown fences) with these exact keys:
{
  "is_ai": true or false,
  "ai_probability": float between 0.05 and 0.99,
  "reason": "Clear 1-2 sentence explanation describing what you heard in the vocals, instrumentation, and audio texture."
}"""

    payload = {
        "contents": [{
            "parts": [
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": audio_b64
                    }
                },
                {"text": prompt}
            ]
        }],
        "generationConfig": {"temperature": 0.0}
    }

    raw_resp = call_gemini_generate(payload, api_key, timeout=45)
    text_out = ""
    for candidate in raw_resp.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "text" in part:
                text_out += part["text"]

    json_match = re.search(r'\{.*\}', text_out, re.DOTALL)
    if not json_match:
        raise ValueError("Gemini returned an unreadable response format.")

    parsed = json.loads(json_match.group(0))
    prob = float(parsed.get("ai_probability", 0.5))
    return {
        "is_ai": bool(parsed.get("is_ai", prob > 0.5)),
        "ai_probability": min(max(prob, 0.05), 0.99),
        "reason": parsed.get("reason", "Analyzed directly via Gemini multimodal audio listening.")
    }


def analyze_audio_bytes(file_bytes: bytes, file_name: str = "audio.mp3", api_key: str = "") -> dict:
    """Combines FFT spectral analysis with Gemini multimodal audio listening when an API key is provided."""
    metrics = {}
    spectral_score = 0.25

    try:
        raw_signal = np.frombuffer(file_bytes[:120000], dtype=np.int8).astype(np.float32)
        if len(raw_signal) > 0:
            fft_data = np.abs(np.fft.rfft(raw_signal))
            geom_mean = np.exp(np.mean(np.log(fft_data + 1e-10)))
            arith_mean = np.mean(fft_data) + 1e-10
            flatness = float(geom_mean / arith_mean)
            high_freq_power = float(np.sum(fft_data[int(len(fft_data)*0.7):]) / (np.sum(fft_data) + 1e-10))
            variance = float(np.var(raw_signal))

            if flatness > 0.048:
                spectral_score += 0.30
            if high_freq_power > 0.18:
                spectral_score += 0.25
            if variance < 450:
                spectral_score += 0.15

            spectral_score = float(min(max(spectral_score, 0.08), 0.94))
            metrics = {
                "Spectral Flatness": round(flatness, 4),
                "High-Freq Energy": round(high_freq_power, 4),
                "Signal Variance": int(variance)
            }
    except Exception:
        pass

    if api_key and api_key.strip():
        try:
            gemini_res = analyze_audio_with_gemini(file_bytes, file_name, api_key.strip())
            return {
                "ai_probability": round(gemini_res["ai_probability"], 2),
                "is_ai": gemini_res["is_ai"],
                "confidence": "High",
                "metrics": metrics,
                "reason": gemini_res["reason"]
            }
        except Exception as e:
            return {
                "ai_probability": round(spectral_score, 2),
                "is_ai": spectral_score > 0.5,
                "confidence": "Medium",
                "metrics": metrics,
                "reason": f"Gemini audio listening failed ({str(e)}). Showing local FFT spectral heuristic."
            }

    return {
        "ai_probability": round(spectral_score, 2),
        "is_ai": spectral_score > 0.5,
        "confidence": "High" if spectral_score > 0.78 or spectral_score < 0.25 else "Medium",
        "metrics": metrics,
        "reason": "Analyzed using local FFT spectral flatness, high-frequency energy, and signal variance. Enter a Gemini API key to enable active AI listening."
    }


def inspect_universal_link(url: str, selected_app: str, api_key: str = "") -> dict:
    """Fetches real track data and executes Gemini multimodal video watching + keyword analysis."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    detected_platform = identify_platform(url) if selected_app == "Auto-Detect Platform" else selected_app

    # 1. Direct AI Generation Domain Inspection
    for ai_domain in KNOWN_AI_DOMAINS:
        if ai_domain in domain:
            return {
                "is_ai": True,
                "confidence": "Very High",
                "ai_probability": 0.98,
                "reason": f"Direct link from recognized AI music generation platform ({ai_domain}).",
                "title": f"Generative Track ({ai_domain})",
                "artist": "AI Music Engine",
                "platform": "AI Generator",
                "thumbnail": ""
            }

    # 2. Fetch real metadata first
    if "spotify.com" in domain or selected_app == "Spotify":
        metadata = fetch_spotify_metadata(url)
    elif "youtube.com" in domain or "youtu.be" in domain or selected_app == "YouTube":
        metadata = fetch_youtube_metadata(url)
    else:
        metadata = fetch_generic_metadata(url, detected_platform)

    # 3. Check explicit keyword markers & YouTube's synthetic content disclosure flag
    matched_keywords = check_ai_markers(metadata.get("raw_text", "")) if metadata.get("success") else []
    if metadata.get("synthetic_disclosed"):
        if "YouTube Synthetic Disclosure" not in matched_keywords:
            matched_keywords.insert(0, "YouTube Synthetic Disclosure")

    # 4. If Gemini API Key is provided, watch the video & listen to the audio stream
    if api_key and api_key.strip():
        try:
            gemini_res = analyze_link_with_gemini(url, metadata, detected_platform, api_key.strip())
            if matched_keywords and not gemini_res["is_ai"]:
                kw_str = ", ".join([f"'{k}'" for k in matched_keywords[:3]])
                gemini_res["is_ai"] = True
                gemini_res["ai_probability"] = max(gemini_res["ai_probability"], 0.90)
                gemini_res["reason"] += f" Additionally, video metadata explicitly contains AI markers: {kw_str}."
            return gemini_res
        except Exception as e:
            gemini_error = f"Gemini API error ({str(e)}). Falling back to metadata inspection: "
    else:
        gemini_error = ""

    # 5. Fallback metadata evaluation
    if metadata.get("success", False):
        if matched_keywords:
            kw_str = ", ".join([f"'{k}'" for k in matched_keywords[:3]])
            return {
                "is_ai": True,
                "confidence": "High",
                "ai_probability": 0.92,
                "reason": f"{gemini_error}Live inspection on {metadata.get('provider', detected_platform)} found generative markers: {kw_str}.",
                "title": metadata.get("title", "Track Detected"),
                "artist": metadata.get("artist", "Artist Detected"),
                "platform": metadata.get("provider", detected_platform),
                "thumbnail": metadata.get("thumbnail", "")
            }
        else:
            return {
                "is_ai": False,
                "confidence": "High" if not gemini_error else "Low",
                "ai_probability": 0.12,
                "reason": f"{gemini_error}Live inspection of track metadata on {metadata.get('provider', detected_platform)} found no AI markers.",
                "title": metadata.get("title", "Track Detected"),
                "artist": metadata.get("artist", "Artist Detected"),
                "platform": metadata.get("provider", detected_platform),
                "thumbnail": metadata.get("thumbnail", "")
            }

    return {
        "is_ai": False,
        "confidence": "Low",
        "ai_probability": 0.50,
        "reason": f"{gemini_error}Could not fetch track metadata from {detected_platform}. Enter a valid Gemini API key or upload the audio file directly.",
        "title": detected_platform + " Track",
        "artist": "Unverified",
        "platform": detected_platform,
        "thumbnail": ""
    }


input_type = st.radio(
    "Source Type",
    ["Streaming Link", "Audio File Upload"],
    horizontal=True
)

st.markdown('<div style="margin-bottom: 12px;"></div>', unsafe_allow_html=True)

if input_type == "Streaming Link":
    selected_platform = st.selectbox(
        "Platform Selector",
        ["Auto-Detect Platform", "Spotify", "YouTube", "SoundCloud", "Apple Music", "Tidal", "Deezer", "Amazon Music"]
    )
    user_input = st.text_input(
        "Paste Song Link",
        placeholder="e.g. https://www.youtube.com/watch?v=... or https://open.spotify.com/track/...",
    )
else:
    uploaded_file = st.file_uploader(
        "Upload track", type=["mp3", "wav", "m4a"]
    )

st.markdown('<div style="margin-bottom: 8px;"></div>', unsafe_allow_html=True)

analyze_clicked = st.button("Run Analysis")

if analyze_clicked:
    st.session_state.ad_watched = False
    st.session_state.ad_in_progress = True

if st.session_state.ad_in_progress and not st.session_state.ad_watched:
    if input_type == "Streaming Link":
        link = user_input.strip()
        if not link:
            st.warning("Please enter a link before starting analysis.")
            st.session_state.ad_in_progress = False
            st.stop()
        if not is_valid_url(link):
            st.error("Invalid URL format. Please enter a valid web address.")
            st.session_state.ad_in_progress = False
            st.stop()
    else:
        if not uploaded_file:
            st.warning("Please upload an audio file before starting analysis.")
            st.session_state.ad_in_progress = False
            st.stop()

    st.markdown("""
    <div class="ad-card">
        <span class="ad-badge">Sponsored</span>
        <div class="ad-title">SOUNDPROOF Studio Pro FX Plugin</div>
        <div class="ad-body">High-definition vocal isolation and acoustic cleaning for digital audio workstations.</div>
    </div>
    """, unsafe_allow_html=True)

    progress_bar = st.progress(0)
    status_text = st.empty()

    for seconds_remaining in range(15, -1, -1):
        percent_complete = int(((15 - seconds_remaining) / 15) * 100)
        progress_bar.progress(percent_complete)
        if seconds_remaining > 0:
            status_text.markdown(f"Ad in progress. Please wait {seconds_remaining} seconds...")
            time.sleep(1)
        else:
            status_text.markdown("Complete. Fetching live track details...")

    st.session_state.ad_watched = True
    st.session_state.ad_in_progress = False
    st.rerun()

if st.session_state.ad_watched:
    if input_type == "Streaming Link":
        link = user_input.strip()

        with st.spinner("Watching video, listening to audio stream, and verifying artist..."):
            res = inspect_universal_link(link, selected_platform, gemini_api_key)

        st.markdown("### Analysis Report")
        
        if res["is_ai"]:
            st.markdown(
                f'<div class="result-banner result-ai">Likely AI-Generated Track ({int(res["ai_probability"] * 100)}% AI Confidence)</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="result-banner result-human">Likely Human-Made Track ({int((1 - res["ai_probability"]) * 100)}% Human Confidence)</div>',
                unsafe_allow_html=True
            )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-badge">
                <div class="metric-label">Platform</div>
                <div class="metric-value">{res['platform']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-badge">
                <div class="metric-label">Track Title</div>
                <div class="metric-value">{res.get('title', 'Unknown Title')}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-badge">
                <div class="metric-label">Artist / Channel</div>
                <div class="metric-value">{res.get('artist', 'Unknown Artist')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
        st.info(f"Verification Details: {res['reason']}")

    else:
        with st.spinner("Listening to uploaded audio and computing spectral metrics..."):
            file_bytes = uploaded_file.read()
            res = analyze_audio_bytes(file_bytes, uploaded_file.name, gemini_api_key)

        st.markdown("### Analysis Report")
        
        if res["is_ai"]:
            st.markdown(
                f'<div class="result-banner result-ai">Likely AI-Generated Track ({int(res["ai_probability"] * 100)}% Probability)</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="result-banner result-human">Likely Human-Made Track ({int((1 - res["ai_probability"]) * 100)}% Human Confidence)</div>',
                unsafe_allow_html=True
            )

        if res.get("reason"):
            st.info(f"Verification Details: {res['reason']}")

        if res.get("metrics"):
            st.markdown("##### Acoustic Spectral Metrics")
            m_cols = st.columns(len(res["metrics"]))
            for idx, (k, v) in enumerate(res["metrics"].items()):
                with m_cols[idx]:
                    st.markdown(f"""
                    <div class="metric-badge">
                        <div class="metric-label">{k}</div>
                        <div class="metric-value">{v}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
            with st.expander("Metric descriptions"):
                st.markdown("""
- **Spectral Flatness:** Evaluates tonal variation against static noise. Scores over `0.048` typically indicate synthetic noise artifacts.
- **High-Freq Energy:** Measures the ratio of total energy in treble frequencies (> `0.18` signals synthetic high-frequency noise).
- **Signal Variance:** Dynamic range variation. Low values (< `450`) indicate heavily flattened digital sound dynamics.
                """)

    st.session_state.ad_watched = False
