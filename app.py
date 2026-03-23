from flask import Flask, make_response, render_template, jsonify, request, send_file, Response
import subprocess
import os
from transcriber import transcribe_audio
from ttsmp3 import generate_mp3
from llm import ask
import serial
import time
from picamera2 import Picamera2
import io

app = Flask(__name__)

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

    text_answer = ask(transcription)
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



@app.route('/stream')
def get_stream():
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    def generate_frames():
        while True:
            # Create an in-memory binary stream
            stream = io.BytesIO()
            
            # Capture directly to the stream in JPEG format
            # use_video_port=True is faster for streaming
            picam2.capture_file(stream, format='jpeg')
            
            # Reset stream pointer to the beginning to read it
            stream.seek(0)
            frame_bytes = stream.read()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


#app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
app.run(host='0.0.0.0', port=5000)
#app.run(host='0.0.0.0')

