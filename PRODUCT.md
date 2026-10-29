# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
The author, as a personal tool. They upload a video from their own machine, pick a model and language, and want the transcript as text to read, copy, or download. No other audience is planned.

## Product Purpose
Transcribe the audio of a video to text, entirely locally. Success is a correct transcript with minimal steps and no data leaving the machine.

## Positioning
Private and local: transcription runs on the user's own CPU/GPU with faster-whisper, and no file is sent to any service.

## Operating Context
Runs as a local Gradio server at http://127.0.0.1:7860 (`python main.py`). Requires Python 3.10+ and ffmpeg on the PATH. Flow: ffmpeg extracts mono 16 kHz WAV, faster-whisper transcribes with VAD filter, and the text is shown and saved as a downloadable `.txt`. The first use of each model downloads it (`small` is about 500 MB). Long runs are slow on CPU, so progress feedback matters.

## Capabilities and Constraints
- Inputs: video file, model (`tiny`, `base`, `small` default, `medium`, `large-v3`), language (auto-detect, Español, English).
- Outputs: transcript text with copy button, `.txt` download.
- Stack: Python + Gradio (`gr.Interface`) in a single `main.py`; the UI stays on Gradio, so visual work happens through Gradio theming and CSS.
- UI copy is in Spanish.

## Brand Commitments
Name: "Video Transcriber". UI language is Spanish.

## Evidence on Hand
README.md documents setup, models, and pipeline. No screenshots, logos, testimonials, or benchmarks exist; none should be invented.

## Product Principles
- Local-first: never imply or require network services for transcription.
- Few steps from video to text; defaults should work without configuration.
- Be honest about time and cost (model size, download, CPU speed) while work is running.
- Stay a small single-purpose tool; resist feature sprawl.
