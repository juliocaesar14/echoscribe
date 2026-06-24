import pyaudiowpatch as pyaudio
import numpy as np
import wave
import json
from datetime import datetime
from faster_whisper import WhisperModel

CHUNK = 1024
RATE = 44100
THRESHOLD = 30
SILENCE_CHUNKS_TO_END = 50
TEMP_WAV = "echoscribe_temp_utterance.wav"
CAPTIONS_LOG = "echoscribe_captions_log.jsonl"

def compute_rms(data):
    audio = np.frombuffer(data, dtype=np.int16).astype(np.float64)
    if len(audio) == 0:
        return 0.0
    return np.sqrt(np.mean(audio ** 2))

def normalize_audio(frames):
    audio = np.frombuffer(b"".join(frames), dtype=np.int16).astype(np.float64)
    peak = np.max(np.abs(audio))
    if peak == 0:
        return frames
    target_peak = 32767 * 0.9
    gain = target_peak / peak
    audio = audio * gain
    audio = np.clip(audio, -32768, 32767).astype(np.int16)
    return [audio.tobytes()]

def save_wav(frames, rate):
    wf = wave.open(TEMP_WAV, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
    wf.close()

def main():
    print("loading speech to text model")
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    print("model loaded")

    p = pyaudio.PyAudio()
    device = p.get_default_input_device_info()
    print("using device", device["name"])

    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        input_device_index=device["index"],
        frames_per_buffer=CHUNK,
    )

    print("listening, press control c to stop")

    buffer = []
    silence_count = 0
    is_speaking = False

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            rms = compute_rms(data)

            if rms > THRESHOLD:
                buffer.append(data)
                is_speaking = True
                silence_count = 0
            elif is_speaking:
                buffer.append(data)
                silence_count = silence_count + 1
                if silence_count > SILENCE_CHUNKS_TO_END:
                    normalized = normalize_audio(buffer)
                    save_wav(normalized, RATE)
                    segments, info = model.transcribe(TEMP_WAV, vad_filter=True, condition_on_previous_text=False)
                    text = ""
                    for segment in segments:
                        text = text + segment.text
                    text = text.strip()
                    if text:
                        timestamp = datetime.now().isoformat()
                        print(timestamp, ", caption, ", text)
                        entry = {"timestamp": timestamp, "text": text}
                        with open(CAPTIONS_LOG, "a") as f:
                            f.write(json.dumps(entry) + "\n")
                    buffer = []
                    is_speaking = False
                    silence_count = 0
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main()



