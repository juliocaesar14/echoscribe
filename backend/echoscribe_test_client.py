import asyncio
import websockets

async def listen():
    uri = "ws://127.0.0.1:8000/captions"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(message)

asyncio.run(listen())


