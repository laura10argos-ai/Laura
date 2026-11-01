# Laura · Your Own Voice

Herramientas para producir el contenido del canal.

## Kit de edición de entrevistas para DaVinci Resolve

Prepara cada entrevista para editarla en DaVinci Resolve (funciona con la versión
gratuita):

- quita los silencios largos y genera el corte bruto (`.fcpxml`)
- marca muletillas, repeticiones y candidatos a Short/Reel con marcadores de colores
- genera subtítulos `.srt` alineados con el corte
- incluye scripts para Resolve: estructura de proyecto, Shorts verticales automáticos
  desde marcadores y capítulos de YouTube

```bash
pip install -r requirements.txt
python resolve/preparar_entrevista.py "Entrevista.mp4"
```

Guía completa: [`resolve/GUIA_EDICION.md`](resolve/GUIA_EDICION.md)

## Transcripción simple

```bash
python transcribe.py path/to/audio.mp3 --model small --language es
```

Usa [openai-whisper](https://github.com/openai/whisper) con
[static-ffmpeg](https://pypi.org/project/static-ffmpeg/), así que no hace falta
instalar ffmpeg en el sistema.
