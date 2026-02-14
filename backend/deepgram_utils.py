import os
from deepgram import DeepgramClient
from dotenv import load_dotenv
import base64

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

def transcribe_audio(audio_base64: str) -> tuple[str, float]:
    """
    Transcribe audio using Deepgram API
    
    Args:
        audio_base64: Base64 encoded audio data
        
    Returns:
        tuple: (transcript, confidence_score)
    """
    if not DEEPGRAM_API_KEY:
        raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
    
    try:
        # Initialize Deepgram client with SDK 5.x API
        deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Transcribe audio using SDK 5.x API - all options as keyword arguments
        response = deepgram.listen.v1.media.transcribe_file(
            request=audio_bytes,
            model="nova-3",
            smart_format=True,
            language="en",
            punctuate=True,
        )
        
        # Extract transcript and confidence
        if response and hasattr(response, 'results'):
            results = response.results
            if hasattr(results, 'channels') and len(results.channels) > 0:
                channel = results.channels[0]
                if hasattr(channel, 'alternatives') and len(channel.alternatives) > 0:
                    alternative = channel.alternatives[0]
                    transcript = alternative.transcript if hasattr(alternative, 'transcript') else ""
                    confidence = alternative.confidence if hasattr(alternative, 'confidence') else 0.0
                    return transcript, confidence
        
        return "", 0.0
        
    except Exception as e:
        print(f"Deepgram transcription error: {e}")
        raise Exception(f"Transcription failed: {str(e)}")
