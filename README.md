# Reels Bot — vídeos animados automáticos para Instagram y YouTube Shorts

Dos veces al día GitHub Actions genera un vídeo vertical de 40-55 s y lo publica solo:

1. **Guion** con IA (Gemini gratis): 25 temáticas organizadas en series con número de episodio, gancho inicial, sin repetir temas.
2. **Voz** con `edge-tts` (gratis), con reintentos y voz de reserva.
3. **Animación por código** (sin imágenes de IA): monigotes, 168 modelos animados con rayos X, modelos a medida
   que diseña la IA, ~1.000 iconos, 33 paisajes, lupas que explican procesos y gráficas.
4. **Montaje** con ffmpeg: subtítulos palabra a palabra, gancho y etiqueta de serie en pantalla, música opcional.
5. **Publicación** en Instagram Reels y YouTube Shorts, y **aviso al móvil** (Discord o Telegram) con el vídeo o el error.

Coste: 0 €.

## Secrets (Settings → Secrets and variables → Actions)
| Secret | Para qué |
|---|---|
| `LLM_API_KEY` | clave de Gemini (aistudio.google.com/apikey) |
| `IG_USER_ID`, `IG_ACCESS_TOKEN` | Instagram (token de System User, no caduca) |
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` | YouTube Shorts (opcional) |
| `DISCORD_WEBHOOK` | avisos al móvil por Discord (opcional) |
| `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID` | avisos por Telegram (opcional) |

Variables: `AUTO_PUBLISH` (`true` para publicar en las ejecuciones programadas), `LANGUAGE` (`es`/`en`).

## Ajustes rápidos
- **Horas**: líneas `cron` de `.github/workflows/reel.yml` (en UTC).
- **Temáticas y series**: `CATEGORIES` y `SERIES` en `config.py`.
- **Voz**: `VOICES` en `config.py`. **Música**: mp3 sin copyright en `assets/music/`.

## Probar
```bash
pip install -r requirements.txt     # y tener ffmpeg instalado
python main.py --demo               # vídeo de prueba sin APIs
python -m tests.fuzz                # dibuja todos los modelos y paisajes buscando fallos
python -m tests.fuzz_guion          # comprueba que un guion mal formado no rompe nada
```

## Créditos
- Iconos: [Fluent Emoji](https://github.com/microsoft/fluentui-emoji) de Microsoft, licencia MIT (ver `assets/emoji/LICENSE-fluentui-emoji.txt`).
