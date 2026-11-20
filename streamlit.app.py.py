import streamlit as st
import os
import re
import time
import json
import base64
import urllib.request
import urllib.parse
from urllib.parse import urlparse
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
    '<div class="brand-subtitle">Perform real-time multimodal AI audio & metadata detection on songs from Spotify, YouTube, SoundCloud, Apple Music, and uploaded files.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="info-card">
        Real-time multimodal inspector: Combines Gemini acoustic listening, live streaming metadata, artist tags, and FFT spectral analysis.
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
    "Gemini API Key (Enables active audio listening & deep web search)",
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
    "kits.ai", "jammable", "voicify", "weights.gg"
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
        r'([a-zA-Z0-9-
