# Video Transcriber

Aplicación web para transcribir el audio de un video a texto. Todo se ejecuta en local con [faster-whisper](https://github.com/SYSTRAN/faster-whisper): ningún archivo sale de tu máquina.

## Requisitos

- Python 3.10 o superior
- [ffmpeg](https://ffmpeg.org/) instalado y disponible en el `PATH`

## Instalación

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Uso

```bash
.venv/bin/python main.py
```

Abre http://127.0.0.1:7860, sube un video, elige el modelo y el idioma, y pulsa **Submit**. La transcripción aparece en pantalla (con botón para copiarla) y puedes descargarla como `.txt`.

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

El modelo se ejecuta en GPU si hay una disponible, y en CPU (cuantizado a int8) en caso contrario.

## Notas

- `requirements.txt` fija `av>=14,<16` porque versiones posteriores de `av` son incompatibles con `faster-whisper` 1.2.1.
