import simpleaudio as sa

def play_audio(filename):
    # This reads the file into a buffer and plays it directly
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    
    # Wait for playback to finish
    play_obj.wait_done()

play_audio("temp_output.wav")