from abc import ABC, abstractmethod


class GenerateTranscript(ABC):

    @abstractmethod
    async def streaming(self, audio_byes: bytes):
        pass