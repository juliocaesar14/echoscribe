import os
import sys
import uvicorn

def check_devices():
    try:
        import pyaudiowpatch as pyaudio
        p = pyaudio.PyAudio()
        p.get_default_input_device_info()
        p.terminate()
    except Exception:
        print("ERROR: No microphone found. Please connect a microphone and try again.")
        sys.exit(1)

def check_vosk_model():
    model_path = os.path.join(os.path.dirname(__file__), "models", "vosk-model-en-us")
    if not os.path.isdir(model_path):
        print("Vosk model not found. Run: python download_vosk_model.py")
        sys.exit(1)

if __name__ == "__main__":
    check_devices()
    check_vosk_model()
    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, reload=False)

    