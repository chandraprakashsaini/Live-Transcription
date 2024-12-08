
from useless_code.utils import split_audio_bytes

from stream import GcpStream, MockStream
import uuid
from database import session, Transcript, Task

from summeriser import process_transcription

import os 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/cp_/temp/service-account.json"


import argparse



mode = os.getenv("MODE", "mock")

if mode == "mock":
    streamer = MockStream()
else:
    streamer = GcpStream()



def read_audio_file(file_path: str) -> bytes:
    with open(file_path, "rb") as audio_file:
        return audio_file.read()
    
async def main():

    parser = argparse.ArgumentParser(description="Process a file input.")
    
    parser.add_argument('file', type=str, help="Path to the input file")

    args = parser.parse_args()
    
    audio_bytes = read_audio_file(args.file)

    audio_chunks = split_audio_bytes(audio_bytes)

    id =str(uuid.uuid4())
    order = 0
    transcripts = []


    for audio_chunk in audio_chunks:
        print("Sending a chunk of audio")
        transcript = await streamer.streaming(audio_chunk)
        print(transcript[0])
        context_size = 0

        # Saving the transcript to the database
        print(transcript[1])
        if transcript[1]:
            transcript_db = Transcript(client_id=id, transcription_text=transcript[0], order=order)
            session.add(transcript_db)
            session.commit()
            print("Transcript saved to the database")
            transcripts.append(transcript[0])
            order += 1
            context_size += 1

            if context_size == 5:
                latest_transcript = session.query(Transcript).filter_by(client_id=id).order_by(Transcript.order.desc).limit(10).all()

                gpt_batch = [t.transcription_text for t in latest_transcript][::-1]

                gpt_transcipts = "/n".join(gpt_batch)

                gpt_results = await process_transcription(gpt_transcipts)

                for i, gpt_result in enumerate(gpt_results):
                    print(f"completed task {i}: {gpt_result['task_description']}")

                context_size = 0

            
        
            



        

        

    # Return or print the collected transcripts
    print("All transcripts:", transcripts)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())