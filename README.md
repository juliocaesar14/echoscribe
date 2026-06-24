# Echoscribe

captures your mic and your system audio at the same time, runs both through speech to text locally, and pushes live captions to a chrome extension. no cloud, nothing leaves your machine.

windows only for now, it relies on PyAudioWPatch for the WASAPI loopback trick that grabs system audio.

## Setup

bashgit clone https://github.com/juliocaesar14/echoscribe.git
cd echoscribe
pip install -r requirements.txt
python download_vosk_model.py
python main.py

then go to chrome://extensions, turn on dev mode, load unpacked, point it at the extension folder. open the popup and start talking.

## How it works

mic and system audio each get their own thread doing basic energy threshold VAD. finished clips land on a shared queue. one worker thread pulls from that queue and runs each clip through vosk and whisper at the same time using a thread pool, so a slow whisper pass doesn't hold up vosk. whatever comes back gets broadcast over a websocket to the extension, tagged with which engine produced it.

there's a lock around just the pyaudio setup step, starting both streams at the exact same moment used to crash the whole thing and that one took a while to track down.

# Structure

backend has the actual logic, api.py for the websocket server, audio_source.py for capture and VAD, worker.py for the vosk plus whisper pipeline. extension is the chrome side. models is where the vosk model goes once you run the download script. audio is leftover day one code, haven't cleaned it out yet.

# Rough edges

only two sources for now, mic and system audio, by design. loud non-speech stuff like music or notification sounds occasionally gets transcribed like it's a sentence. no real test suite, test_client.py is just something I run by hand to watch the websocket output. requirements.txt was saved on windows so it might be utf-16, re-save as utf-8 if pip throws a fit.

## Next

streaming partial results from vosk instead of waiting for a full clip to finish, vosk already supports this, just haven't wired it through yet. after that, picking one engine instead of always running both, right now you get both results side by side which is great for debugging and kind of noisy for actual use.

