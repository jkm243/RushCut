#!/bin/bash
# Build RushCut.app (macOS)
pip3 install -r requirements.txt
pyinstaller --onefile --windowed --name RushCut app/main.py
echo "OK -> dist/RushCut.app"
