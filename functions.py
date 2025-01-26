from bidi.algorithm import get_display
from moviepy import VideoFileClip
from pydub import AudioSegment
import arabic_reshaper
from fpdf import FPDF
import os

def process_audio(file):    # file object is FileStorage object not str
    filename = file.filename
    if filename.lower().endswith(("mp3", "aac", "wav")):
        return AudioSegment.from_file(file, format=file.split('.')[-1])
    elif filename.lower().endswith(("mp4", "avi", "mov", "webm", "wmv")):
        temp_video_path = "temp_video." + filename.split('.')[-1]
        file.save(temp_video_path)  # Save the file locally
        with VideoFileClip(temp_video_path) as video_clip:
            audio_clip = video_clip.audio
            audio_path = "extracted_audio.mp3"

            # Export audio and close the video clip
            audio_clip.write_audiofile(audio_path)
            audio_clip.close()
        # Remove the temporary video file
        os.remove(temp_video_path)
        audio = AudioSegment.from_file(audio_path, format="mp3")
        os.remove(audio_path)
        return audio
    


def transcribe(audio, model):

    # Whisper expects 16 kHz mono audio
    if audio.frame_rate != 16000 or audio.channels != 1:
        audio = audio.set_frame_rate(16000).set_channels(1)

    temp_wav_path = "temp_audio.wav"
    audio.export(temp_wav_path, format="wav")
    result = model.transcribe(temp_wav_path)
    transcription_with_timestamps = [
        {
            "start": segment['start'],
            "end": segment['end'],
            "text": segment['text']
        }
        for segment in result['segments']
    ]
    os.remove("temp_audio.wav")
    return transcription_with_timestamps



def create_PDF(t, ln_text, ln_summary=None, summary=None):
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
    for segment in t:
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
    return pdf.output('transcript.pdf')