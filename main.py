
from stream import GcpStream, MockStream
import uuid
from database import session, Transcript, Task, async_session, add_tasks_to_db
from sqlalchemy import desc, select
import streamlit as st
import uuid

from summeriser import process_transcription

import os 
import asyncio
from pydub import AudioSegment
import numpy as np
from whisper_transcriber import WhisperStream

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"


import argparse



mode = os.getenv("MODE", "mock")

if mode == "mock":
    streamer = MockStream()
else:
    streamer = GcpStream()


def convert_seconds_to_hhmmss(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{remaining_seconds:02}"




async def main():

    parser = argparse.ArgumentParser(description="Process a file input.")
    
    parser.add_argument('file', type=str, help="Path to the input file")

    args = parser.parse_args()
    

    id =str(uuid.uuid4())
    order = 0
    transcripts = []

    chunk_duration_ms = 2000
    audio = AudioSegment.from_file(args.file)

    audio = audio.set_channels(1).set_frame_rate(16000)

    whisper_stream = WhisperStream(model_size="base")

    context_size = 0
    for start_ms in range(0, len(audio), chunk_duration_ms):
        end_ms = min(start_ms + chunk_duration_ms, len(audio))
        chunk = audio[start_ms:end_ms]

        audio_chunk = np.array(chunk.get_array_of_samples(), dtype=np.float32)
        
        audio_chunk = audio_chunk / (2 ** 15)

        transcript = await whisper_stream.transcribe_chunk(audio_chunk)

        context_size +=1

        # Saving the transcript to the database
        print(transcript)
        if transcript:
            transcript_data = Transcript(client_id=id, transcription_text=transcript, order=order, start_stamp=start_ms)
            async with async_session() as session:
                session.add(transcript_data)
                await session.commit()
            transcripts.append(transcript)
            order += 1
            print(context_size)
            if context_size == 5:
                stmt = select(Transcript).filter_by(client_id=id).order_by(desc(Transcript.order)).limit(10)
                async with async_session() as async_session_temp:
                    result = await async_session_temp.execute(stmt)
                    latest_transcript = result.scalars().all()
               
                gpt_batch = [t.transcription_text for t in latest_transcript][::-1]

                gpt_transcipts = " ".join(gpt_batch)
                print(gpt_transcipts)

                try:
                    gpt_results = process_transcription(gpt_transcipts)

                    for i, gpt_result in enumerate(gpt_results):
                        print(f"completed task {i}: {gpt_result['task_description']}")
                except Exception as e:
                    print(e)

                context_size = 0

        print(f"Transcription: {transcript}")







def run():
    st.title("Live Audio Transcription")

    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg", "m4a"])

    if uploaded_file is not None:

        
        all_text = []
        box_id = str(uuid.uuid4())
        transcript_container = st.empty()
        id = str(uuid.uuid4())
        order = 0
        transcripts = []

        chunk_duration_ms = 2000
        audio = AudioSegment.from_file(uploaded_file)

        audio = audio.set_channels(1).set_frame_rate(16000)

        whisper_stream = WhisperStream(model_size="base")

        context_size = 0
        progress_bar = st.progress(0)
        total_chunks = len(range(0, len(audio), chunk_duration_ms))
        completed_tasks = {}
        for idx, start_ms in enumerate(range(0, len(audio), chunk_duration_ms)):
            end_ms = min(start_ms + chunk_duration_ms, len(audio))
            chunk = audio[start_ms:end_ms]

            audio_chunk = np.array(chunk.get_array_of_samples(), dtype=np.float32)
            audio_chunk = audio_chunk / (2 ** 15)

            transcript = asyncio.run(whisper_stream.transcribe_chunk(audio_chunk))

            context_size += 1
            
            if transcript:
                transcript_data = Transcript(client_id=id, transcription_text=transcript, order=order, start_stamp=start_ms)
                session.add(transcript_data)
                session.commit()
                transcripts.append(transcript)
                order += 1

                if context_size == 5:
                    stmt = select(Transcript).filter_by(client_id=id).order_by(desc(Transcript.order)).limit(10)
                    result = session.execute(stmt)
                    latest_transcript = result.scalars().all()

                    gpt_batch = [t.transcription_text for t in latest_transcript][::-1]
                    gpt_transcripts = " ".join(gpt_batch)

                    try:
                        gpt_results =process_transcription(gpt_transcripts)

                        for i, gpt_result in enumerate(gpt_results):
                            if gpt_result['task_description'] not in completed_tasks:
                                st.write(f"Completed task {i}: {gpt_result['task_description']}")

                                completed_tasks[gpt_result['task_description']] = gpt_result
                            
                    except Exception as e:
                        all_text.append(f"Error: chat gpt summary failed")
                    context_size = 0

                all_text.append(f"{convert_seconds_to_hhmmss(int(start_ms/1000))}: {transcript}")

                last_10_transcripts = all_text[-15:]
                transcript_container.text_area("Transcription", value="\n".join(last_10_transcripts), height=400)
                

            progress_bar.progress((idx + 1) / total_chunks)

        add_tasks_to_db(id, completed_tasks)

        st.success("Transcription completed.")

if __name__ == "__main__":
    run()
    