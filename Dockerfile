FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Usuario sin privilegios; /models guarda los modelos descargados (montado como volumen)
RUN useradd --create-home app && mkdir /models && chown app /models
USER app
WORKDIR /home/app

ENV PATH="/home/app/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/models \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    GRADIO_ANALYTICS_ENABLED=False

COPY --chown=app requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app main.py style.css ./

EXPOSE 7860
CMD ["python", "main.py"]
