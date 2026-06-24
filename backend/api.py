import asyncio
import queue
import threading
from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
from backend.audio_source import AudioSource
from backend.worker import DualEngineWorker

app = FastAPI()

utterance_queue = queue.Queue()
caption_queue = queue.Queue()
connected_clients = []
main_loop = None

async def send_to_clients(item):
    living_clients = []
    for client in connected_clients:
        try:
            await client.send_json(item)
            living_clients.append(client)
        except Exception:
            pass
    connected_clients.clear()
    connected_clients.extend(living_clients)

def broadcast_loop():
    while True:
        item = caption_queue.get()
        if main_loop is not None:
            asyncio.run_coroutine_threadsafe(send_to_clients(item), main_loop)

@app.on_event("startup")
def start_pipeline():
    global main_loop
    main_loop = asyncio.get_event_loop()

    mic_source = AudioSource("microphone", utterance_queue, False)
    speaker_source = AudioSource("system_audio", utterance_queue, True)
    worker = DualEngineWorker(utterance_queue, caption_queue)

    mic_source.start()
    speaker_source.start()
    worker.start()

    threading.Thread(target=broadcast_loop, daemon=True).start()

@app.websocket("/captions")
async def caption_socket(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

@app.get("/sources")
def list_sources():
    return {"sources": ["microphone", "system_audio"]}

