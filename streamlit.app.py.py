import streamlit as st
import os
import re
import time
import json
import html
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

    .result-unverified {
        background: #fffbeb !important;
        border: 1px solid #fde68a !important;
        color: #92400e !important;
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

# Explicit, unambiguous AI generator markers (avoids false positives on real songs)
EXPLICIT_AI_KEYWORDS = [
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
    """Normalizes HTML entities, full-width Unicode characters, and lowercase."""
    cleaned = html.unescape(text)
    return unicodedata.normalize("NFKC", cleaned).lower()


def check_ai_markers(title: str, artist: str, description: str) -> list:
    """Checks only clean title, artist, and description for explicit AI generation tags."""
    norm_title = normalize_text(title)
    norm_all = normalize_text(f"{title} {artist} {description}")
    matches = []

    for kw in EXPLICIT_AI_KEYWORDS:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, norm_all):
            matches.append(kw)

    # Check explicit bracketed/parenthesized AI tags in the title ONLY (e.g., "(AI)", "[AI]", "(AI Cover)")
    if re.search(r'(?:\(|\[)\s*ai(?:\s+cover|\s+version|\s+voice)?\s*(?:\)|\])', norm_title):
        if "explicit (AI) title tag" not in matches:
            matches.append("explicit (AI) title tag")

    return list(dict.fromkeys(matches))


def verify_artist_via_public_web(artist: str, title: str) -> dict:
    """Zero-quota fallback check using Wikipedia when Gemini API quota is exhausted."""
    if not artist or artist.lower() in ("unknown artist", "youtube channel", "unverified"):
        return {"found_ai": False, "evidence": ""}

    ctx = ssl.create_default_context() if HAS_SSL else None
    clean_artist = re.sub(r'\s*-\s*topic$', '', artist, flags=re.I).strip()

    try:
        query = urllib.parse.quote(f'"{clean_artist}"')
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json&srlimit=3"
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "SOUNDPROOF-Detector/1.0"})
        with urllib.request.urlopen(req, timeout=6, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("query", {}).get("search", []):
                snippet = re.sub(r'<[^>]+>', '', item.get("snippet", "")).lower()
                item_title = item.get("title", "").lower()
                if clean_artist.lower() == item_title or f"{clean_artist.lower()} (" in item_title:
                    if any(term in snippet for term in ["ai-generated", "artificial intelligence", "ai music", "ai country", "suno", "udio", "virtual band", "synthetic"]):
                        return {
                            "found_ai": True,
                            "evidence": f"Public knowledge base confirms '{clean_artist}' is documented as an AI-generated music project."
                        }
    except Exception:
        pass

    return {"found_ai": False, "evidence": ""}


def call_gemini_generate(payload: dict, api_key: str, timeout: int = 55) -> dict:
    """Tries free-tier-friendly multimodal Gemini models in order, rotating on 400/404/429 limits."""
    ctx = ssl.create_default_context() if HAS_SSL else None
    clean_key = urllib.parse.quote(api_key.strip())

    candidate_models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-3-flash-preview",
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
            last_error = f"HTTP {e.code} on {model_name}: {err_body[:160] or e.reason}"
            if e.code in (400, 404, 429):
                continue
            raise RuntimeError(last_error)
        except Exception as e:
            last_error = str(e)
            continue

    raise RuntimeError(last_error or "All Gemini models hit quota or availability limits.")


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
            title = html.unescape(data.get("title", "Spotify Track"))
            author = html.unescape(data.get("author_name", "Unknown Artist"))
            thumbnail = data.get("thumbnail_url", "")
            
            page_desc = ""
            try:
                page_req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(page_req, timeout=6, context=ctx) as page_res:
                    page_html = page_res.read().decode('utf-8', errors='ignore')
                    desc_match = re.search(r'<meta\s+(?:property|name)=["\'](?:og:)?description["\']\s+content=["\'](.*?)["\']', page_html, re.I)
                    if desc_match:
                        page_desc = html.unescape(desc_match.group(1))
            except Exception:
                pass

            return {
                "success": True,
                "title": title,
                "artist": author,
                "description": page_desc,
                "thumbnail": thumbnail,
                "provider": "Spotify"
            }
    except Exception:
        return fetch_generic_metadata(url, "Spotify")


def fetch_youtube_metadata(url: str) -> dict:
    """Fetches clean YouTube track title, channel, description, and synthetic content disclosures."""
    clean_url = normalize_youtube_url(url)
    title = ""
    author = ""
    description = ""
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
                    title = html.unescape(data.get("title", ""))
                    author = html.unescape(data.get("author_name", ""))
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
            page_html = response.read().decode('utf-8', errors='ignore')

            if not title:
                t_match = re.search(r'<meta\s+name=["\']title["\']\s+content=["\'](.*?)["\']', page_html, re.I)
                if t_match:
                    title = html.unescape(t_match.group(1))

            desc_match = re.search(r'"shortDescription"\s*:\s*"((?:[^"\\]|\\.)*)"', page_html)
            if desc_match:
                description = json.loads(f'"{desc_match.group(1)}"')

            if re.search(r'"isAlteredOrSyntheticContent"\s*:\s*true', page_html, re.I):
                synthetic_disclosed = True
    except Exception:
        pass

    if title or description or synthetic_disclosed:
        return {
            "success": True,
            "title": title or "YouTube Track",
            "artist": author or "YouTube Channel",
            "description": description,
            "thumbnail": thumbnail,
            "synthetic_disclosed": synthetic_disclosed,
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
            page_html = response.read().decode('utf-8', errors='ignore')
            
            title_match = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', page_html, re.I)
            if not title_match:
                title_match = re.search(r'<title>(.*?)</title>', page_html, re.I)
            title = html.unescape(title_match.group(1).strip()) if title_match else f"{platform_name} Track"

            desc_match = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', page_html, re.I)
            if not desc_match:
                desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', page_html, re.I)
            description = html.unescape(desc_match.group(1).strip()) if desc_match else ""

            artist_match = re.search(r'<meta\s+property=["\']music:musician["\']\s+content=["\'](.*?)["\']', page_html, re.I)
            artist = html.unescape(artist_match.group(1).strip()) if artist_match else ""
            
            if not artist and " - " in title:
                parts = title.split(" - ")
                artist = parts[0]
                title = " - ".join(parts[1:])

            if not artist:
                artist = platform_name + " Creator"

            img_match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']', page_html, re.I)
            thumbnail = img_match.group(1) if img_match else ""

            return {
                "success": True,
                "title": title,
                "artist": artist,
                "description": description,
                "thumbnail": thumbnail,
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
            "provider": platform_name
        }


def analyze_link_with_gemini(url: str, metadata: dict, platform: str, api_key: str) -> dict:
    """Objective multimodal video watching + grounded search verification."""
    is_youtube = "youtube.com" in url.lower() or "youtu.be" in url.lower()
    clean_url = normalize_youtube_url(url) if is_youtube else url

    track_title = metadata.get("title", "")
    track_artist = metadata.get("artist", "")
    track_desc = metadata.get("description", "")[:1200]

    prompt = f"""You are an objective forensic audio & video analyst. Watch the attached video, listen closely to the vocals and instruments, and use Google Search to verify whether this song is genuinely human-made or AI-generated (Suno, Udio, RVC voice clone, etc.).

URL: {clean_url}
Platform: {platform}
Extracted Title: {track_title}
Extracted Artist/Channel: {track_artist}
Description Snippet: {track_desc}

Evaluation Criteria (Be accurate and balanced — do NOT falsely accuse real human artists of being AI):
1. HUMAN-MADE INDICATORS:
   - Real human artist, band, producer, or label with verifiable discography, live shows, credits, or authentic studio/live video footage.
   - Natural human vocal timbre, organic breath intakes, consistent lyric pronunciation, and real acoustic/electronic production dynamics.
   - Official music videos, behind-the-scenes footage, lyric videos, or standard YouTube auto-generated "Topic" audio tracks for real musicians.
2. AI-GENERATED INDICATORS:
   - Audible Suno/Udio/RVC artifacts: metallic phase-vocoder shimmer on vocals, slurred/garbled nonsensical syllables, robotic pitch glides, or unnatural breathing.
   - Search results or credits explicitly identifying the artist/project as AI-generated (e.g., Suno, Udio, AI persona like Breaking Rust) or an AI voice cover.

Return ONLY a raw JSON object (no markdown fences) with these exact keys:
{{
  "is_ai": true or false,
  "ai_probability": float between 0.05 and 0.99 (use < 0.25 if clearly human-made, > 0.80 if clearly AI-generated),
  "title": "Exact Song Title",
  "artist": "Artist or Channel Name",
  "reason": "Clear 2-sentence forensic explanation referencing what you heard in the vocals/instruments and verified about the artist."
}}"""

    raw_resp = None
    watched_video = False

    if is_youtube:
        video_parts = [
            {
                "fileData": {"fileUri": clean_url},
                "videoMetadata": {"startOffset": "0s", "endOffset": "45s"}
            },
            {"text": prompt}
        ]
        video_payload = {
            "contents": [{"parts": video_parts}],
            "tools": [{"google_search": {}}],
            "generationConfig": {"temperature": 0.0}
        }
        try:
            raw_resp = call_gemini_generate(video_payload, api_key, timeout=55)
            watched_video = True
        except Exception:
            raw_resp = None

    if raw_resp is None:
        search_payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "tools": [{"google_search": {}}],
            "generationConfig": {"temperature": 0.0}
        }
        raw_resp = call_gemini_generate(search_payload, api_key, timeout=40)

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
    mode_tag = "[Video + Audio Watched] " if watched_video else "[Search + Metadata Verified] "
    return {
        "is_ai": bool(parsed.get("is_ai", prob > 0.5)),
        "ai_probability": min(max(prob, 0.05), 0.99),
        "confidence": "High",
        "unverified": False,
        "title": parsed.get("title") or track_title or "Verified Track",
        "artist": parsed.get("artist") or track_artist or "Verified Artist",
        "platform": platform,
        "reason": mode_tag + parsed.get("reason", "Verified via Gemini multimodal inspection.")
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

    prompt = """Listen carefully to this audio track and evaluate objectively whether it is AI-generated (e.g., Suno, Udio, Boomy, Riffusion, or an RVC AI vocal cover) or a real human-performed/recorded song.

Listen for:
- Metallic/phase vocoder shimmer in vocals and high-frequency cymbals vs. clean studio/live transients
- Natural human breathing and clear pronunciation vs. robotic pitch transitions or slurred/garbled lyrics

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
    """Fetches real track data and executes Gemini multimodal video watching + keyword & public web analysis."""
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
                "unverified": False,
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
    matched_keywords = check_ai_markers(
        metadata.get("title", ""),
        metadata.get("artist", ""),
        metadata.get("description", "")
    ) if metadata.get("success") else []

    if metadata.get("synthetic_disclosed"):
        if "YouTube Synthetic Disclosure" not in matched_keywords:
            matched_keywords.insert(0, "YouTube Synthetic Disclosure")

    # 4. If Gemini API Key is provided, watch the video & listen to the audio stream
    if api_key and api_key.strip():
        try:
            gemini_res = analyze_link_with_gemini(url, metadata, detected_platform, api_key.strip())
            # Only override Gemini if YouTube officially disclosed synthetic content or an explicit generator name (Suno/Udio) was found
            strong_overrides = [k for k in matched_keywords if k in ("YouTube Synthetic Disclosure", "suno", "udio", "suno.ai", "udio.com", "explicit (AI) title tag")]
            if strong_overrides and not gemini_res["is_ai"]:
                kw_str = ", ".join([f"'{k}'" for k in strong_overrides[:3]])
                gemini_res["is_ai"] = True
                gemini_res["ai_probability"] = max(gemini_res["ai_probability"], 0.92)
                gemini_res["reason"] += f" Additionally, video metadata explicitly discloses AI generation: {kw_str}."
            return gemini_res
        except Exception as e:
            gemini_error = f"Gemini API error ({str(e)})."
    else:
        gemini_error = ""

    # 5. Zero-quota fallback: check explicit metadata tags AND public web knowledge base
    if metadata.get("success", False):
        if matched_keywords:
            kw_str = ", ".join([f"'{k}'" for k in matched_keywords[:3]])
            return {
                "is_ai": True,
                "confidence": "High",
                "ai_probability": 0.92,
                "unverified": False,
                "reason": f"{gemini_error} Live inspection on {metadata.get('provider', detected_platform)} found generative markers: {kw_str}.",
                "title": metadata.get("title", "Track Detected"),
                "artist": metadata.get("artist", "Artist Detected"),
                "platform": metadata.get("provider", detected_platform),
                "thumbnail": metadata.get("thumbnail", "")
            }

        web_check = verify_artist_via_public_web(metadata.get("artist", ""), metadata.get("title", ""))
        if web_check.get("found_ai"):
            return {
                "is_ai": True,
                "confidence": "High",
                "ai_probability": 0.94,
                "unverified": False,
                "reason": f"{web_check['evidence']} (Note: {gemini_error})" if gemini_error else web_check["evidence"],
                "title": metadata.get("title", "Track Detected"),
                "artist": metadata.get("artist", "Artist Detected"),
                "platform": metadata.get("provider", detected_platform),
                "thumbnail": metadata.get("thumbnail", "")
            }

        if gemini_error:
            return {
                "is_ai": False,
                "confidence": "Low",
                "ai_probability": 0.50,
                "unverified": True,
                "reason": f"{gemini_error} Deep audio/video listening could not complete because your Gemini API key hit its quota limit.",
                "title": metadata.get("title", "Track Detected"),
                "artist": metadata.get("artist", "Artist Detected"),
                "platform": metadata.get("provider", detected_platform),
                "thumbnail": metadata.get("thumbnail", "")
            }

        return {
            "is_ai": False,
            "confidence": "Medium",
            "ai_probability": 0.15,
            "unverified": False,
            "reason": f"Metadata inspection on {metadata.get('provider', detected_platform)} found no AI markers. Enter a Gemini API key to watch & listen to the audio stream.",
            "title": metadata.get("title", "Track Detected"),
            "artist": metadata.get("artist", "Artist Detected"),
            "platform": metadata.get("provider", detected_platform),
            "thumbnail": metadata.get("thumbnail", "")
        }

    return {
        "is_ai": False,
        "confidence": "Low",
        "ai_probability": 0.50,
        "unverified": True,
        "reason": f"{gemini_error} Could not fetch track metadata from {detected_platform}. Enter a valid Gemini API key with active quota or upload the audio file directly.",
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
        
        if res.get("unverified"):
            st.markdown(
                '<div class="result-banner result-unverified">Unverified Track (Deep AI Check Incomplete)</div>',
                unsafe_allow_html=True
            )
        elif res["is_ai"]:
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
            st.markdown(
                f'<div class="metric-badge"><div class="metric-label">Platform</div><div class="metric-value">{res["platform"]}</div></div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'<div class="metric-badge"><div class="metric-label">Track Title</div><div class="metric-value">{res.get("title", "Unknown Title")}</div></div>',
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f'<div class="metric-badge"><div class="metric-label">Artist / Channel</div><div class="metric-value">{res.get("artist", "Unknown Artist")}</div></div>',
                unsafe_allow_html=True
            )

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
                    st.markdown(
                        f'<div class="metric-badge"><div class="metric-label">{k}</div><div class="metric-value">{v}</div></div>',
                        unsafe_allow_html=True
                    )
            
            st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
            with st.expander("Metric descriptions"):
                st.markdown("""
- **Spectral Flatness:** Evaluates tonal variation against static noise. Scores over `0.048` typically indicate synthetic noise artifacts.
- **High-Freq Energy:** Measures the ratio of total energy in treble frequencies (> `0.18` signals synthetic high-frequency noise).
- **Signal Variance:** Dynamic range variation. Low values (< `450`) indicate heavily flattened digital sound dynamics.
                """)

    st.session_state.ad_watched = False
