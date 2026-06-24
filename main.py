
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

if __name__ == "__main__":
    check_devices()
    print("Starting Echoscribe...")
    uvicorn.run("backend.echoscribe_api:app", host="127.0.0.1", port=8000, reload=False)
EOF




