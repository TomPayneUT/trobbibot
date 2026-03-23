import subprocess
import os

def generate_mp3(text, model_path, output_mp3):
    temp_wav = "static/sounds/temp_output.wav"
    
    # 1. Generate the WAV file using Piper
    # We pipe the text into the piper executable
    command = f'echo "{text}" | piper --model {model_path} --output_file {temp_wav}'
    
    print("Synthesizing speech...")
    subprocess.run(command, shell=True, check=True)
    
    # 2. Convert WAV to MP3 using FFmpeg
    print("Converting to MP3...")
    conversion_command = f'ffmpeg -i {temp_wav} -codec:a libmp3lame -qscale:a 2 {output_mp3} -y'
    subprocess.run(conversion_command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 3. Clean up the temporary WAV file
    #if os.path.exists(temp_wav):
    #    os.remove(temp_wav)
        
    print(f"Done! Created: {output_mp3}")

# Usage
if __name__ == "__main__":
    my_text = "Hello! This is a high-quality voice running locally on my Raspberry Pi 6."
    model = "voices/en_GB-semaine-medium.onnx"
    output_file = "greeting.mp3"
    
    generate_mp3(my_text, model, output_file)