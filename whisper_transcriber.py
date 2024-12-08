import whisper
import asyncio
from pydub import AudioSegment
import numpy as np
import torch


class WhisperStream:
    def __init__(self, model_size="base"):
        """
        Initializes the WhisperStream object and loads the Whisper model.
        
        :param model_size: The size of the Whisper model (base, small, medium, large)
        """
        self.model = whisper.load_model(model_size)
        
    async def transcribe_chunk(self, audio_chunk: np.ndarray) -> str:
        """
        Asynchronously transcribes an audio chunk using the Whisper model.

        :param audio_chunk: Audio chunk as a numpy array (should be in float32 format)
        :return: Transcribed text from the audio chunk
        """
        # Convert audio chunk to a tensor and move it to the appropriate device (CPU/GPU)
        audio_tensor = torch.tensor(audio_chunk).float()
        
        # Perform the transcription asynchronously
        loop = asyncio.get_event_loop()
        transcript = await loop.run_in_executor(None, self._transcribe, audio_tensor)
        
        return transcript

    def _transcribe(self, audio_chunk: torch.Tensor) -> str:
        """
        Synchronously transcribes audio using the Whisper model.
        
        This is a helper function used in the async function to run transcription in a non-blocking way.
        
        :param audio_chunk: Audio chunk as a torch tensor
        :return: Transcribed text from the audio chunk
        """
        # Run the Whisper model and get the transcription
        result = self.model.transcribe(audio_chunk.numpy())
        
        # Return the transcribed text
        return result["text"]

async def transcribe_audio_file_live(file_path: str, chunk_duration_ms: int = 2000):
    """
    Transcribes an audio file in real-time using WhisperStream.

    :param file_path: Path to the audio file
    :param chunk_duration_ms: Duration of each chunk in milliseconds (default is 1000 ms, or 1 second)
    """
    audio = AudioSegment.from_file(file_path)

    audio = audio.set_channels(1).set_frame_rate(16000)

    whisper_stream = WhisperStream(model_size="base")

    
    # Iterate over the audio in chunks and transcribe
    for start_ms in range(0, len(audio), chunk_duration_ms):
        end_ms = min(start_ms + chunk_duration_ms, len(audio))
        chunk = audio[start_ms:end_ms]

        audio_chunk = np.array(chunk.get_array_of_samples(), dtype=np.float32)
        
        audio_chunk = audio_chunk / (2 ** 15)

        transcript = await whisper_stream.transcribe_chunk(audio_chunk)
        print(f"Transcription: {transcript}")



if __name__ == "__main__":
    asyncio.run(transcribe_audio_file_live("sample.wav"))
