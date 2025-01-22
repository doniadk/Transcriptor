from flask import Flask, request, render_template, jsonify
import whisper
import functions as f
from googletrans import Translator
from transformers import pipeline

app = Flask(__name__) # __name__ :file

model = whisper.load_model("small")

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/transcribe', methods=['POST'])
def transcribe():

    file = request.files['file']
    if file not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    audio = f.process_audio(file)
    transcript = f.transcribe(audio, model)
    return jsonify(transcript)


@app.route('/translate', methods=['POST'])
def translate(transcript, lan):

    tl = Translator(service_urls=[
        'translate.google.com',
        'translate.google.co.kr',
    ]) 
    output = tl.translate(transcript, dest=lan)
    
    return jsonify(output)


@app.route('/summarize', methods=['POST'])
def summarize(transcript):

    # transcript must be text ( str )
    summarize = pipeline(task="summarization", model="facebook/bart-large-cnn")
    output = summarize(
    transcript, 
    min_length=50,
    max_length=100 )
    return jsonify(output[0]['summary_text'])


@app.route('/download', methods=['POST'])
def download(transcript, summary=None):
   
    text_formated = "\n".join([segment['text'] for segment in transcript])
    tl = Translator(service_urls=[
        'translate.google.com',
        'translate.google.co.kr',
    ]) 
    ln_text = tl.detect(transcript).lang
    if summary:
        ln_summary = tl.detect(summary).lang
    pdf = f.create_PDF(text_formated, ln_text, ln_summary=None, summary=None)
    return pdf



if __name__ == "__main__":
    app.run(debug=True)