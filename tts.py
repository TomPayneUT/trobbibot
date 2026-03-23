import subprocess
import os

def generate_wav(text, model_path="voices/en_GB-semaine-medium.onnx", output_wav="static/sound/temp_output.wav"):
    temp_wav = "static/sounds/temp_output.wav"
    
    # 1. Generate the WAV file using Piper
    # We pipe the text into the piper executable
    command = f'echo "{text}" | piper --model {model_path} --output_file {temp_wav}'
    
    print("Synthesizing speech...")
    subprocess.run(command, shell=True, check=True)
    
        
    print(f"Done! Created: {temp_wav}")

# Usage
if __name__ == "__main__":
    my_text = "Hello! This is a test of my speech generation capability. I think that I am pretty amazing."
    model = "voices/en_GB-semaine-medium.onnx"
    output_file = "static/sound/temp_output.wav"
    
    #generate_wav(my_text, model, output_file)
    generate_wav("Hi I am Trobbius")
