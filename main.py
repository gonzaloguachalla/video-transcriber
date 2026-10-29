import subprocess
import tempfile
from pathlib import Path

import gradio as gr
from faster_whisper import WhisperModel

MODELS = ["tiny", "base", "small", "medium", "large-v3"]
LANGUAGES = {"Detectar automáticamente": None, "Español": "es", "English": "en"}

_model_cache: dict[str, WhisperModel] = {}


def get_model(name: str) -> WhisperModel:
    if name not in _model_cache:
        _model_cache[name] = WhisperModel(name, device="auto", compute_type="int8")
    return _model_cache[name]


def extract_audio(video_path: str, wav_path: str) -> None:
    # 16 kHz mono es el formato que espera Whisper
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000", wav_path],
        check=True,
        capture_output=True,
    )


def transcribe(video_path, model_name, language, progress=gr.Progress()):
    if not video_path:
        raise gr.Error("Sube un video primero.")

    with tempfile.TemporaryDirectory() as tmp:
        wav_path = str(Path(tmp) / "audio.wav")
        progress(0, desc="Extrayendo audio...")
        try:
            extract_audio(video_path, wav_path)
        except subprocess.CalledProcessError:
            raise gr.Error("No se pudo extraer el audio (¿el video tiene pista de audio?).")

        progress(0.1, desc=f"Cargando modelo {model_name}...")
        model = get_model(model_name)
        segments, info = model.transcribe(wav_path, language=LANGUAGES[language], vad_filter=True)

        parts = []
        for seg in segments:
            parts.append(seg.text.strip())
            progress(0.1 + 0.9 * min(seg.end / info.duration, 1), desc="Transcribiendo...")

    text = "\n".join(parts)
    out_path = Path(tempfile.mkdtemp()) / f"{Path(video_path).stem}.txt"
    out_path.write_text(text, encoding="utf-8")
    return text, str(out_path)


demo = gr.Interface(
    fn=transcribe,
    inputs=[
        gr.Video(label="Video"),
        gr.Dropdown(MODELS, value="small", label="Modelo (más grande = más preciso y lento)"),
        gr.Dropdown(list(LANGUAGES), value="Detectar automáticamente", label="Idioma"),
    ],
    outputs=[
        gr.Textbox(label="Transcripción", lines=15, buttons=["copy"]),
        gr.File(label="Descargar .txt"),
    ],
    title="Video Transcriber",
    description="Transcribe el audio de un video localmente con Whisper.",
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.launch()
