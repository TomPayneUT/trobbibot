import pyaudio
import wave
#import keyboard
#from gtts import gTTS
#from playsound import playsound
from transcriber import transcribe_audio
from tts import generate_wav
from playaudiopygame import play_audio
from llm import ask


while True:
    prompt = input('prompt (type r to record, or q to quit): ')
    if prompt == 'q':
        print('Goodbye')
        break
    elif prompt == 'r':
        # Record parameters
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        #RATE = 16000
        RATE = 48000
        SILENCE_THRESHOLD = 500  # Adjust this value based on your microphone/environment
        
        # Calculate how many silent chunks constitute 750ms
        # Chunks per second = RATE / CHUNK
        # Number of silent chunks = (0.75 seconds) * (RATE / CHUNK)
        SILENCE_LIMIT_CHUNKS = int(1.75 * RATE / CHUNK) 
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        
        print("Recording... Speak now. Recording will stop after 1.75 seconds of silence.")
        frames = []
        silent_chunks_count = 0
        recording_active = True
        
        # Start recording loop
        while recording_active:
            try:
                # Read audio data from the stream
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)

                # Convert the chunk of audio data to an array of 16-bit integers
                # 'h' is for short (16-bit integer)
                import numpy as np
                import struct
                
                # The 'struct' module is used to pack and unpack C data types.
                # Convert binary data to a tuple of short integers
                data_chunk = struct.unpack(str(CHUNK) + 'h', data)
                
                # Calculate the Root Mean Square (RMS) for volume detection
                # RMS = sqrt(sum(x^2) / n)
                rms = np.sqrt(np.mean(np.array(data_chunk, dtype=np.int64)**2))

                # Voice Activity Detection (VAD) Logic
                if rms < SILENCE_THRESHOLD:
                    silent_chunks_count += 1
                    if silent_chunks_count > SILENCE_LIMIT_CHUNKS:
                        print("Silence limit reached. Stopping recording.")
                        recording_active = False
                else:
                    # Reset the counter if sound is detected above the threshold
                    silent_chunks_count = 0
                
                # Optional: Implement a max recording time safeguard (e.g., 60 seconds)
                # if len(frames) > int(RATE / CHUNK * 60): 
                #     print("Maximum recording time reached. Stopping.")
                #     recording_active = False

            except IOError as e:
                # Handle buffer overflow (common with real-time audio)
                #print(f"IOError: {e}")
                continue

        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save to wav
        wf = wave.open("static/sounds/live_recording.wav", 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    # Transcribe with Gemini (rest of your existing code)
    # ...

        # Transcribe with Gemini
        
        #audio = client.files.upload(file="live_recording.wav")
        #response = client.models.generate_content(
        #    model="gemini-2.5-flash", contents=[audio]
        #)

        transcription = transcribe_audio('static/sounds/live_recording.wav')
        response = ask(transcription)
        
        #print(response.text)
        #print(genai.GenerativeModel("gemini-2.0-flash-exp").generate_content([audio, "Transcribe"]).text)
    else:
        #response = client.models.generate_content(
        #    model="gemini-2.5-flash", contents=prompt
        #)
        response = ask(prompt)
    
    print(response)

    #speak the response
    #tts = gTTS(text=response.text, lang='en', slow=False)
    file_name = "static/sounds/temp_output.wav"
    #tts.save(file_name)
    generate_wav(response, "voices/en_GB-semaine-medium.onnx", file_name)

    try:
        #playsound(file_name)
        play_audio(file_name)
    except Exception as e:
        print(f"Could not play audio using playsound: {e}")
        print("You might need to install an audio player or use system commands.")
