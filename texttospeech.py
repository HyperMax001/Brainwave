from google.cloud import texttospeech
import pygame
import io
import time

# Initialize TTS client once at module level (reusing client saves 3-4 seconds per call)
_tts_client = None

def _get_tts_client():
    """Get or create the TTS client (singleton pattern)"""
    global _tts_client
    if _tts_client is None:
        _tts_client = texttospeech.TextToSpeechClient()
    return _tts_client

# Initialize pygame mixer once at module level
pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=512)

# Pre-configure voice settings (reuse across calls)
_voice_params = texttospeech.VoiceSelectionParams(
    language_code="en-IN",
    name="en-IN-Neural2-D"
)

# Use LINEAR16 for faster processing (no MP3 encoding overhead)
_audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    sample_rate_hertz=24000
)

def text_to_speech_live(text: str):
    """
    Convert text to speech and play it live without saving to file.
    Optimized for minimal latency.
    """
    if not text or text.strip() == "":
        return
    
    # Use the singleton client (avoids re-authentication overhead)
    client = _get_tts_client()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Synthesize speech with pre-configured settings
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=_voice_params,
        audio_config=_audio_config
    )

    # Load audio from bytes and play immediately
    audio_stream = io.BytesIO(response.audio_content)
    
    # Load and play with optimized settings
    pygame.mixer.music.load(audio_stream, 'wav')
    pygame.mixer.music.play()

    # Wait for audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)  # More efficient than time.sleep()


if __name__ == "__main__":
    text = (
        "This is a simple demonstration of Google Cloud Text to Speech. "
        "The audio you are hearing was generated using Application Default Credentials."
    )
    text_to_speech_live(text)
