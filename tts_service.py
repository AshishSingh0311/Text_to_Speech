import os
import uuid
import logging
from gtts import gTTS
from io import BytesIO
import tempfile
from pydub import AudioSegment

# Supported languages with their codes and display names
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ta': 'Tamil',
    'te': 'Telugu',
    'ml': 'Malayalam'
}

# Emotion modulation parameters
EMOTION_PARAMETERS = {
    'neutral': {
        'speed': 1.0,
        'pitch': 0,
    },
    'happy': {
        'speed': 1.1,  # Slightly faster
        'pitch': 2,    # Higher pitch
    },
    'sad': {
        'speed': 0.85,  # Slower
        'pitch': -2,    # Lower pitch
    },
    'angry': {
        'speed': 1.15,  # Faster
        'pitch': 1,     # Slightly higher pitch with emphasis
    }
}

class TextToSpeechService:
    def __init__(self, static_folder):
        self.static_folder = static_folder
        self.audio_folder = os.path.join(static_folder, 'audio')
        
        # Create audio directory if it doesn't exist
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)
            
    def generate_speech(self, text, language='en', emotion='neutral', format='mp3'):
        """
        Generate speech from text with the specified language and emotion
        """
        if not text:
            raise ValueError("Text cannot be empty")
            
        if language not in SUPPORTED_LANGUAGES:
            logging.warning(f"Unsupported language: {language}. Falling back to English.")
            language = 'en'
            
        if emotion not in EMOTION_PARAMETERS:
            logging.warning(f"Unsupported emotion: {emotion}. Falling back to neutral.")
            emotion = 'neutral'
            
        try:
            # Generate basic speech with gTTS
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                tts.save(temp_file.name)
                temp_path = temp_file.name
            
            # Apply emotion modulation with pydub
            audio = AudioSegment.from_mp3(temp_path)
            
            # Apply speed modification
            speed = EMOTION_PARAMETERS[emotion]['speed']
            if speed != 1.0:
                # Speed change is performed by modifying the frame rate
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * speed)
                })
                
            # Apply pitch modification (simplified approach)
            pitch_semitones = EMOTION_PARAMETERS[emotion]['pitch']
            if pitch_semitones != 0:
                # For more advanced implementations, consider using librosa or other libraries
                # This is a simplified approach for demonstration
                new_sample_rate = int(audio.frame_rate * (2 ** (pitch_semitones / 12.0)))
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": new_sample_rate
                })
                audio = audio.set_frame_rate(44100)  # Reset to standard frame rate
            
            # Generate a unique filename
            filename = f"{uuid.uuid4()}.{format}"
            filepath = os.path.join(self.audio_folder, filename)
            
            # Export the audio in the requested format
            if format.lower() == 'mp3':
                audio.export(filepath, format="mp3")
            elif format.lower() == 'wav':
                audio.export(filepath, format="wav")
            else:
                audio.export(filepath, format="mp3")  # Default to mp3
                
            # Clean up temporary file
            os.unlink(temp_path)
            
            return {
                'success': True,
                'filename': filename,
                'path': f'/static/audio/{filename}'
            }
            
        except Exception as e:
            logging.error(f"Error generating speech: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def get_supported_languages(self):
        """Return the dictionary of supported languages"""
        return SUPPORTED_LANGUAGES
        
    def get_supported_emotions(self):
        """Return the list of supported emotions"""
        return list(EMOTION_PARAMETERS.keys())
