import subprocess

def play_audio(filename):
    # -D specifies the device. 'plughw:2,0' targets Card 2 (your USB).
    # 'plug' handles sample rate conversions automatically so it doesn't crash.
    try:
        #subprocess.run(['aplay', '-D', 'plughw:2,0', filename], check=True)
        #subprocess.run(['aplay', filename], check=True)
        subprocess.run(['aplay', '-D', 'plughw:CARD=USB,DEV=0', filename], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Playback failed: {e}")

if __name__ == "__main__":
    #play_audio("temp_output.wav")
    play_audio("static/sounds/temp_output.wav")