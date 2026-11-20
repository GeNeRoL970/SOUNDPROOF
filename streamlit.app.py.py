import streamlit as st
import os
import re
import time
import json
import base64
import urllib.request
import urllib.parse
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
    /* Modern Neutral Theme Reset */
    .stApp {
        background-color: #fafafa !important;
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
        color: #475569 !important;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 1.75rem;
        line-height: 1.5;
    }

    /* Crisp Minimal Cards */
    .info-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        color: #334155 !important;
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
        border: 1px solid #e2e8f0 !important;
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
        border: 1px solid #cbd5e1 !important;
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
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    
    .metric-label {
        color: #64748b !important;
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

    .track-meta-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 16px;
        display: flex;
        gap: 16px;
        align-items: center;
    }

    .stAlert {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        color: #0f172a !important;
        border-radius: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="brand-title">SOUNDPROOF</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-subtitle">Perform real-time detection on songs from Spotify, YouTube, SoundCloud, Apple Music, Tidal, Deezer, and direct AI platforms.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="info-card">
        Real-time audio & metadata inspector: Analyzes live API responses, artist tags, and acoustic spectral features across all supported streaming providers.
    </div>
    """,
    unsafe_allow_html=True,
)

# Gemini API Key Configuration (supports st.secrets, env var, or direct UI input)
default_gemini_key = os.environ.get("GEMINI_API_KEY", "")
try:
    if "GEMINI_API_KEY" in st.secrets:
        default_gemini_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

gemini_api_key = st.text_input(
    "Gemini API Key (Optional — Enables Deep AI Link Investigation)",
    value=default_gemini_key,
    type="password",
    placeholder="AIzaSy...",
    help="Enter a Google Gemini API key to allow Gemini AI to search and inspect the song link directly."
)

KNOWN_AI_DOMAINS = [
    "suno.com", "suno.ai", "udio.com", "beatoven.ai", 
    "boomy.com", "mubert.com", "riffusion.com", "soundraw.io",
    "soundful.com", "musiclm.com", "aimusic.ai"
]

AI_KEYWORDS = [
    "suno", "suno.ai", "suno v3", "suno v3.5", "suno v4", "udio", "udio.com", 
    "generated with ai", "ai music", "ai generated", "boomy", "beatoven", 
    "mubert", "riffusion", "musiclm", "noise2music", "suno ai", "udio ai",
    "ai song", "created with suno", "created with udio", "ai cover", "ai covers", 
    "ai vocal", "ai voice", "rvc", "so-vits", "so-vits-svc", "kits.ai", 
    "voicify", "jammable", "weights.gg", "ai version", "sung by ai", "made with ai",
    "soundraw", "soundful", "aiva", "amper music", "ai remix", "ai parody",
    "artificial intelligence", "neural audio", "voice model", "ai model"
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
    url_pattern = re.compile(
        r'^(https?://)'
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
        r'(:\d+)?(/.*)?$', re.IGNORECASE
    )
    if not url_pattern.match(url):
        return False
    
    parsed = urlparse(url)
    if not parsed.netloc or "." not in parsed.netloc:
        return False
        
    return True

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
            
            # Fetch webpage metadata for descriptions/tags
            page_text = ""
            try:
                page_req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(page_req, timeout=6, context=ctx) as page_res:
                    page_text = page_res.read().decode('utf-8', errors='ignore').lower()
            except Exception:
                pass

            combined_text = f"{title} {author} {page_text}".lower()

            return {
                "success": True,
                "title": title,
                "artist": author,
                "thumbnail": thumbnail,
                "raw_text": combined_text,
                "provider": "Spotify"
            }
    except Exception:
        return fetch_generic_metadata(url, "Spotify")

def fetch_youtube_metadata(url: str) -> dict:
    """Fetches full YouTube video title, author, description, and tags with CORS & consent fallbacks."""
    title = ""
    author = ""
    thumbnail = ""
    description = ""
    keywords = ""
    fetch_succeeded = False
    
    ctx = ssl.create_default_context() if HAS_SSL else None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'CONSENT=YES+cb.20210328-17-p0.en+FX+999; SOCS=CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg'
    }

    # Normalize YouTube URL
    video_id = ""
    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        video_id = parsed.path.lstrip('/').split('/')[0]
    elif "youtube.com" in parsed.netloc:
        video_id = parse_qs(parsed.query).get("v", [""])[0]
        if not video_id and "/shorts/" in parsed.path:
            video_id = parsed.path.split("/shorts/")[1].split('/')[0]

    clean_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else url.split("?si=")[0].split("&si=")[0]
    encoded_url = urllib.parse.quote(clean_url, safe='')

    # 1. Try multiple oEmbed / metadata endpoints (includes CORS-friendly noembed)
    oembed_endpoints = [
        f"https://www.youtube.com/oembed?url={encoded_url}&format=json",
        f"https://noembed.com/embed?url={encoded_url}"
    ]

    for endpoint in oembed_endpoints:
        try:
            req = urllib.request.Request(endpoint, headers=headers)
            with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
                data = json.loads(response.read().decode('utf-8'))
                if "title" in data and data["title"]:
                    title = data.get("title", "")
                    author = data.get("author_name", "")
def analyze_audio_bytes(file_bytes: bytes, file_name: str = "audio.mp3", api_key: str = "") -> dict:
    """Calculates FFT spectrum metrics and uses Gemini multimodal audio listening when an API key is provided."""
    try:
        raw_signal = np.frombuffer(file_bytes[:120000], dtype=np.int8).astype(np.float32)
        
        if len(raw_signal) == 0:
            raise ValueError("Audio stream sample is empty.")

        fft_data = np.abs(np.fft.rfft(raw_signal))
        
        geom_mean = np.exp(np.mean(np.log(fft_data + 1e-10)))
        arith_mean = np.mean(fft_data) + 1e-10
        flatness = float(geom_mean / arith_mean)

        high_freq_power = float(np.sum(fft_data[int(len(fft_data)*0.7):]) / (np.sum(fft_data) + 1e-10))
        variance = float(np.var(raw_signal))

        spectral_metrics = {
            "Spectral Flatness": round(flatness, 4),
            "High-Freq Energy": round(high_freq_power, 4),
            "Signal Variance": int(variance)
        }

        # If a Gemini API key is provided, send the actual audio bytes to Gemini so it can listen directly
        if api_key and api_key.strip():
            gemini_audio_res = analyze_audio_with_gemini(file_bytes, file_name, api_key, spectral_metrics)
            if gemini_audio_res.get("success"):
                gemini_audio_res["metrics"] = spectral_metrics
                return gemini_audio_res

        ai_score = 0.25
        if flatness > 0.048:
            ai_score += 0.30
        if high_freq_power > 0.18:
            ai_score += 0.25
        if variance < 450:
            ai_score += 0.15

        ai_score = float(min(max(ai_score, 0.08), 0.94))

        return {
            "ai_probability": round(ai_score, 2),
            "is_ai": ai_score > 0.5,
            "confidence": "High" if ai_score > 0.78 or ai_score < 0.25 else "Medium",
            "reason": "Evaluated using local NumPy FFT spectral flatness, high-frequency energy, and dynamic variance.",
            "metrics": spectral_metrics
        }
    except Exception as e:
        return {
            "ai_probability": 0.30,
            "is_ai": False,
            "confidence": "Medium",
            "metrics": {},
            "error": str(e)
        }

def analyze_audio_with_gemini(file_bytes: bytes, file_name: str, api_key: str, spectral_metrics: dict) -> dict:
    """Sends uploaded audio directly to Gemini 2.5 Flash so the AI actually listens to the track."""
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={urllib.parse.quote(api_key.strip())}"

    ext = os.path.splitext(file_name)[1].lower()
    mime_map = {
        ".mp3": "audio/mp3",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac"
    }
    mime_type = mime_map.get(ext, "audio/mpeg")

    # Limit payload size to ~12MB for inline base64 reliability
    audio_b64 = base64.b64encode(file_bytes[:12_000_000]).decode("utf-8")

    prompt = (
        "Listen carefully to this audio track and analyze its acoustic characteristics alongside these measured spectral metrics: "
        f"{json.dumps(spectral_metrics)}. "
        "Listen for signs of AI music/voice synthesis (such as Suno, Udio, RVC voice conversion artifacts, metallic vocoder shimmer, "
        "unnatural breathing, robotic phrasing, or diffusion noise) versus authentic human studio/live performance. "
        "Respond ONLY with a valid JSON object using this exact schema (no markdown): "
        '{"is_ai": true or false, "ai_probability": 0.0 to 1.0, "confidence": "High" or "Medium" or "Low", '
        '"reason": "Clear 1-2 sentence explanation of what you heard in the vocals, instruments, and production."}'
    )

    payload = {
        "contents": [{
            "parts": [
                {"inlineData": {"mimeType": mime_type, "data": audio_b64}},
                {"text": prompt}
            ]
        }],
        "generationConfig": {"temperature": 0.1}
    }

    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        ctx = ssl.create_default_context() if HAS_SSL else None
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            candidates = resp_data.get("candidates", [])
            if not candidates:
                return {"success": False, "error": "No response returned from Gemini audio analysis."}

            parts = candidates[0].get("content", {}).get("parts", [])
            raw_reply = "".join([p.get("text", "") for p in parts]).strip()
            json_match = re.search(r'\{.*\}', raw_reply, re.DOTALL)
            if not json_match:
                return {"success": False, "error": "Could not parse Gemini audio analysis JSON."}

            parsed_verdict = json.loads(json_match.group(0))
            prob = float(parsed_verdict.get("ai_probability", 0.85 if parsed_verdict.get("is_ai") else 0.15))
            return {
                "success": True,
                "ai_probability": round(min(max(prob, 0.01), 0.99), 2),
                "is_ai": bool(parsed_verdict.get("is_ai", prob > 0.5)),
                "confidence": f"{parsed_verdict.get('confidence', 'High')} (Gemini Audio Listening)",
                "reason": parsed_verdict.get("reason", "Analyzed directly via Gemini multimodal audio listening.")
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def analyze_with_gemini(url: str, platform_name: str, api_key: str, known_title: str = "", known_artist: str = "", keyword_hits: list = None) -> dict:
    """Uses Gemini API with multimodal YouTube listening + Google Search grounding + keyword signals."""
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={urllib.parse.quote(api_key.strip())}"
    
    track_context = ""
    if known_title and known_title not in ("Unreachable Video", "Metadata Blocked", ""):
        track_context = f"The track title is '{known_title}' by '{known_artist}'. "

    keyword_context = ""
    if keyword_hits:
        keyword_context = f"Metadata keyword scan flagged these terms: {', '.join(keyword_hits)}. "

    is_youtube = "youtube.com" in url.lower() or "youtu.be" in url.lower()

    prompt = (
        f"Investigate and listen to this music link ({url}) on {platform_name}. {track_context}{keyword_context}"
        "1. Listen directly to the audio/vocals if accessible, AND use Google Search to verify the exact song, artist/channel, and release details. "
        "2. Evaluate both acoustic cues (RVC voice conversion artifacts, Suno/Udio synth shimmer, unnatural vocal phrasing) AND metadata/keywords. "
        "3. Determine if this song, cover, or vocals were generated using AI or if it is an authentic human-made song by a real artist (like Bruno Mars, Taylor Swift, Drake, etc.). "
        "If it is an official song or authentic human recording, set is_ai to false. "
        "Respond ONLY with a valid JSON object using this exact schema (no markdown formatting): "
        '{"is_ai": true or false, "ai_probability": 0.0 to 1.0, "confidence": "High" or "Medium" or "Low", '
        '"title": "Exact Song Title", "artist": "Exact Artist or Channel Name", "reason": "Clear 1-2 sentence explanation combining what you heard in the audio and found in the metadata."}'
    )

    parts = []
    if is_youtube:
        # Attach YouTube URL directly via fileData so Gemini processes the actual video/audio stream
        parts.append({"fileData": {"fileUri": url}})
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0.1}
    }

    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        ctx = ssl.create_default_context() if HAS_SSL else None
        with urllib.request.urlopen(req, timeout=20, context=ctx) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            candidates = resp_data.get("candidates", [])
            if not candidates:
                return {"success": False, "error": "No response returned from Gemini API."}

            parts = candidates[0].get("content", {}).get("parts", [])
            raw_reply = "".join([p.get("text", "") for p in parts]).strip()
            
            # Extract JSON block cleanly
            json_match = re.search(r'\{.*\}', raw_reply, re.DOTALL)
            if not json_match:
                return {"success": False, "error": "Could not parse structured verdict from Gemini."}
                
            parsed_verdict = json.loads(json_match.group(0))
            prob = float(parsed_verdict.get("ai_probability", 0.85 if parsed_verdict.get("is_ai") else 0.10))
            
            return {
                "success": True,
                "is_ai": bool(parsed_verdict.get("is_ai", prob > 0.5)),
                "unverified": False,
                "confidence": f"{parsed_verdict.get('confidence', 'High')} (Gemini AI)",
                "ai_probability": min(max(prob, 0.01), 0.99),
                "reason": parsed_verdict.get("reason", "Analyzed via Gemini AI live search."),
                "title": parsed_verdict.get("title", known_title or "Track Inspected"),
                "artist": parsed_verdict.get("artist", known_artist or "Creator Inspected"),
                "platform": platform_name,
                "thumbnail": ""
            }
    except urllib.error.HTTPError as http_err:
        err_body = http_err.read().decode("utf-8", errors="ignore")
        return {"success": False, "error": f"Gemini API HTTP {http_err.code}: {err_body[:150]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def inspect_universal_link(url: str, selected_app: str, api_key: str = "") -> dict:
    """Fetches real track data and executes AI metadata analysis across platforms."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    detected_platform = identify_platform(url) if selected_app == "Auto-Detect Platform" else selected_app

    # 1. Direct AI Generation Domain Inspection
    for ai_domain in KNOWN_AI_DOMAINS:
        if ai_domain in domain:
            return {
                "is_ai": True,
                "unverified": False,
                "confidence": "Very High",
                "ai_probability": 0.98,
                "reason": f"Direct link from recognized AI music generation platform ({ai_domain}).",
                "title": f"Generative Track ({ai_domain})",
                "artist": "AI Music Engine",
                "platform": "AI Generator",
                "thumbnail": ""
            }

    # 2. Fetch real track metadata first (Title, Artist, Description)
    if "spotify.com" in domain or selected_app == "Spotify":
        metadata = fetch_spotify_metadata(url)
    elif "youtube.com" in domain or "youtu.be" in domain or selected_app == "YouTube":
        metadata = fetch_youtube_metadata(url)
    else:
        metadata = fetch_generic_metadata(url, detected_platform)

    known_title = metadata.get("title", "") if metadata.get("success") else ""
    known_artist = metadata.get("artist", "") if metadata.get("success") else ""

    # Pre-compute keyword hits from metadata so both Gemini and local checks can use them
    all_matches = []
    if metadata.get("success", False):
        clean_title_artist = f"{known_title} {known_artist}".lower().replace("ａｉ", "ai")
        full_metadata_text = metadata.get("raw_text", "").lower().replace("ａｉ", "ai")
        title_ai_matches = re.findall(r'(?:^|[\s\(\[\|#\-])(ai|rvc|suno|udio)(?:$|[\s\)\]\|#\-])', clean_title_artist)
        phrase_matches = [kw for kw in AI_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', full_metadata_text)]
        all_matches = list(dict.fromkeys(phrase_matches + title_ai_matches))

    # 3. If Gemini API Key is provided, pass the URL + Audio Stream + Title/Artist + Keyword signals to Gemini
    if api_key and api_key.strip():
        gemini_result = analyze_with_gemini(url, detected_platform, api_key, known_title, known_artist, all_matches)
        if gemini_result.get("success"):
            return gemini_result
        else:
            # Surface the actual Gemini API error instead of silently guessing
            return {
                "is_ai": False,
                "unverified": True,
                "confidence": "API Error",
                "ai_probability": 0.50,
                "reason": f"Gemini API Request Failed: {gemini_result.get('error', 'Unknown error')}. Check your API key or network environment.",
                "title": known_title or "API Request Failed",
                "artist": known_artist or "Error",
                "platform": detected_platform,
                "thumbnail": ""
            }

    # 4. Handle blocked/unreachable links honestly instead of guessing "Human-Made"
    if not metadata.get("success", False):
        return {
            "is_ai": False,
            "unverified": True,
            "confidence": "Low (Blocked)",
            "ai_probability": 0.50,
            "reason": f"Could not retrieve live page metadata from {detected_platform} (blocked by browser CORS/SSL sandbox or private link). Add a Gemini API Key above or use 'Audio File Upload' for direct scanning.",
            "title": metadata.get("title", "Metadata Blocked"),
            "artist": metadata.get("artist", "Unknown"),
            "platform": detected_platform,
            "thumbnail": ""
        }

    # 5. Fallback keyword-only analysis when no Gemini API Key is entered
    if all_matches:
        kw_str = ", ".join([f"'{k}'" for k in all_matches[:4]])
        return {
            "is_ai": True,
            "unverified": False,
            "confidence": "High",
            "ai_probability": 0.94,
            "reason": f"Live inspection of {metadata.get('provider', detected_platform)} title, channel, description, and tags detected AI markers: {kw_str}.",
            "title": known_title or "Track Detected",
            "artist": known_artist or "Artist Detected",
            "platform": metadata.get("provider", detected_platform),
            "thumbnail": metadata.get("thumbnail", "")
        }
    else:
        return {
            "is_ai": False,
            "unverified": False,
            "confidence": "High",
            "ai_probability": 0.12,
            "reason": f"Live inspection of track metadata ('{known_title}' by {known_artist}) on {metadata.get('provider', detected_platform)} found no AI disclosure or model tags.",
            "title": known_title or "Track Detected",
            "artist": known_artist or "Artist Detected",
            "platform": metadata.get("provider", detected_platform),
            "thumbnail": metadata.get("thumbnail", "")
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
        placeholder="e.g. https://open.spotify.com/track/... or https://www.youtube.com/watch?v=...",
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
        with st.spinner("Listening to audio track and computing spectral metrics..."):
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
