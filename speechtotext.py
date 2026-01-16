import sounddevice as sd
import numpy as np
import whisper
import webrtcvad

def speech_to_text():
    # ---------------- CONFIG ----------------
    SAMPLE_RATE = 16000
    FRAME_DURATION = 30  # ms
    FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)
    SILENCE_DURATION = 1.5  # seconds
    VAD_MODE = 2  # aggressive
    MODEL_SIZE = "small"
    NOISE_GATE = 500  # int16 units
    # ---------------------------------------

    vad = webrtcvad.Vad(VAD_MODE)
    model = whisper.load_model(MODEL_SIZE)

    audio_buffer = []
    required_silence_frames = int(SILENCE_DURATION * 1000 / FRAME_DURATION)

    print("Listening... Speak and pause.")
    check = True

    with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=FRAME_SIZE,
            dtype="int16",
            channels=1
    ) as stream:
        in_speech = False
        voiced_frames = 0
        silence_frames = 0

        MIN_VOICED_FRAMES = int(0.25 * 1000 / FRAME_DURATION)  # 250 ms

        while check:
            frame, _ = stream.read(FRAME_SIZE)

            # -------- RAW AUDIO (for Whisper) --------
            raw_int16 = np.frombuffer(frame, dtype=np.int16)
            raw_bytes = raw_int16.tobytes()

            # -------- CLEAN AUDIO (for VAD only) -----
            vad_audio = raw_int16.astype(np.float32)
            vad_audio -= vad_audio.mean()  # DC removal
            vad_audio[np.abs(vad_audio) < 100] = 0  # light gate
            vad_bytes = vad_audio.astype(np.int16).tobytes()
            # -----------------------------------------

            is_speech = vad.is_speech(vad_bytes, SAMPLE_RATE)
            # print("Speech:", is_speech)

            if is_speech:
                audio_buffer.append(raw_bytes)  # STORE RAW AUDIO
                voiced_frames += 1
                silence_frames = 0

                if voiced_frames >= MIN_VOICED_FRAMES:
                    in_speech = True
            else:
                if in_speech:
                    silence_frames += 1

            if in_speech and silence_frames >= required_silence_frames:
                print("Processing...")

                audio_np = np.frombuffer(
                    b"".join(audio_buffer),
                    dtype=np.int16
                ).astype(np.float32) / 32768.0

                # Reset state
                audio_buffer = []
                voiced_frames = 0
                silence_frames = 0
                in_speech = False

                duration = len(audio_np) / SAMPLE_RATE
                # print("Audio seconds:", duration)

                if duration < 0.7:
                    print("Too short, skipping")
                    continue
                else:
                    check = False
                # VERY IMPORTANT: pad a bit of silence

                audio_np = np.concatenate([
                    audio_np,
                    np.zeros(int(0.2 * SAMPLE_RATE), dtype=np.float32)
                ])

                result = model.transcribe(
                    audio_np,
                    language="en",
                    fp16=False,
                    temperature=0.0,
                    condition_on_previous_text=False
                )

                # print("RAW WHISPER OUTPUT:", result)

                text = result["text"].strip()
                if text:
                    # print(">>", text)
                    return text  # Return only the string, not the full result dict
                else:
                    """Whisper returned empty text"""
                    # print("Whisper returned empty text")
                    return None