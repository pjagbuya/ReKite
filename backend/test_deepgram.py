import os
from deepgram import DeepgramClient
from dotenv import load_dotenv
import base64

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
print(f"API Key loaded: {DEEPGRAM_API_KEY[:20]}..." if DEEPGRAM_API_KEY else "No API key found")

try:
    # Initialize client - try with api_key as keyword argument
    deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
    print("✓ DeepgramClient initialized")
    
    # Create a simple test audio (silence)
    # Generate 1 second of silence (WAV format)
    import struct
    sample_rate = 16000
    duration = 1
    num_samples = sample_rate * duration
    
    # WAV header
    wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + num_samples * 2,
        b'WAVE',
        b'fmt ',
        16, 1, 1,
        sample_rate,
        sample_rate * 2,
        2, 16,
        b'data',
        num_samples * 2
    )
    
    # Silence audio data
    audio_data = b'\x00\x00' * num_samples
    audio_bytes = wav_header + audio_data
    
    print(f"✓ Test audio created ({len(audio_bytes)} bytes)")
    
    # Try to transcribe using SDK 5.x API
    print("Attempting transcription...")
    response = deepgram.listen.v1.media.transcribe_file(
        request=audio_bytes,
        model="nova-2",
        smart_format=True,
        language="en",
        punctuate=True,
    )
    print(f"✓ Response received: {type(response)}")
    print(f"Response attributes: {dir(response)}")
    
    if hasattr(response, 'results'):
        print(f"✓ Has results: {response.results}")
        
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
