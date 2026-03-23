from faster_whisper import WhisperModel
import time
import os

model_size =   'base.en'
UPLOAD_FOLDER = 'static/sounds'

start_load = time.time()
model = WhisperModel(model_size, device='cpu', compute_type='int8', download_root='home/pi/.cache/whisper')

print(f'Model loaded in {time.time() - start_load:.1f} seconds')

audio_file = os.path.join(UPLOAD_FOLDER, 'test.mp3')

segments, info = model.transcribe(
    audio_file,
    beam_size=3,
    language='en',
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=250),
)

print(f'Language: {info.language} (prob {info.language_probability:.2f})')

for segment in segments:
    print(segment.text.strip())