import threading
import wave
from faster_whisper import WhisperModel

TEMP_WAV = "echoscribe_temp_utterance.wav"

def save_wav(frames, rate):
    wf = wave.open(TEMP_WAV, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
    wf.close()

class TranscriptionWorker(threading.Thread):
    def __init__(self, input_queue, output_queue):
        threading.Thread.__init__(self, daemon=True)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.running = True
        print("loading speech to text model")
        self.model = WhisperModel("base.en", device="cpu", compute_type="int8")
        print("model loaded")

    def run(self):
        while self.running:
            item = self.input_queue.get()
            save_wav(item["frames"], item["rate"])
            segments, info = self.model.transcribe(
                TEMP_WAV, vad_filter=True, condition_on_previous_text=False
            )
            text = ""
            for segment in segments:
                text = text + segment.text
            text = text.strip()
            if text:
                self.output_queue.put({
                    "source": item["source"],
                    "timestamp": item["timestamp"],
                    "text": text,
                })

    def stop(self):
        self.running = False


        