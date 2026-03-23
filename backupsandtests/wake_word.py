import openwakeword
from openwakeword.model import Model
import pyaudio
import numpy as np

class WakeWordDetector:
    def __init__(self, callback, model_path=None):
        self.callback = callback
        # Use built-in "hey_jarvis" or path to custom .tflite
        print('starting')
        self.model = Model(
            wakeword_model_paths=[model_path or "hey_jarvis"]
            #inference_framework="tflite"
        )
        print('model loaded')
        self.pa = pyaudio.PyAudio()

    def listen(self):
        stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1280,
            input_device_index=0
        )
        print("[Wake Word] Listening...")
        while True:
            audio = np.frombuffer(stream.read(1280), dtype=np.int16)
            predictions = self.model.predict(audio)
            for key, score in predictions.items():
                if score > 0.5:  # confidence threshold
                    print(f"[Wake Word] Detected: {key} ({score:.2f})")
                    self.callback()
                    break