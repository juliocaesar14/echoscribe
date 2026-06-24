import io
import json
import os
import tempfile
import threading
import uuid
import wave
from concurrent.futures import ThreadPoolExecutor
from faster_whisper import WhisperModel
from vosk import Model, KaldiRecognizer, SetLogLevel


VOSK_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "vosk-model-en-us")


def frames_to_wav_bytes(frames, rate):
    buf = io.BytesIO()
    wf = wave.open(buf, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
    wf.close()
    buf.seek(0)
    return buf


class VoskEngine:
    def __init__(self):
        SetLogLevel(-1)
        self.model = Model(VOSK_MODEL_PATH)

    def transcribe(self, frames, rate):
        rec = KaldiRecognizer(self.model, rate)
        rec.SetWords(True)
        rec.SetPartialWords(True)
        buf = frames_to_wav_bytes(frames, rate)
        buf.seek(44)
        results = []
        while True:
            chunk = buf.read(4000)
            if not chunk:
                break
            if rec.AcceptWaveform(chunk):
                text = json.loads(rec.Result()).get("text", "").strip()
                if text:
                    results.append({"text": text, "is_final": True})
            else:
                text = json.loads(rec.PartialResult()).get("partial", "").strip()
                if text:
                    results.append({"text": text, "is_final": False})
        text = json.loads(rec.FinalResult()).get("text", "").strip()
        if text:
            results.append({"text": text, "is_final": True})
        return results


class WhisperEngine:
    def __init__(self):
        self.model = WhisperModel("base.en", device="cpu", compute_type="int8")
        self.lock = threading.Lock()

    def transcribe(self, frames, rate):
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp.name
        tmp.close()
        wf = wave.open(tmp_path, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b"".join(frames))
        wf.close()
        with self.lock:
            segments, _ = self.model.transcribe(
                tmp_path, vad_filter=True, condition_on_previous_text=False
            )
            text = "".join(s.text for s in segments).strip()
        os.unlink(tmp_path)
        return text


class DualEngineWorker(threading.Thread):
    def __init__(self, input_queue, output_queue):
        threading.Thread.__init__(self, daemon=True)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.running = True
        self.vosk = VoskEngine()
        self.whisper = WhisperEngine()
        self.pool = ThreadPoolExecutor(max_workers=4)

    def run_vosk(self, item, uid):
        results = self.vosk.transcribe(item["frames"], item["rate"])
        for r in results:
            self.output_queue.put({
                "source": item["source"],
                "timestamp": item["timestamp"],
                "utterance_id": uid,
                "engine": "vosk",
                "text": r["text"],
                "is_final": r["is_final"],
            })

    def run_whisper(self, item, uid):
        text = self.whisper.transcribe(item["frames"], item["rate"])
        if text:
            self.output_queue.put({
                "source": item["source"],
                "timestamp": item["timestamp"],
                "utterance_id": uid,
                "engine": "whisper",
                "text": text,
                "is_final": True,
            })

    def run(self):
        while self.running:
            item = self.input_queue.get()
            uid = str(uuid.uuid4())
            self.pool.submit(self.run_vosk, item, uid)
            self.pool.submit(self.run_whisper, item, uid)

    def stop(self):
        self.running = False
        self.pool.shutdown(wait=False)


        