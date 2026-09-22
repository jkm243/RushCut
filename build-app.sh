#!/bin/bash
# RushCut - Build macOS (ffmpeg embarque, installe via brew si absent)
set -e
echo "[1/3] Dependances..."
pip3 install -r requirements.txt
echo "[2/3] ffmpeg..."
if ! command -v ffmpeg &>/dev/null; then
    brew install ffmpeg
fi
FFMPEG_PATH=$(command -v ffmpeg)
mkdir -p vendor && cp "$FFMPEG_PATH" vendor/ffmpeg
echo "[3/3] Build RushCut.app..."
pyinstaller --onefile --windowed --name RushCut \
    --add-binary "vendor/ffmpeg:." \
    app/main.py
echo "OK -> dist/RushCut.app (a zipper pour distribution)"
