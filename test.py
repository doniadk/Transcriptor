from moviepy import VideoFileClip
from pydub import AudioSegment
import whisper
import os

file = 'AQMNKzZbThxhHXye_AewI6arBCy2OnfoN9AaQlRQ750BpVzGe5CxoDrUSr2x0yl4Z017olpyLKbUBFhJyVcDnSXg.mp4'

try:
    if file.lower().endswith(("mp3", "aac", "wav")):
        # Load audio file directly
        audio = AudioSegment.from_file(file, format=file.split('.')[-1])
        print("Audio file loaded successfully.")
        
    elif file.lower().endswith(("mp4", "avi", "mov", "webm", "wmv")):
        # Extract audio from video
        video_clip = VideoFileClip(file)
        if video_clip.audio is None:
            raise ValueError("No audio stream found in video file.")
        audio_clip = video_clip.audio
        
        # Save audio as mp3 file
        temp_audio_path = "extracted_audio.mp3"
        audio_clip.write_audiofile(temp_audio_path)
        audio_clip.close()
        
        # Load the extracted audio into pydub for further processing
        audio = AudioSegment.from_file(temp_audio_path, format="mp3")
        print("Audio extracted and loaded into pydub.")
        
        # Delete the temporary mp3 file
        os.remove(temp_audio_path)
    
    else:
        print("Unsupported file format.")
        exit()
    
    # Whisper expects 16 kHz mono audio
    if audio.frame_rate != 16000 or audio.channels != 1:
        print("Converting audio to 16 kHz mono...")
        audio = audio.set_frame_rate(16000).set_channels(1)
    
    # Save processed audio to temporary WAV file
    temp_wav_path = "temp_audio.wav"
    audio.export(temp_wav_path, format="wav")
    
    # Load the Whisper model and transcribe
    model = whisper.load_model("small")
    result = model.transcribe(temp_wav_path)
    print(result["text"])
    
    # Clean up the temporary file
    os.remove(temp_wav_path)

except Exception as e:
    print(f"Error: {e}")
    exit()
