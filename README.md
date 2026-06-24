# Echoscribe

Live captions from your microphone and your system audio, generated entirely on your machine, with no cloud and no API key.

## Project structure

The root holds main.py, start dot bat and requirements.txt. The audio folder holds audio_capture.py and transcriber.py for capturing and converting sound into text. The backend folder holds api.py, audio_source.py, worker.py and test_client.py, which run the FastAPI server and the transcription worker. The extension folder holds manifest.json, popup.html and popup.js, the Chrome extension that shows the captions. The docs folder holds SYSTEM_DESIGN.md.

## Install

Clone the repository and move into the project folder, then install the dependencies in requirements.txt using pip. Python 3.9 or above is required, and Windows users need the VC++ Redistributable installed first. Load the extension by opening Chrome, going to the extensions page, enabling developer mode, then choosing load unpacked and selecting the extension folder.

## Run

Run main.py with Python to start the backend, then open the Chrome extension. Captions appear live as you speak or as audio plays through your speakers.

## How it works

Microphone and system audio each run in their own thread, measuring loudness to detect when speech starts and ends. Finished clips go into a shared queue, where a single transcription worker processes them with the speech model. Captions are sent live to the Chrome extension over a WebSocket, labeled by source.

## Tech stack

Audio capture uses PyAudioWPatch, signal processing uses NumPy, speech recognition runs locally on CPU with faster whisper, the backend is built on FastAPI and WebSockets, and the frontend is a Chrome extension on Manifest V3.

## Limitations

Loud non speech sounds can occasionally trigger an unwanted transcription, and the model can struggle with uncommon technical words.

## Phase two

Vosk is planned as a second, streaming capable speech engine alongside faster whisper, returning partial words as audio comes in to reduce caption delay, with either engine selectable depending on speed or accuracy needs. Support for audio sources beyond the current two fixed ones is also planned.

