import subprocess
import tempfile
from pathlib import Path

import gradio as gr
from faster_whisper import WhisperModel

MODELS = [
    ("tiny · muy rápido", "tiny"),
    ("base · rápido", "base"),
    ("small · equilibrado", "small"),
    ("medium · lento, preciso", "medium"),
    ("large-v3 · muy lento, máxima precisión", "large-v3"),
]
LANGUAGES = {"Detectar automáticamente": None, "Español": "es", "English": "en"}

ASSETS = Path(__file__).parent

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
    if not text:
        gr.Warning("No se detectó voz en el audio.")
    out_path = Path(tempfile.mkdtemp()) / f"{Path(video_path).stem}.txt"
    out_path.write_text(text, encoding="utf-8")
    return text, str(out_path)


theme = gr.themes.Base(
    primary_hue=gr.themes.Color(
        c50="#f4f3ef", c100="#e9e6dc", c200="#cfcbbd", c300="#a7a394", c400="#7d7a6e",
        c500="#4a483f", c600="#2c2b24", c700="#17160f", c800="#17160f", c900="#0f0e0a", c950="#0a0907",
    ),
    neutral_hue=gr.themes.Color(
        c50="#fbfaf6", c100="#f3f1ea", c200="#e9e6dc", c300="#cfcbbd", c400="#9a968a",
        c500="#7d7a6e", c600="#4a483f", c700="#3a382f", c800="#2a2922", c900="#17160f", c950="#0f0e0a",
    ),
    font=[gr.themes.Font("Archivo"), gr.themes.Font("Helvetica Neue"), gr.themes.Font("Arial"), gr.themes.Font("sans-serif")],
    font_mono=[gr.themes.Font("IBM Plex Mono"), gr.themes.Font("ui-monospace"), gr.themes.Font("Menlo"), gr.themes.Font("monospace")],
    radius_size=gr.themes.sizes.radius_none,
).set(
    body_background_fill="#f3f1ea",
    block_background_fill="#fbfaf6",
    block_border_color="#cfcbbd",
    button_primary_background_fill="#17160f",
    button_primary_background_fill_hover="#2c2b24",
    button_primary_text_color="#f3f1ea",
)

# Fuerza el tema claro: el papel no tiene versión oscura
HEAD = """<script>
const light = () => {
  document.documentElement.classList.remove('dark');
  document.body && document.body.classList.remove('dark');
};
light();
document.addEventListener('DOMContentLoaded', light);
[300, 1000, 2500].forEach((ms) => setTimeout(light, ms));
</script>"""

with gr.Blocks(title="Video Transcriber") as demo:
    gr.HTML(
        "<header class='app-head'><h1>Video Transcriber</h1>"
        "<p>Transcribe el audio de un video con Whisper. <strong>Ningún archivo sale de tu equipo.</strong></p></header>"
    )
    with gr.Group(elem_classes="panel entrada"):
        gr.HTML("<div class='strip'><b>entrada</b><span>video · modelo · idioma</span></div>")
        video = gr.Video(label="Video")
        with gr.Row():
            model = gr.Dropdown(
                MODELS,
                value="small",
                label="Modelo",
            )
            language = gr.Dropdown(list(LANGUAGES), value="Detectar automáticamente", label="Idioma")
        gr.HTML("<p class='hint'>Más grande = más preciso y más lento. La primera vez que usas un modelo se descarga (small ≈ 500 MB).</p>")
        submit = gr.Button("Transcribir", variant="primary", elem_classes="go")
    with gr.Group(elem_classes="panel salida"):
        gr.HTML("<div class='strip'><b>salida</b><span>transcripción · .txt</span></div>")
        transcript = gr.Textbox(
            label="Transcripción",
            lines=14,
            max_lines=14,
            buttons=["copy"],
            placeholder="La transcripción aparecerá aquí cuando termine.",
            elem_classes="transcript",
        )
        download = gr.File(label="Descargar .txt")
    submit.click(transcribe, [video, model, language], [transcript, download])

if __name__ == "__main__":
    demo.launch(theme=theme, css_paths=[ASSETS / "style.css"], head=HEAD)
