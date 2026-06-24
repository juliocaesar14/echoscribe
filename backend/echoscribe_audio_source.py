import threading
import numpy as np
import pyaudiowpatch as pyaudio
from datetime import datetime

pyaudio_lock = threading.Lock()

CHUNK = 1024
THRESHOLD = 30
SILENCE_CHUNKS_TO_END = 43
MAX_BUFFER_CHUNKS = 260

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

class AudioSource(threading.Thread):
    def __init__(self, source_name, output_queue, is_loopback):
        threading.Thread.__init__(self, daemon=True)
        self.source_name = source_name
        self.output_queue = output_queue
        self.is_loopback = is_loopback
        self.running = True

    def get_device(self, p):
        if not self.is_loopback:
            return p.get_default_input_device_info()
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        if not default_speakers["isLoopbackDevice"]:
            for loopback in p.get_loopback_device_info_generator():
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
        return default_speakers

    def run(self):
        with pyaudio_lock:
            p = pyaudio.PyAudio()
            device = self.get_device(p)
            channels = device["maxInputChannels"]
            rate = int(device["defaultSampleRate"])

            stream = p.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                input=True,
                input_device_index=device["index"],
                frames_per_buffer=CHUNK,
            )

        buffer = []
        silence_count = 0
        is_speaking = False

        while self.running:
            data = stream.read(CHUNK, exception_on_overflow=False)
            if channels > 1:
                audio = np.frombuffer(data, dtype=np.int16).reshape(-1, channels)
                data = audio.mean(axis=1).astype(np.int16).tobytes()

            rms = compute_rms(data)

            if rms > THRESHOLD:
                buffer.append(data)
                is_speaking = True
                silence_count = 0
                if len(buffer) >= MAX_BUFFER_CHUNKS:
                    self.output_queue.put({
                        "source": self.source_name,
                        "frames": normalize_audio(buffer),
                        "rate": rate,
                        "timestamp": datetime.now().isoformat(),
                    })
                    buffer = []
            elif is_speaking:
                buffer.append(data)
                silence_count = silence_count + 1
                if silence_count > SILENCE_CHUNKS_TO_END:
                    self.output_queue.put({
                        "source": self.source_name,
                        "frames": normalize_audio(buffer),
                        "rate": rate,
                        "timestamp": datetime.now().isoformat(),
                    })
                    buffer = []
                    is_speaking = False
                    silence_count = 0

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self.running = False


