"""Configuración del bot. Casi todo se puede cambiar con variables de entorno."""
import os

# --- Idioma y voz -----------------------------------------------------------
LANGUAGE = os.getenv("LANGUAGE", "es")  # "es" o "en"
VOICES = {
    "es": os.getenv("VOICE", "es-ES-AlvaroNeural"),   # alternativas: es-MX-JorgeNeural, es-ES-ElviraNeural
    "en": os.getenv("VOICE", "en-US-AndrewNeural"),   # alternativas: en-US-ChristopherNeural, en-US-AriaNeural
}
VOICE_RATE = os.getenv("VOICE_RATE", "+8%")  # un pelín más rápido = más retención

# --- Temas ("de todo") -------------------------------------------------------
# Cada ejecución elige una categoría distinta a la última. Añade o quita las que quieras.
CATEGORIES = [
    "curiosidad científica sorprendente",
    "historia real poco conocida",
    "misterio sin resolver",
    "dato increíble de animales",
    "el espacio y el universo",
    "qué pasaría si... (hipotético explicado con ciencia)",
    "inventos y accidentes que cambiaron el mundo",
    "cuerpo humano y cerebro",
    "lugares extraños del planeta",
    "personajes históricos con vidas de película",
    "psicología y comportamiento humano",
    "deporte: récords e historias legendarias",
]

# --- Guion (LLM gratis vía API compatible con OpenAI) ------------------------
# gemini -> clave gratis en https://aistudio.google.com/apikey
# groq   -> clave gratis en https://console.groq.com/keys
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_PRESETS = {
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "gemini-3.8-flash"),
    "groq": ("https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"),
}
LLM_BASE_URL = os.getenv("LLM_BASE_URL", LLM_PRESETS[LLM_PROVIDER][0])
LLM_MODEL = os.getenv("LLM_MODEL", LLM_PRESETS[LLM_PROVIDER][1])
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

TARGET_WORDS = (110, 145)  # ~40-55 s de narración

# --- Imágenes (Pollinations, gratis) -----------------------------------------
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "flux")
POLLINATIONS_TOKEN = os.getenv("POLLINATIONS_TOKEN", "")  # opcional, da más cuota
# Estilo visual:
#   "animado"   -> monigotes animados por código (se mueven de verdad, sin imágenes de IA)  <- por defecto
#   "monigotes" / "pixar" -> imágenes de IA con zoom;  "mix" -> alterna entre imágenes de IA
VISUAL_STYLE = os.getenv("VISUAL_STYLE", "animado")
VISUAL_STYLES = {
    "animado": {"hint": "animación de monigotes", "suffix": ""},
    "pixar": {
        "hint": "personajes 3D tipo película de animación, muy expresivos y exagerados, caras grandes, colores vivos",
        "suffix": "3D animated movie style render, cute stylized cartoon characters, big expressive eyes, "
                  "exaggerated facial expression, vibrant saturated colors, soft cinematic lighting, "
                  "detailed background, no text, vertical composition",
    },
    "monigotes": {
        "hint": "monigotes (stickmen) simples dibujados a mano, sobre fondo blanco limpio, con algún objeto clave",
        "suffix": "simple hand-drawn stick figure cartoon, thick black marker lines, round head with simple "
                  "expressive face, minimalist doodle, clean plain white background, one or two flat accent colors, "
                  "funny explainer video style, no text, vertical composition",
    },
}

# --- Vídeo -------------------------------------------------------------------
WIDTH, HEIGHT, FPS = 1080, 1920, 30
FONT_NAME = os.getenv("FONT_NAME", "DejaVu Sans")
FONT_SIZE = int(os.getenv("FONT_SIZE", "96"))
HIGHLIGHT_COLOR = "&H0000E5FF"  # amarillo en formato ASS (&HAABBGGRR)
MUSIC_DIR = "assets/music"      # mete aquí mp3 sin copyright; se elige uno al azar
MUSIC_VOLUME = float(os.getenv("MUSIC_VOLUME", "0.12"))

# --- Instagram ---------------------------------------------------------------
IG_USER_ID = os.getenv("IG_USER_ID", "")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "")
IG_API = "https://graph.instagram.com/v23.0"

OUTPUT_DIR = "output"
HISTORY_FILE = "history.json"
