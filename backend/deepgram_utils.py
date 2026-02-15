import os
from dotenv import load_dotenv
import base64
from deepgram import DeepgramClient, PrerecordedOptions

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

async def transcribe_audio(audio_base64: str) -> tuple[str, float]:
    """
    Transcribe audio using Deepgram API
    
    Args:
        audio_base64: Base64 encoded audio data
        
    Returns:
        tuple: (transcript, confidence_score)
    """
    if not DEEPGRAM_API_KEY:
        return "Transcription not available (API key not configured)", 0.0
    
    try:
        # Initialize Deepgram client
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Prepare audio source
        source = {"buffer": audio_bytes}
        
        # Configure transcription options
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            language="en",
            punctuate=True,
        )
        
        # Transcribe audio
        response = deepgram.listen.prerecorded.v("1").transcribe_file(
            source,
            options
        )
        
        # Extract transcript and confidence
        if response and response.results:
            channels = response.results.channels
            if channels and len(channels) > 0:
                alternatives = channels[0].alternatives
                if alternatives and len(alternatives) > 0:
                    transcript = alternatives[0].transcript or ""
                    confidence = alternatives[0].confidence or 0.0
                    return transcript, confidence
        
        return "", 0.0
        
    except Exception as e:
        print(f"Deepgram transcription error: {e}")
        return "", 0.0
