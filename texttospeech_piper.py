"""
Piper TTS - Fast Local Text-to-Speech
Uses Piper for low-latency, offline speech synthesis
"""
import subprocess
import pygame
import os
import tempfile
import wave

# Initialize pygame mixer once at module level for fast playback
pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

# Piper executable path - update this after installation
PIPER_PATH = r"piper/piper.exe"  # Windows
# For Linux/Mac: PIPER_PATH = "./piper/piper"

# Voice model path - update this based on which voice you download
VOICE_MODEL = r"piper/voices/en_US-lessac-high.onnx"

def text_to_speech_live(text: str):
    """
    Convert text to speech using Piper and play it live.
    Ultra-fast, runs completely offline.
    
    Args:
        text: The text to convert to speech
    """
    if not text or text.strip() == "":
        return
    
    # Check if Piper is installed
    if not os.path.exists(PIPER_PATH):
        print(f"ERROR: Piper not found at {PIPER_PATH}")
        print("Please run the installation guide first!")
        return
    
    if not os.path.exists(VOICE_MODEL):
        print(f"ERROR: Voice model not found at {VOICE_MODEL}")
        print("Please download a voice model first!")
        return
    
    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
        temp_wav_path = temp_wav.name
    
    try:
        # Run Piper to generate audio
        # Piper reads from stdin and outputs to stdout
        process = subprocess.Popen(
            [PIPER_PATH, "--model", VOICE_MODEL, "--output_file", temp_wav_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send text to Piper
        stdout, stderr = process.communicate(input=text, timeout=5)
        
        if process.returncode != 0:
            print(f"Piper error: {stderr}")
            return
        
        # Play the generated audio
        pygame.mixer.music.load(temp_wav_path)
        pygame.mixer.music.play()
        
        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
            
    except subprocess.TimeoutExpired:
        print("Piper timed out - text might be too long")
        process.kill()
    except Exception as e:
        print(f"Error during TTS: {e}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_wav_path):
            try:
                os.unlink(temp_wav_path)
            except:
                pass  # File might still be in use


def test_piper():
    """Test if Piper is properly installed and configured"""
    print("Testing Piper TTS...")
    print(f"Piper path: {PIPER_PATH}")
    print(f"Voice model: {VOICE_MODEL}")
    print(f"Piper exists: {os.path.exists(PIPER_PATH)}")
    print(f"Voice exists: {os.path.exists(VOICE_MODEL)}")
    
    if os.path.exists(PIPER_PATH) and os.path.exists(VOICE_MODEL):
        print("\n✓ Piper is properly configured!")
        print("Testing speech output...")
        text_to_speech_live("Hello! This is a test of Piper text to speech. It's running locally on your computer.")
    else:
        print("\n✗ Piper is not properly configured.")
        print("Please follow the installation guide.")


if __name__ == "__main__":
    test_piper()
