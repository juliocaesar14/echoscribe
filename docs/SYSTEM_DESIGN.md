Speech to text model choice.
Tried tiny.en first, fast but produced repeated word loops on noise and weak accuracy on quiet speech.
Fixed loops using vad_filter and condition_on_previous_text false.
Fixed quiet speech volume using manual gain normalization before transcription.
Switched to base.en for better accuracy on quiet audio, accepted slightly higher latency per caption as the tradeoff.


