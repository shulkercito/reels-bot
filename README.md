# Reels Bot — curiosidades automáticas para Instagram

Cada día GitHub Actions genera un Reel de 40-55 s y lo publica en Instagram:

1. **Guion** con IA (Gemini o Groq, ambos gratis) → gancho + 6-9 escenas, sin repetir temas.
2. **Voz** con `edge-tts` (voces neuronales de Microsoft, gratis).
3. **Imágenes** verticales con Pollinations (FLUX, gratis).
4. **Montaje** con ffmpeg: zoom/paneo en cada imagen, subtítulos palabra a palabra con la palabra activa en amarillo, música opcional, audio normalizado.
5. **Publicación** como Reel con la API oficial de Instagram.

Coste: 0 €. Temas: rotan entre 12 categorías (`config.py` → `CATEGORIES`).

---

## Puesta en marcha (≈30 min, una sola vez)

### 1. Repositorio
- Crea un repo **público** en GitHub y sube esta carpeta.
  (Público porque Instagram descarga el vídeo desde una release del repo. Las claves van en *Secrets* y no se ven.)
- Si lo prefieres privado: crea la variable `VIDEO_HOST = catbox` (ver paso 4).

### 2. Clave gratis para el guion
- Gemini: https://aistudio.google.com/apikey → *Create API key*.
- (Alternativa: Groq en https://console.groq.com/keys y variable `LLM_PROVIDER = groq`.)

### 3. Instagram
1. En la app de Instagram, pasa la cuenta a **profesional** (Creador o Empresa).
2. En https://developers.facebook.com crea una app tipo *Business* y añade el producto **Instagram → API setup with Instagram login**.
3. Añade tu cuenta de Instagram, pide el permiso `instagram_business_content_publish` y **genera un token**.
4. Apunta el **ID de usuario de Instagram** que aparece ahí y el **token** (es de 60 días).

Mientras la app esté en modo desarrollo, solo puede publicar en cuentas añadidas como testers: con la tuya basta.

### 4. Secrets y variables del repo
*Settings → Secrets and variables → Actions*

| Secret | Valor |
|---|---|
| `LLM_API_KEY` | clave de Gemini (o Groq) |
| `IG_USER_ID` | ID de Instagram |
| `IG_ACCESS_TOKEN` | token de Instagram |
| `GH_PAT` *(opcional)* | token de GitHub con permiso de *Secrets* del repo; así el bot renueva solo el token de Instagram y no caduca |
| `POLLINATIONS_TOKEN` *(opcional)* | más cuota de imágenes en https://auth.pollinations.ai |

| Variable | Valor |
|---|---|
| `AUTO_PUBLISH` | `false` al principio; `true` cuando te gusten los vídeos |
| `LANGUAGE` | `es` (o `en`) |
| `VIDEO_HOST` | `github` (por defecto) o `catbox` |

### 5. Primera prueba
*Actions → Reel diario → Run workflow* con la casilla de publicar **desmarcada**.
Al acabar, descarga el vídeo en *Artifacts → reel* y revísalo.
Si está bien, repite marcando la casilla y luego pon `AUTO_PUBLISH = true`.

---

## Ajustes rápidos
- **Hora**: línea `cron` en `.github/workflows/reel.yml` (en UTC). Para 2 vídeos al día, añade otra línea `cron`.
- **Voz**: `VOICES` en `config.py` (`es-ES-AlvaroNeural`, `es-MX-JorgeNeural`, `es-ES-ElviraNeural`…).
- **Estilo de imagen**: `IMAGE_STYLE` en `config.py`.
- **Música**: mp3 sin copyright en `assets/music/`.
- **Subtítulos**: `FONT_NAME`, `FONT_SIZE`, `HIGHLIGHT_COLOR` en `config.py`.

## Probar en tu ordenador
```bash
pip install -r requirements.txt   # y tener ffmpeg instalado
python main.py --demo             # montaje de prueba sin APIs
LLM_API_KEY=xxx python main.py --no-publish   # vídeo real, sin publicar
```

## Si algo falla
- **Instagram no procesa el vídeo** (`ERROR` en el estado): pon la variable `VIDEO_HOST = catbox`.
- **Imágenes que fallan**: la cuota gratis de Pollinations se satura a veces; el bot reintenta y reutiliza la imagen anterior. Con `POLLINATIONS_TOKEN` va mejor.
- **Token caducado**: genera uno nuevo y actualiza `IG_ACCESS_TOKEN` (o configura `GH_PAT` para que se renueve solo).

## Créditos
- Iconos: [Fluent Emoji](https://github.com/microsoft/fluentui-emoji) de Microsoft, licencia MIT (ver `assets/emoji/LICENSE-fluentui-emoji.txt`).
