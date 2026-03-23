from faster_whisper import WhisperModel
import os

# Initialize the model once at the module level
# This ensures it's ready to go as soon as the file is imported
MODEL_SIZE = 'base.en'
MODEL_PATH = 'home/pi/.cache/whisper'

print("Loading Whisper model...")
model = WhisperModel(MODEL_SIZE, device='cpu', compute_type='int8', download_root=MODEL_PATH)

def transcribe_audio(file_path):
    """
    Transcribes an audio file and returns the full text.
    """
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."

    segments, info = model.transcribe(
        file_path,
        beam_size=3,
        language='en',
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=250),
    )

    # Collect all segments into a single string
    full_text = " ".join([segment.text.strip() for segment in segments])
    
    return full_text