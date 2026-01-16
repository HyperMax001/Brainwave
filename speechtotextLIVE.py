import sounddevice as sd
import numpy as np
import whisper
import queue
import time

SAMPLE_RATE = 16000
CHUNK_DURATION = 2  # seconds
CHUNK_SIZE = SAMPLE_RATE * CHUNK_DURATION

audio_queue = queue.Queue()

model = whisper.load_model("tiny")  # use "base" for higher accuracy

def audio_callback(indata, frames, time_info, status):
    audio_queue.put(indata.copy())

stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
    callback=audio_callback
)

print("Listening... Ctrl+C to stop")

buffer = np.zeros((0,), dtype=np.float32)

with stream:
    while True:
        audio = audio_queue.get()
        buffer = np.concatenate((buffer, audio.flatten()))

        if len(buffer) >= CHUNK_SIZE:
            chunk = buffer[:CHUNK_SIZE]
            buffer = buffer[CHUNK_SIZE:]

            result = model.transcribe(
                chunk,
                fp16=False,
                language="en",
                temperature=0.0
            )

            print(">>", result["text"].strip())
