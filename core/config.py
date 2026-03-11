"""
Configuration variables and shared constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Define the standard list of electronic genres
GENRES = [
    "House", "Deep House", "Progressive House", "Tech House", "Electro House",
    "Deep Techno", "Acid House", "Disco House", "Drum and Bass", "Trance",
    "Progressive Trance", "Psytrance", "Techno", "Acid Techno", "Minimal Techno",
    "Hard Techno", "Electro", "Nu-Disco"
]

# Check for Gemini availability
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

USE_GEMINI_API = os.getenv("USE_GEMINI_API", "true").lower() == "true"
if USE_GEMINI_API and not GEMINI_AVAILABLE:
    print("Warning: google-genai needed for Gemini API. Using Ollama.")
    USE_GEMINI_API = False
