import openwakeword
from openwakeword.model import Model
import pyaudio
import numpy as np
import ctypes

# Suppress ALSA errors (Optional, for a cleaner terminal)
ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
def py_error_handler(filename, line, function, err, fmt): pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
try:
    asound = ctypes.cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except: pass

class WakeWordDetector:
    def __init__(self, callback, model_path=None):
        self.callback = callback
        print('Starting openWakeWord...')
        # openWakeWord models strictly expect 16000Hz audio
        self.model = Model(wakeword_model_paths=[model_path or "hey_jarvis"])
        print('Model loaded.')
        self.pa = pyaudio.PyAudio()

    def listen(self):
        MIC_RATE = 48000   # Your CMTECK hardware rate
        MODEL_RATE = 16000 # What the model needs
        RESAMPLE_RATIO = MIC_RATE // MODEL_RATE # Factor of 3
        CHUNK_SIZE = 1280 * RESAMPLE_RATIO      # Grab enough to downsample

        stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=MIC_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
            input_device_index=0
        )

        print("[Wake Word] Listening for 'Hey Jarvis' (or your custom model)...")
        
        try:
            while True:
                # Read raw data from mic
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                # Convert to numpy array
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Downsample: Take every 3rd sample to turn 48k into 16k
                audio_16k = audio_data[::RESAMPLE_RATIO]
                
                # Feed the 16k audio to the model
                prediction = self.model.predict(audio_16k)
                
                for mdl, score in prediction.items():
                    if score > 0.5:
                        print(f"\n[Wake Word] Detected! Confidence: {score:.2f}")
                        self.callback()
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            stream.stop_stream()
            stream.close()
            self.pa.terminate()

# --- Execution ---
def my_callback():
    print(">>> Callback Triggered: You said the wake word!")

if __name__ == "__main__":
    detector = WakeWordDetector(callback=my_callback, model_path='static/models/trahbbi.onnx')
    detector.listen() # This line ensures the loop actually starts!