from faster_whisper import WhisperModel
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile, os

model = WhisperModel("tiny.en", device="cpu", compute_type="int8")

def record_until_silence(max_seconds=8, silence_threshold=0.01, silence_duration=1.0):
    """Record audio, stop when silent for 1s or max_seconds reached."""
    sample_rate = 16000
    chunks = []
    silent_chunks = 0
    silence_frames = int(silence_duration * sample_rate / 512)

    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32',
                        blocksize=512) as stream:
        total_frames = int(max_seconds * sample_rate / 512)
        for _ in range(total_frames):
            chunk, _ = stream.read(512)
            chunks.append(chunk.copy())
            rms = np.sqrt(np.mean(chunk**2))
            if rms < silence_threshold:
                silent_chunks += 1
            else:
                silent_chunks = 0
            if silent_chunks > silence_frames and len(chunks) > 16:
                break

    audio = np.concatenate(chunks).flatten()
    return audio, sample_rate

def transcribe():
    """Record speech and return transcribed text."""
    audio, sr = record_until_silence()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, sr)
        segments, _ = model.transcribe(f.name, language="en", vad_filter=True)
        text = " ".join(s.text.strip() for s in segments)
    os.unlink(f.name)
    return text.strip()