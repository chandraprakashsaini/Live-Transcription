import io
from pydub import AudioSegment



def split_audio_bytes(audio_bytes, chunk_length_ms=1000):
    """
    Splits a given audio byte array into smaller byte arrays.

    :param audio_bytes: The audio data in bytes
    :param chunk_length_ms: Length of each chunk in milliseconds
    :return: List of audio chunks as byte arrays
    """
    # Load the audio bytes into a Pydub AudioSegment
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

    # List to store the byte arrays of each chunk
    audio_chunks = []

    # Split the audio into chunks based on the provided chunk_length_ms
    for start in range(0, len(audio), chunk_length_ms):
        chunk = audio[start:start + chunk_length_ms]
        # Convert the chunk to byte format
        chunk_bytes = io.BytesIO()
        chunk.export(chunk_bytes, format="wav")  # Use the format you need (e.g., "wav")
        chunk_bytes.seek(0)
        audio_chunks.append(chunk_bytes.read())

    return audio_chunks




# A sample dictionary of topics with related phrases or sentences
topic_phrases = {
    "technology": [
        "Technology has advanced so much in the last few years.",
        "We are seeing new innovations every day, especially in AI.",
        "The development of 5G technology is going to change how we interact with devices.",
        "It's amazing how quickly the tech industry evolves.",
        "Artificial intelligence is transforming many sectors, from healthcare to finance.",
        "Self-driving cars are becoming more of a reality, which is both exciting and scary."
    ],
    "health": [
        "Taking care of your health is incredibly important.",
        "A balanced diet and regular exercise can have a huge impact on your well-being.",
        "Mental health is just as important as physical health.",
        "Incorporating mindfulness practices can help reduce stress.",
        "The pandemic really showed us the importance of hygiene and vaccination.",
        "Sleep is one of the most underrated aspects of good health."
    ],
    "environment": [
        "Climate change is one of the biggest challenges we face today.",
        "Reducing carbon emissions is crucial to mitigating the effects of global warming.",
        "Renewable energy sources like solar and wind are gaining popularity.",
        "We need to preserve our ecosystems to ensure biodiversity for future generations.",
        "Recycling and reducing waste can have a big impact on the environment.",
        "Deforestation is a major issue that affects the planet's health."
    ],
    "education": [
        "Education is the key to opening up opportunities for everyone.",
        "Online learning has become a major part of education, especially in the last few years.",
        "The traditional education system is evolving, with more emphasis on skills and creativity.",
        "Teachers play such an important role in shaping the future of students.",
        "Access to quality education is still a major challenge in many parts of the world.",
        "Lifelong learning is becoming increasingly important in the fast-changing job market."
    ]
}
