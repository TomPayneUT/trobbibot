from flask import Flask, make_response, render_template, jsonify, request, send_file, Response
import subprocess
import os
from transcriber import transcribe_audio
from ttsmp3 import generate_mp3
from llm import ask # make chat local by uncommenting this and commenting out the genai code below
import serial
import time
from picamera2 import Picamera2
import io
import threading
#import google.genai as genai  # make chat online by uncommenting this and commenting out the local llm code above


app = Flask(__name__)

#client = genai.Client(api_key="dont hardcode your api key you dummy")
counter = 0
transcription = ''
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
except:
    print('USB serial cord unplugged, could not connect to Trobbi')
time.sleep(2)

UPLOAD_FOLDER = 'static/sounds'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html', counter=counter)

@app.route('/move')
def move():
    dir = request.args.get('dir')
    print(f'Detected: {dir}')
    if ser and dir:
        ser.write(dir.encode())
    return 'OK'

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio_data' not in request.files:
        return jsonify(success=False, error="No file part"), 400
    
    file = request.files['audio_data']

    raw_path = os.path.join(UPLOAD_FOLDER, 'input.webm')
    mp3_path = os.path.join(UPLOAD_FOLDER, 'test.mp3')

    file.save(raw_path)

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", raw_path,
        "-ac", "1",
        "-ar", "16000",
        "-codec:a", "libmp3lame",
        "-b:a", "128k",
        mp3_path
    ], check=True)

    global transcription
    transcription = transcribe_audio(mp3_path)

    #uncomment the following line to use a local llm instead of genai
    text_answer = ask(transcription)
    #uncomment the following lines to use genai instead of a local llm
    #text_answer = client.models.generate_content(
    #        model="gemini-2.5-flash", contents=transcription
    #    )


    generate_mp3(text_answer, 'voices/en_GB-semaine-medium.onnx', mp3_path)

    return jsonify({'success': True, 'transcription' : transcription, 'text_answer': text_answer})

@app.route('/increment', methods=['POST'])
def increment():
    global counter
    counter += 1

    return {
        'success': True,
        'new_value': counter
    }

@app.route('/get-audio')
def get_audio():
    mp3_path = os.path.join(UPLOAD_FOLDER, 'test.mp3')

    ########
    #cut this out if you want to hear the original recording
    #answer = ask(transcription)
    #generate_mp3(answer, 'voices/en_GB-semaine-medium.onnx', mp3_path)
    #########


    # Create the response object
    response = make_response(send_file(mp3_path, mimetype='audio/mpeg'))
    
    # Set headers to prevent caching
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response
    #return send_file(mp3_path, mimetype='audio/mpeg')


# --- Camera Setup ---
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

class CameraStreamer:
    def __init__(self):
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        # Start a background thread to update the frame
        threading.Thread(target=self._update, daemon=True).start()

    def _update(self):
        while True:
            if self.running:
                stream = io.BytesIO()
                # Capture frame
                picam2.capture_file(stream, format='jpeg')
                
                with self.lock:
                    self.frame = stream.getvalue()
            else:
                time.sleep(0.5)  # Sleep briefly when not running to reduce CPU usage

    def get_frame(self):
        with self.lock:
            return self.frame

# Initialize our single broadcaster
streamer = CameraStreamer()

def generate_frames():
    while True:
        frame_bytes = streamer.get_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        # Tiny sleep to prevent the loop from eating 100% CPU
        import time
        time.sleep(0.03) # Roughly 30 FPS

@app.route('/stream')
def get_stream():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Add a route to toggle the state
@app.route('/toggle_stream/<state>')
def toggle_stream(state):
    streamer.running = (state == 'on')
    return f"Stream is {state}"

#app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
app.run(host='0.0.0.0', port=5000)
#app.run(host='0.0.0.0')

