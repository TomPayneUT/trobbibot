from flask import Flask, make_response, render_template, jsonify, request, send_file
import subprocess
import os
from transcriber import transcribe_audio

app = Flask(__name__)

counter = 0

UPLOAD_FOLDER = 'static/sounds'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html', counter=counter)

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

    transcription = transcribe_audio(mp3_path)

    return jsonify({'success': True, 'transcription' : transcription})

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
    
    # Create the response object
    response = make_response(send_file(mp3_path, mimetype='audio/mpeg'))
    
    # Set headers to prevent caching
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response
    #return send_file(mp3_path, mimetype='audio/mpeg')

app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
#app.run(host='0.0.0.0')

