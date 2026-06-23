import pyaudiowpatch as pyaudio
import numpy as np
from datetime import datetime

CHUNK = 1024
RATE = 44100
THRESHOLD = 40

def compute_rms(data):
    audio = np.frombuffer(data, dtype=np.int16).astype(np.float64)
    if len(audio) == 0:
        return 0.0
    return np.sqrt(np.mean(audio ** 2))

def main():
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
    log_file = open("echoscribe_audio_log.jsonl", "a")

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            rms = compute_rms(data)
            timestamp = datetime.now().isoformat()
            if rms > THRESHOLD:
                entry = timestamp + ", rms " + str(round(rms, 2)) + ", sound detected"
                print(entry)
                log_file.write(entry + "\n")
                log_file.flush()
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    p.terminate()
    log_file.close()

if __name__ == "__main__":
    main()


