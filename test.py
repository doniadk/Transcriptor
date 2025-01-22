from moviepy import VideoFileClip
from pydub import AudioSegment
import whisper
import os

file = '_clara_vintage__GCYT7BGtpwMkGMwIABbdQxCq8tUXbq_EAAAF.mp4'

model = whisper.load_model("small")


def load_audio(file):
    if file.lower().endswith(("mp3", "aac", "wav")):
        return AudioSegment.from_file(file, format=file.split('.')[-1])
    elif file.lower().endswith(("mp4", "avi", "mov", "webm", "wmv")):
        video_clip = VideoFileClip(file)
        audio_clip = video_clip.audio
        audio_path = "extracted_audio.mp3"
        audio_clip.write_audiofile(audio_path)
        audio_clip.close()
        audio = AudioSegment.from_file(audio_path, format="mp3")
        os.remove(audio_path)
        return audio

# Load and process audio
audio = load_audio(file)

# Whisper expects 16 kHz mono audio
if audio.frame_rate != 16000 or audio.channels != 1:
    audio = audio.set_frame_rate(16000).set_channels(1)

# Save processed audio to temporary WAV file
temp_wav_path = "temp_audio.wav"
audio.export(temp_wav_path, format="wav")

result = model.transcribe(temp_wav_path)

# transcription with timestamps
transcription_with_timestamps = [
    {
        "start": segment['start'],
        "end": segment['end'],
        "text": segment['text']
    }
    for segment in result['segments']
]


"""from googletrans import Translator

def translate_text():
    tl = Translator(service_urls=[
        'translate.google.com',
        'translate.google.co.kr',
    ])
    dest = 'ar'  # Target language
    text = 'good morning'  # Text to translate
    try:
        output = tl.translate(text, dest=dest)
        print(output.text)  # Print the translated text
    except Exception as e:
        print(f"error: {e}")"""

"""from transformers import pipeline

text = (
    "a monarchy is a type of government ruled by a monarch which is often a king or a queen. "
    "the Monarch's role is passed down through the same family from generation to generation often going to the oldest child. "
    "major countries operating under a monarchy include the United Kingdom, Japan, Spain, Sweden, and Saudi Arabia. "
    "there are multiple forms of monarchies - symbolic monarchy where the Monarch has no political or economic power like the United Kingdom, "
    "which is run by a parliamentary government led by a prime minister. On the other hand, an absolute monarchy is where the king or queen "
    "has the power to make all the important decisions in a country. The disadvantage of a monarchy is that it can lead to unsuitable leaders "
    "who came to power because they were The Heirs. This often leads to a lack of democratic governance and the potential for abuse of power."
)

try:
    summarize = pipeline(task="summarization", model="facebook/bart-large-cnn")
    output = summarize(
    text, 
    min_length=50,
    max_length=100 )

    print(output[0]['summary_text'])

except Exception as e:
    print(f"error: {e}")
"""

from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
try:
    # Input text
    text = "\n".join([segment['text'] for segment in transcription_with_timestamps])  # Combine the transcriptions
    

    summary = (
        "This text explains monarchy, its types (symbolic and absolute), and key countries operating under monarchy. "
        "It highlights the disadvantages, such as the risk of unsuitable leadership and lack of democratic governance."
    )

    from googletrans import Translator
    tl = Translator(service_urls=[
        'translate.google.com',
        'translate.google.co.kr',
    ]) 
    ln_text = tl.detect(text).lang
    ln_summary = tl.detect(summary).lang

    # Create a PDF
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.add_font('Amiri', '', 'Amiri-Regular.ttf')
    pdf.add_font('Merriweather', '', 'Merriweather-Regular.ttf')
    pdf.add_font('Merriweather', '', 'Merriweather-Bold.ttf')

    # Optionally add the summary
    if summary:
        pdf.ln(10)  # Add space before the summary
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Summary', align='C')
        pdf.ln(10)

        if ln_summary == 'ar':
            reshaped_summary = arabic_reshaper.reshape(summary)
            display_summary = get_display(reshaped_summary)
            pdf.set_font('Amiri', size=12)
            pdf.multi_cell(0, 10, summary, align='R')
        else:
            pdf.set_font('Arial', size=12)
            pdf.multi_cell(0, 10, summary)
        pdf.ln(10)

    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, 'Transcript', align='C')
    pdf.ln(10)  # Add some space

    # Add the transcript text with timestamps
    for segment in transcription_with_timestamps:
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text']

        if ln_text == 'ar':
            reshaped_text = arabic_reshaper.reshape(text)
            display_text = get_display(reshaped_text)
            timestamp_text = f"{display_text} [{start_time:.2f}s - {end_time:.2f}s]"
        else:
            timestamp_text = f"[{start_time:.2f}s - {end_time:.2f}s] {text}"


        if ln_text == 'ar':
            
            pdf.set_font('Amiri', size=12)
            pdf.multi_cell(0, 10, timestamp_text, align='R')
        else:
            pdf.set_font('Arial', size=12)
            pdf.multi_cell(0, 10, timestamp_text)  # Add each sentence with timestamps
        pdf.ln(2)

    

    # Output the PDF
    pdf.output('tuto1.pdf')
    print("PDF created successfully.")

except Exception as e:
    print(f"error: {e}")