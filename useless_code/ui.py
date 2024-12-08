import pyaudio
import websockets
import asyncio
import threading
import streamlit as st
import time
import queue
import uuid

# WebSocket URI for the transcription service (replace with your transcription server URL)
WEB_SOCKET_URI = "ws://localhost:8000/transcribe"

# Audio parameters
FORMAT = pyaudio.paInt16  # 16-bit format
CHANNELS = 1              # Mono
RATE = 16000              # 16kHz sample rate
CHUNK_SIZE = 1024         # Number of frames per buffer

class TranscriptionApp:
    def __init__(self):
        # Initialize unique key for text area to prevent Streamlit duplicate ID error
        self.text_area_key = f'transcript_area_{uuid.uuid4()}'
        
        # Initialize session state
        if 'transcripts' not in st.session_state:
            st.session_state.transcripts = []
        
        # Flags and queues
        self.is_recording = False
        self.transcript_queue = queue.Queue()
        self.stop_event = threading.Event()
        
        # Audio and WebSocket components
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
        self.websocket = None

    def audio_callback(self, in_data, frame_count, time_info, status):
        if self.is_recording and self.websocket:
            try:
                # Use asyncio to send data (this might need adjustment based on your WebSocket implementation)
                asyncio.run(self.websocket.send(in_data))
            except Exception as e:
                st.error(f"Error sending audio: {e}")
        return (in_data, pyaudio.paContinue)

    async def websocket_listener(self):
        try:
            async with websockets.connect(WEB_SOCKET_URI) as websocket:
                self.websocket = websocket
                while not self.stop_event.is_set():
                    try:
                        # Receive transcription with a timeout
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        
                        # Add to transcript queue
                        self.transcript_queue.put(message)
                        print(message)
                        
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        st.error(f"WebSocket error: {e}")
                        break
        except Exception as e:
            st.error(f"WebSocket connection error: {e}")

    def start_audio_stream(self):
        self.stream = self.pyaudio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
            stream_callback=self.audio_callback
        )
        self.stream.start_stream()

    def process_transcripts(self):
        # Process transcripts from the queue
        while not self.transcript_queue.empty():
            try:
                transcript = self.transcript_queue.get_nowait()
                if transcript:
                    # Update session state with new transcript
                    st.session_state.transcripts.append(transcript)
                    
                    # Limit transcript history
                    st.session_state.transcripts = st.session_state.transcripts[-10:]
                    print(st.session_state.transcripts)
            except queue.Empty:
                break

    def run(self):
        # Set up the Streamlit UI
        st.title("Live Transcription")

        # Transcript display with a unique key
        if st.session_state.transcripts:
            st.text_area(
                "Transcription", 
                value="\n".join(st.session_state.transcripts), 
                height=300, 
                disabled=True,
                key=self.text_area_key  # Added unique key here
            )

        # Recording control
        if st.button("Start/Stop Recording"):
            # Toggle recording state
            self.is_recording = not self.is_recording
            
            if self.is_recording:
                # Reset stop event and transcript state
                self.stop_event.clear()
                st.session_state.transcripts = []

                # Start audio stream
                self.start_audio_stream()

                # Start WebSocket listener in a separate thread
                listener_thread = threading.Thread(target=lambda: asyncio.run(self.websocket_listener()))
                listener_thread.start()

                st.success("Recording started...")
            else:
                # Stop recording
                self.stop_event.set()
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                st.warning("Recording stopped.")

        # Continuously update transcript display
        self.process_transcripts()

def main():
    app = TranscriptionApp()
    app.run()

if __name__ == "__main__":
    main()