# Video Transcriber

Aplicación web para transcribir el audio de un video a texto. Todo se ejecuta en local con [faster-whisper](https://github.com/SYSTRAN/faster-whisper): ningún archivo sale de tu máquina.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) con Docker Compose

No necesitas instalar Python ni ffmpeg: van dentro de la imagen.

## Uso

```bash
docker compose up --build
```

Abre http://127.0.0.1:7860, suelta un video, elige el modelo y el idioma, y pulsa **Transcribir**. La transcripción aparece en pantalla (con botón para copiarla) y puedes descargarla como `.txt`.

Para parar: `docker compose down` (añade `-v` para borrar también los modelos descargados).

El puerto solo se publica en tu propio equipo (`127.0.0.1`), y los modelos se guardan en el volumen `models`, así que se descargan una sola vez.

## Rendimiento

La imagen usa solo CPU. En Linux el rendimiento es prácticamente el mismo que sin Docker; en Mac y Windows, Docker corre dentro de una máquina virtual y la transcripción es algo más lenta. Para usar GPU hace falta una imagen con CUDA y el NVIDIA Container Toolkit, que esta configuración no incluye.

## Modelos

| Modelo | Velocidad | Precisión |
|---|---|---|
| `tiny` | Muy rápido | Baja |
| `base` | Rápido | Media-baja |
| `small` (por defecto) | Moderada | Buena |
| `medium` | Lenta | Muy buena |
| `large-v3` | Muy lenta en CPU | Máxima |

La primera vez que se usa un modelo se descarga automáticamente (`small` ocupa unos 500 MB) y queda en caché.

## Cómo funciona

1. `ffmpeg` extrae el audio del video a WAV mono de 16 kHz.
2. `faster-whisper` transcribe el audio (con filtro de silencios VAD).
3. El texto se muestra en la interfaz y se guarda en un `.txt` descargable.

El modelo se ejecuta en CPU, cuantizado a int8. Si el audio no contiene voz, la app lo avisa en lugar de devolver un resultado vacío.

## Estructura

| Archivo | Contenido |
|---|---|
| `main.py` | Lógica de transcripción, tema de Gradio y layout (`gr.Blocks`) |
| `style.css` | Estilo visual: papel cálido, tinta casi negra y rojo señal, con etiquetas en monoespaciada |
| `Dockerfile`, `docker-compose.yml` | Imagen y servicio: Python, ffmpeg, dependencias y volumen de modelos |
| `PRODUCT.md` | Contexto del producto (usuarios, posición, principios) para las herramientas de diseño |

La interfaz usa siempre el tema claro, aunque el navegador esté en modo oscuro. Las fuentes (Archivo e IBM Plex Mono) no se descargan: si no están instaladas se usan Helvetica/Arial y una monoespaciada del sistema, para no hacer peticiones de red.

## Notas

- `requirements.txt` lo instala el `Dockerfile` y fija `av>=14,<16` porque versiones posteriores de `av` son incompatibles con `faster-whisper` 1.2.1.
- Gradio 6 recibe el tema y el CSS en `launch()`, no en el constructor de `Blocks`.
