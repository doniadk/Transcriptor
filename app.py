from flask import Flask, request, render_template, jsonify
import whisper
import functions as f
from googletrans import Translator
from transformers import pipeline

app = Flask(__name__) # __name__ :file

model = whisper.load_model("small")
summarize_model = pipeline(task="summarization", model="google/mt5-small")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    # Ensure the file is not empty
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Process the uploaded file
    print("processing audio file...")
    audio = f.process_audio(file)
    print("transcribing in process...")
    transcript = f.transcribe(audio, model)
    return jsonify({"transcription": transcript})



@app.route('/translate', methods=['POST'])
def translate():

    data = request.json     # retrieve JSON data
    transcript = data.get('transcript')
    lan = data.get('language')

    tl = Translator(service_urls=[
        'translate.google.com',
        'translate.google.co.kr',
    ]) 
    output = tl.translate(transcript, dest=lan)
    translation = output.text
    return jsonify({"translation": translation})


@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    transcript = data.get('transcript')
    # transcript must be text ( str )
    print("in process...")
    output = summarize_model(
    transcript, 
    min_length=50,
    max_length=100 )
    return jsonify(output[0]['summary_text'])


@app.route('/download', methods=['POST'])
def download():
    data = request.json
    transcript = data.get('transcript')
    summary = data.get('summary')
    text_formated = "\n".join([segment['text'] for segment in transcript])
    tl = Translator(service_urls=[
        'translate.google.com',
        'translate.google.co.kr',
    ]) 
    ln_text = tl.detect(transcript).lang
    if summary:
        ln_summary = tl.detect(summary).lang
    pdf = f.create_PDF(text_formated, ln_text, ln_summary, summary)
    return pdf



if __name__ == "__main__":
    app.run(debug=True)