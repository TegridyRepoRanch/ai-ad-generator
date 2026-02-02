"""
Configuration for the Ad Generation Platform
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Paths
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
FONTS_DIR = TEMPLATES_DIR / "fonts"

# Use /tmp for output in serverless environments (Vercel, AWS Lambda, etc.)
# Falls back to local output/ directory for local development
IS_SERVERLESS = os.getenv("VERCEL", os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
if IS_SERVERLESS:
    OUTPUT_DIR = Path("/tmp/output")
else:
    OUTPUT_DIR = BASE_DIR / "output"

# Create directories if they don't exist (wrapped in try for serverless cold starts)
try:
    OUTPUT_DIR.mkdir(exist_ok=True)
    TEMPLATES_DIR.mkdir(exist_ok=True)
    FONTS_DIR.mkdir(exist_ok=True)
except Exception:
    pass  # May fail in some serverless environments, that's okay

# Image Generation Settings (Google Imagen)
IMAGE_MODELS = {
    "imagen_3": "imagen-3.0-generate-002",
    "imagen_3_fast": "imagen-3.0-fast-generate-001",
}
DEFAULT_IMAGE_MODEL = "imagen_3"

# Ad Dimensions (standard social media sizes)
AD_SIZES = {
    "facebook_feed": (1200, 1200),
    "instagram_feed": (1080, 1080),
    "instagram_story": (1080, 1920),
    "facebook_story": (1080, 1920),
}
DEFAULT_AD_SIZE = "instagram_feed"

# Headline Settings
MIN_HEADLINE_WORDS = 3
MAX_HEADLINE_WORDS = 7

# Template Settings
TEMPLATE_STYLES = [
    "minimal",           # Clean, headline at top
    "banner_bottom",     # Banner bar at bottom
    "sale_sticker",      # Sale sticker overlay
    "split_layout",      # Image on one side, text on other
    "diagonal_banner",   # Diagonal banner across corner
    "gradient_overlay",  # Gradient with text overlay
]

# Colors for templates
TEMPLATE_COLORS = {
    "primary": "#1a1a2e",
    "secondary": "#16213e",
    "accent": "#e94560",
    "text_light": "#ffffff",
    "text_dark": "#1a1a2e",
    "sale_red": "#ff3333",
    "sale_yellow": "#ffcc00",
}

# Typography
FONT_SETTINGS = {
    "headline": {
        "size_ratio": 0.08,  # Relative to image width
        "weight": "bold",
    },
    "subheadline": {
        "size_ratio": 0.04,
        "weight": "regular",
    }
}
