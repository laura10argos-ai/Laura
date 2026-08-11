#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# ffmpeg: apt package (Homebrew isn't available on this Linux container).
# transcribe.py normally bundles its own ffmpeg via static-ffmpeg, but a
# system ffmpeg/ffprobe is handy for ad-hoc debugging and other tooling.
if ! command -v ffmpeg >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y -qq ffmpeg
fi

# node: expected to already be preinstalled in the base image; nothing in
# this repo depends on it (no package.json), so just verify it's on PATH.
command -v node >/dev/null 2>&1 || echo "warning: node not found on PATH" >&2

# python: install the project's runtime dependencies into a venv.
# Ubuntu 24.04 blocks system-wide pip installs (PEP 668), and static-ffmpeg
# pulls in twine -> packaging>=26, which conflicts with the apt-owned
# "packaging" package when installed system-wide.
VENV="$CLAUDE_PROJECT_DIR/.venv"
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q -r "$CLAUDE_PROJECT_DIR/requirements.txt"

echo "export PATH=\"$VENV/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
