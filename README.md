# Echoscribe

Live captions from your mic and system audio. Runs fully on your machine, no cloud, no API key.

## Project structure
echoscribe/

├── main.py
├── start.bat
├── requirements.txt
├── audio/
│   ├── audio_capture.py
│   └── transcriber.py
├── backend/
│   ├── api.py
│   ├── audio_source.py
│   ├── worker.py
│   └── test_clint.py
├── extension/
│   ├── manifest.json
│   ├── popup.html
│   └── popup.js
└── docs/
└── SYSTEM_DESIGN.md

## Install

Clone the repo.
git clone https://github.com/juliocaesar14/echoscribe.git

cd echoscribe

Install dependencies.
pip install -r requirements.txt

Requires Python 3.9 or above. On Windows, install the VC++ Redistributable before running.

Load the Chrome extension. Open Chrome and go to chrome://extensions. Enable Developer mode. Click Load unpacked and select the extension folder.

## Run
python main.py

Open the Chrome extension. Captions appear as you speak or play audio through your speakers.

## How it works

Mic and system audio each run in their own thread. Each thread measures loudness and decides when speech starts and ends. Clips are added to a shared queue. One transcription worker picks from the queue and runs the speech model once. Captions are sent live to the Chrome extension over a WebSocket.

## Tech stack

Audio capture, PyAudioWPatch. Signal processing, NumPy. Speech recognition, faster-whisper running locally on CPU. Backend, FastAPI with WebSockets. Frontend, Chrome extension using Manifest V3.

## Limitations

Loud non-speech sounds can occasionally trigger transcription. The model can struggle with uncommon technical words.

