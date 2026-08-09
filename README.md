# Laura

Audio transcription using [openai-whisper](https://github.com/openai/whisper), with
[static-ffmpeg](https://pypi.org/project/static-ffmpeg/) providing a bundled ffmpeg
binary so no system-wide ffmpeg install is needed.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python transcribe.py path/to/audio.mp3
```

Options:

```bash
python transcribe.py path/to/audio.mp3 --model small --language en
```

`transcribe.py` calls `static_ffmpeg.add_paths()` on import to put the bundled
ffmpeg/ffprobe binaries on `PATH` before Whisper needs them.
