import os
import urllib.request
import zipfile

URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
ZIP_NAME = "vosk-model-small-en-us-0.15.zip"
INNER_DIR = "vosk-model-small-en-us-0.15"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "models", "vosk-model-en-us")

def progress(count, block_size, total):
    mb = count * block_size / 1048576
    pct = min(count * block_size / total * 100, 100)
    print(f"\r{pct:.1f}% ({mb:.1f} MB)", end="", flush=True)

if os.path.isdir(TARGET_DIR):
    print("Model already exists at " + TARGET_DIR)
else:
    zip_path = os.path.join(os.path.dirname(__file__), ZIP_NAME)
    urllib.request.urlretrieve(URL, zip_path, reporthook=progress)
    print()
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(os.path.join(os.path.dirname(__file__), "models"))
    extracted = os.path.join(os.path.dirname(__file__), "models", INNER_DIR)
    os.rename(extracted, TARGET_DIR)
    os.remove(zip_path)
    print("Done. Model saved to " + TARGET_DIR)

    