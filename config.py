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
    # historias y gente
    "historia real tan loca que parece inventada",
    "¿por qué...? la explicación sorprendente de una costumbre, objeto o norma de todos los días",
    "oficios antiguos rarísimos que ya no existen",
    "personaje histórico con una vida de película",
    "estafa o golpe famoso (cómo lo hicieron y cómo los pillaron)",
    "anécdota increíble de un famoso",
    "el origen sorprendente de una marca o empresa famosa",
    "millonarios, dinero y fortunas absurdas",
    # deporte y ocio
    "fútbol: anécdotas, récords y momentos legendarios",
    "deporte: historias épicas y récords imposibles",
    "videojuegos: secretos y curiosidades",
    "cine y series: secretos de rodaje y curiosidades",
    "música: historias detrás de canciones y artistas",
    # mundo y vida diaria
    "costumbres y leyes rarísimas de otros países",
    "lugares extraños, prohibidos o abandonados del planeta",
    "comida: orígenes y curiosidades que no sabías",
    "mitos que todo el mundo cree y son falsos",
    "trucos y datos útiles para la vida diaria",
    "psicología: por qué hacemos lo que hacemos",
    "récords Guinness absurdos",
    "inventos y accidentes que cambiaron el mundo",
    "misterio sin resolver",
    "historia de Internet, memes y tecnología",
    # naturaleza y ciencia (minoría a propósito)
    "dato increíble de animales",
    "el espacio y el universo",
    "cuerpo humano y cerebro",
    "qué pasaría si... (hipotético)",
]

# Peso de cada temática al elegir (por defecto 1). Las historias de personas y engaños son las que más
# visitas dan; la ciencia pura queda como minoría.
CATEGORY_WEIGHTS = {
    # Revisado el 28/11/2026 con las estadísticas reales (likes de Instagram + visitas de YouTube, 47 Shorts).
    # En YouTube todos se quedan en ~1.000 visitas (el problema es el gancho, no el tema); en Instagram sí
    # hay diferencias claras: ganan las historias con algo que todo el mundo conoce (fútbol, videojuegos,
    # países, timos) y pierden la ciencia, el deporte "épico" genérico y los trucos.
    "fútbol: anécdotas, récords y momentos legendarios": 6,       # 93 likes (falso futbolista de la Premier)
    "videojuegos: secretos y curiosidades": 6,                    # 80 likes (Creeper) + Especial GTA 22-46
    "costumbres y leyes rarísimas de otros países": 6,            # 74 likes, el más visto en YouTube (1.395)
    "estafa o golpe famoso (cómo lo hicieron y cómo los pillaron)": 5,  # 59, 36, 35
    "oficios antiguos rarísimos que ya no existen": 4,            # 64 y 19
    "historia real tan loca que parece inventada": 3,             # 59, 23, 21
    "personaje histórico con una vida de película": 3,            # 68
    "inventos y accidentes que cambiaron el mundo": 3,            # 44
    "anécdota increíble de un famoso": 3,                         # 32
    "el origen sorprendente de una marca o empresa famosa": 3,
    "¿por qué...? la explicación sorprendente de una costumbre, objeto o norma de todos los días": 2,
    "lugares extraños, prohibidos o abandonados del planeta": 2,  # 37
    "cine y series: secretos de rodaje y curiosidades": 2,
    # flojos: salen muy de vez en cuando
    "millonarios, dinero y fortunas absurdas": 0.7,               # 10 y 6
    "dato increíble de animales": 0.5,
    "récords Guinness absurdos": 0.5,                             # 21 y 3
    "música: historias detrás de canciones y artistas": 0.5,
    "comida: orígenes y curiosidades que no sabías": 0.5,
    "misterio sin resolver": 0.5,
    "qué pasaría si... (hipotético)": 0.3,
    "psicología: por qué hacemos lo que hacemos": 0.3,
    "mitos que todo el mundo cree y son falsos": 0.3,
    "historia de Internet, memes y tecnología": 0.3,              # 24 y 4
    "deporte: historias épicas y récords imposibles": 0.2,        # 2 y 2
    "trucos y datos útiles para la vida diaria": 0.2,             # 5
    "cuerpo humano y cerebro": 0.2,                               # 1 y 19
    "el espacio y el universo": 0.2,                              # 3
}

# Cada temática es una SERIE con nombre fijo y número de episodio (crea costumbre y seguidores)
SERIES = {
    "¿por qué...? la explicación sorprendente de una costumbre, objeto o norma de todos los días": "¿Por qué?",
    "oficios antiguos rarísimos que ya no existen": "Oficios olvidados",
    "historia real tan loca que parece inventada": "Parece inventado",
    "personaje histórico con una vida de película": "Vidas de película",
    "estafa o golpe famoso (cómo lo hicieron y cómo los pillaron)": "Golpes maestros",
    "anécdota increíble de un famoso": "Famosos al desnudo",
    "el origen sorprendente de una marca o empresa famosa": "Así nació",
    "millonarios, dinero y fortunas absurdas": "Dinero absurdo",
    "fútbol: anécdotas, récords y momentos legendarios": "Fútbol de leyenda",
    "deporte: historias épicas y récords imposibles": "Deporte épico",
    "videojuegos: secretos y curiosidades": "Secretos gamer",
    "cine y series: secretos de rodaje y curiosidades": "Detrás de cámara",
    "música: historias detrás de canciones y artistas": "La historia de la canción",
    "costumbres y leyes rarísimas de otros países": "Solo pasa allí",
    "lugares extraños, prohibidos o abandonados del planeta": "Lugares prohibidos",
    "comida: orígenes y curiosidades que no sabías": "Lo que comes",
    "mitos que todo el mundo cree y son falsos": "Mitos falsos",
    "trucos y datos útiles para la vida diaria": "Truco del día",
    "psicología: por qué hacemos lo que hacemos": "Tu cerebro te engaña",
    "récords Guinness absurdos": "Récords absurdos",
    "inventos y accidentes que cambiaron el mundo": "Inventado por error",
    "misterio sin resolver": "Sin resolver",
    "historia de Internet, memes y tecnología": "Historia de Internet",
    "dato increíble de animales": "Animales increíbles",
    "el espacio y el universo": "Fuera de este mundo",
    "cuerpo humano y cerebro": "Tu cuerpo es raro",
    "qué pasaría si... (hipotético)": "¿Qué pasaría si...?",
}

# Ejecuciones especiales (p. ej. el workflow "Especial GTA"): si están vacías, el bot funciona como siempre
FORCE_CATEGORY = os.getenv("FORCE_CATEGORY", "").strip()   # temática fija para este vídeo
FORCE_SERIES = os.getenv("FORCE_SERIES", "").strip()       # nombre de serie propio ("Especial GTA")
FORCE_NOTES = os.getenv("FORCE_NOTES", "").strip()         # indicaciones extra para el guion

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

# Duración del vídeo. Se prueban dos versiones y se comparan con "python -m tools.stats":
#   "corto" -> ~25 s   |   "medio" -> ~40 s   |   "ab" -> alterna una y otra (por defecto)
# La voz va a unas 2,6 palabras por segundo.
DURATIONS = {
    "corto": {"words": (52, 66), "scenes": (5, 7), "label": "~25 s"},
    "medio": {"words": (88, 108), "scenes": (8, 11), "label": "~40 s"},
}
DURATION_MODE = (os.getenv("DURATION_MODE", "") or "ab").strip().lower()
# valores por defecto (los usa el vídeo largo); main.py los cambia en cada Short según la duración elegida
TARGET_WORDS = (70, 95)
TARGET_SCENES = (7, 10)

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
