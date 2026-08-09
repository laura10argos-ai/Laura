#!/usr/bin/env python3
"""Transcribe an audio file to text using openai-whisper.

Bundles its own ffmpeg via static-ffmpeg, so no system ffmpeg install is required.
"""
import argparse
import sys

import static_ffmpeg

# Must run before whisper (or anything else that shells out to ffmpeg) is used,
# since whisper locates ffmpeg via PATH rather than accepting a binary path.
static_ffmpeg.add_paths()

import whisper


def transcribe(audio_path: str, model_name: str = "base", language: str | None = None) -> str:
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path, language=language)
    return result["text"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", help="Path to an audio file (mp3, wav, m4a, etc.)")
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size to use (default: base)",
    )
    parser.add_argument("--language", default=None, help="Force a source language (e.g. 'en')")
    args = parser.parse_args()

    text = transcribe(args.audio, model_name=args.model, language=args.language)
    print(text.strip())


if __name__ == "__main__":
    main()
