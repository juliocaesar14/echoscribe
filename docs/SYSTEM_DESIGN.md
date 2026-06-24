Speech to text model choice.
Tried tiny.en first, fast but produced repeated word loops on noise and weak accuracy on quiet speech.
Fixed loops using vad_filter and condition_on_previous_text false.
Fixed quiet speech volume using manual gain normalization before transcription.
Switched to base.en for better accuracy on quiet audio, accepted slightly higher latency per caption as the tradeoff.


Backend and concurrency.
Microphone and system audio run as two separate threads, each detecting and splitting its own speech.
Both send finished clips to one shared queue. One worker thread picks these up and runs them through the speech model, so the model loads once and is shared, not duplicated per source.
Both threads crashed the app when they started at the same exact moment, since the audio library underneath is not safe for that. Fixed by locking just the startup step so they set up one after another, while the actual listening still runs fully in parallel after that.
Finished captions are sent out to anyone listening over a websocket, so the audio pipeline and whatever displays the captions stay separate from each other.
