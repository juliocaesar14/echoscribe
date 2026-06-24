Echoscribe

Real time, multi source audio captioning that runs entirely on your machine.

Echoscribe listens to your microphone and system audio at the same time and turns speech from both into live captions. No cloud, no internet, nothing leaves your device.

GitHub Repository, https://github.com/juliocaesar14/echoscribe


What it does

Echoscribe captures mic and system audio at the same time. It detects speech using a tuned energy threshold that works even on quiet voices. It transcribes locally using a speech recognition model with no API key needed. It streams live captions to a Chrome extension and keeps the two audio sources labelled separately.


Project structure

echoscribe/
├── main.py
├── transcriber.py
├── audio_capture.py
├── requirements.txt
└── extension/
├── manifest.json
├── popup.html
└── popup.js


Installation

Step 1. Clone the repo.

git clone https://github.com/juliocaesar14/echoscribe.git
cd echoscribe

Step 2. Install Python dependencies.

pip install -r requirements.txt

Requires Python 3.9 or above. On Windows, make sure you have the VC++ Redistributable installed, which is needed by faster whisper.

Step 3. Load the Chrome extension.

Open Chrome and go to chrome://extensions. Enable Developer mode in the top right. Click Load unpacked and select the extension folder.


How to run

python main.py

This starts the backend. Open the Chrome extension and you will see live captions appear as you speak or play audio through your speakers.


How it works

Microphone and system audio each run in their own thread. Each thread listens for sound, measures loudness, and decides when speech starts and ends. When a clip is ready it gets added to a shared queue. A single transcription worker picks clips from the queue, runs the speech model once, and keeps it shared across both sources. Finished captions are sent live over a websocket to the Chrome extension.


Tech stack

Audio capture, Python and PyAudioWPatch for Windows system audio loopback.
Signal processing, NumPy for energy detection and gain normalisation.
Speech recognition, faster whisper running locally on CPU with no cloud dependency.
Backend, FastAPI with websockets and a multi threaded producer consumer pipeline.
Frontend, Chrome extension using Manifest V3.
Version control, Git and GitHub.


Known limitations

Loud non speech sounds like music or notifications can occasionally trigger a transcription attempt. The model can struggle with uncommon technical words. The system currently supports two fixed sources, microphone and system audio, by design.


CV summary

Designed and built a real time, multi source audio captioning system that runs entirely on device. Captures microphone and system audio simultaneously via OS level audio APIs, detects speech at low volume using a tuned signal energy threshold, and transcribes locally using a CPU based speech recognition model. Diagnosed and fixed a native level multi threading race condition. Exposed live captions through a FastAPI websocket backend with a Chrome extension frontend.

Resume bullet points

Built a real time captioning pipeline capturing two simultaneous audio streams, microphone and system audio, using direct OS audio APIs.

Implemented signal energy based speech detection, tuned through real testing to reliably capture low volume speech.

Integrated and tuned a local, CPU based speech recognition model, improving accuracy through audio normalisation and a deliberate model size tradeoff.

Diagnosed and resolved a native level multi threading race condition in the audio capture layer.

Designed a multi threaded producer consumer backend with a shared model worker, exposing live captions over a websocket API.


Future plans

Vosk integration is planned as an alternative speech recognition engine. Vosk supports streaming recognition, meaning it can return partial results word by word as audio comes in rather than waiting for a full clip to finish. This would significantly reduce caption latency. The plan is to add it alongside faster whisper so either engine can be selected depending on whether accuracy or speed is the priority.


