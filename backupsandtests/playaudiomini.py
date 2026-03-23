import miniaudio

def play_audio(filename):
    # Decode the wav file (very low memory footprint)
    stream = miniaudio.stream_file(filename)
    
    # Create the output device
    # On Pi 5, this hooks into PipeWire automatically
    with miniaudio.PlaybackDevice() as device:
        device.start(stream)
        
        # Keep the script alive until the sound finishes
        import time
        while stream.num_frames_played < stream.nframes:
            time.sleep(0.1)

if __name__ == "__main__":
    play_audio("temp_output.wav")