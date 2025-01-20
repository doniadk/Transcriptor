from flask import Flask, request, render_template, jsonify
from moviepy import VideoFileClip
from pydub import AudioSegment
import whisper
import os

app = Flask(__name__) # __name__ :file

model = whisper.load_model("small")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/transcribe', methods=['POST'])
def transcribe():

    if file not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    # Save the uploaded file temporarily
    temp_input_path = "temp_input" + file.filename.split('.')[-1]
    file.save(temp_input_path)

    try:
        # process video file
        if temp_input_path.lower().endswith(("mp4", "wov", "avi", "webm", "wmv", "avchd", "flv")):

            # extract audio from video
            video_clip = VideoFileClip(file).audio

            # write audio in file
            temp_audio_path = "temp_audio.mp3"
            video_clip.write_audiofile(temp_audio_path)
            video_clip.close()

        else:
            temp_audio_path = temp_input_path # assume it's already an audio file
        
        # transcribe using speech-to-text
        # whisper expects 16 kHz mono audio
        audio = AudioSegment.from_file(temp_audio_path)
        if audio.frame_rate != 16000 or audio.channels != 1:
            audio = audio.set_frame_rate(16000).set_channels(1)
        
        # Save processed audio to temporary WAV file
        temp_wav_path = "temp_audio.wav"
        audio.export(temp_wav_path, format="wav")

        result = model.transcribe(temp_wav_path)

        # return the transcript to the frontend
        return jsonify({"transcription": result["text"]})

    finally:
        # Clean up temporary files
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        if os.path.exists(temp_audio_path) and temp_audio_path != temp_input_path:
            os.remove(temp_audio_path)
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)


@app.route('/translate', methods=['POST'])
def translate():
    """
    Accepts the transcript and the target language.
    
    Returns the translated text."""

@app.route('/summarize', methods=['POST'])
def summarize():
    '''
    Accepts the transcript.
    
    Returns a summarized version of the text.'''   

@app.route('/download', methods=['POST'])
def download(transcript, summary=None):
    '''
    Accepts the transcript (and optional summary).
    
    Generates a downloadable file and sends it back to the user.
    '''

if __name__ == "__main__":
    app.run(debug=True)