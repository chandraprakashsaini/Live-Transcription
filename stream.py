from google.cloud import speech_v2



from streamer import GenerateTranscript
import asyncio
import random
import time
from useless_code.utils import topic_phrases

class GcpStream(GenerateTranscript):


    async def streaming(self, audio_byes: bytes):
        # Create a client
        client = speech_v2.SpeechAsyncClient()

        # Initialize request argument(s)
        request = speech_v2.StreamingRecognizeRequest(
            recognizer="recognizer_value",
            audio = audio_byes,
        )

        # This method expects an iterator which contains
        # 'speech_v2.StreamingRecognizeRequest' objects
        # Here we create a generator that yields a single `request` for
        # demonstrative purposes.
        requests = [request]

        def request_generator():
            for request in requests:
                yield request

        # Make the request
        stream = await client.streaming_recognize(requests=request_generator())

        # Handle the response
        async for response in stream:
            print(response)


class MockStream(GenerateTranscript):

    async def streaming(self, audio_byes: bytes = None):

        topics = ["technology", "health", "environment", "education"]

        # Choose a random topic
        topic = random.choice(topics)

        streaming_duration = 30

        delay_range = (2, 4)  # Range of delays between phrases

        if topic not in topic_phrases:
            print("Sorry, I don't have information on that topic.")
            return

    # Get the list of phrases related to the given topic
        phrases = topic_phrases[topic]
        
        start_time = time.time()
        while time.time() - start_time < streaming_duration:
            # Randomly select a phrase from the topic's list
            phrase = random.choice(phrases)
            for response in phrase.split(" "):
                print(response, False)
                await asyncio.sleep(random.uniform(0.1,0.25))
            print(phrase, True)
            return phrase, True
            
            # break
        
        
            # await asyncio.sleep(random.uniform(*delay_range))
        