import asyncio, traceback
import websockets

from io import BytesIO

from stream import GcpStream, MockStream
import uuid,os


mode = os.getenv("MODE", "mock")

if mode == "mock":
    streamer = MockStream()
else:
    streamer = GcpStream()




async def handle_transcription(websocket, path):

    while True:
        try:
            # Receive audio from the client (as bytes)
            # audio_data = await websocket.recv()

            # Process audio data using SpeechRecognition
            

            # Transcribe audio
            transcription = await streamer.streaming(audio_byes=None)
            print(f"Transcription: {transcription}")

            # Send transcription back to the client
            await websocket.send(transcription[0])

        except Exception as e:
            print(traceback.format_exc())
            print(f"Error during transcription: {e}")

async def main():
    server = await websockets.serve(handle_transcription, "localhost", 8000)
    await server.wait_closed()

# Start WebSocket server
asyncio.run(main())
