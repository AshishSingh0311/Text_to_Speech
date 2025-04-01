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
    'ml': 'Malayalam',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'mr': 'Marathi',
    'pa': 'Punjabi',
    'or': 'Oriya',
    'as': 'Assamese',
    'ur': 'Urdu'
}

# Emotion modulation parameters
EMOTION_PARAMETERS = {
    'neutral': {
        'speed': 1.0,
        'pitch': 0,
        'volume': 0,
        'emphasis': 0
    },
    'happy': {
        'speed': 1.1,    # Slightly faster
        'pitch': 2,      # Higher pitch
        'volume': 2,     # Slightly louder
        'emphasis': 1    # More emphasis on key words
    },
    'sad': {
        'speed': 0.85,   # Slower
        'pitch': -2,     # Lower pitch
        'volume': -1,    # Slightly quieter
        'emphasis': -1   # Less emphasis
    },
    'angry': {
        'speed': 1.15,   # Faster
        'pitch': 1,      # Slightly higher pitch
        'volume': 3,     # Louder
        'emphasis': 2    # Strong emphasis
    },
    'excited': {
        'speed': 1.2,    # Fast
        'pitch': 3,      # Very high pitch
        'volume': 2,     # Louder
        'emphasis': 2    # Strong emphasis
    },
    'calm': {
        'speed': 0.9,    # Slightly slow
        'pitch': -1,     # Slightly lower pitch
        'volume': -1,    # Quieter
        'emphasis': -1   # Soft emphasis
    },
    'fearful': {
        'speed': 1.1,    # Slightly faster (nervousness)
        'pitch': 1,      # Slightly higher pitch
        'volume': -1,    # Quieter
        'emphasis': 0    # Normal emphasis but quivering
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
        
        Args:
            text (str): The text to convert to speech (supports up to 400 words)
            language (str): The language code (e.g., 'en', 'hi')
            emotion (str): The emotion name (e.g., 'neutral', 'happy')
            format (str): Output format ('mp3' or 'wav')
            
        Returns:
            dict: Result with success status and file details
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
            logging.debug(f"Generating speech for text: {text[:50]}... in language: {language}")
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
                logging.debug(f"Applying speed modification: {speed}")
                # Speed change is performed by modifying the frame rate
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * speed)
                })
                
            # Apply pitch modification (simplified approach)
            pitch_semitones = EMOTION_PARAMETERS[emotion]['pitch']
            if pitch_semitones != 0:
                logging.debug(f"Applying pitch modification: {pitch_semitones} semitones")
                # For more advanced implementations, consider using librosa or other libraries
                # This is a simplified approach for demonstration
                new_sample_rate = int(audio.frame_rate * (2 ** (pitch_semitones / 12.0)))
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": new_sample_rate
                })
                audio = audio.set_frame_rate(44100)  # Reset to standard frame rate
            
            # Apply volume adjustment
            volume_db = EMOTION_PARAMETERS[emotion]['volume']
            if volume_db != 0:
                logging.debug(f"Applying volume adjustment: {volume_db}dB")
                audio = audio + volume_db
            
            # Apply emphasis effect based on emotion
            emphasis = EMOTION_PARAMETERS[emotion]['emphasis']
            if emphasis != 0:
                logging.debug(f"Applying emphasis effect: {emphasis}")
                # Simplified emphasis effect
                if emphasis > 0:
                    # For positive emphasis, add some compression (reduce dynamic range)
                    # This makes loud parts relatively less loud and quiet parts more prominent
                    audio = audio.compress_dynamic_range(threshold=-20.0, ratio=4.0, attack=5.0, release=50.0)
                else:
                    # For negative emphasis, add slight normalization
                    audio = audio.normalize()
            
            # Generate a unique filename that includes language and emotion
            filename = f"{language}_{emotion}_{uuid.uuid4()}.{format}"
            filepath = os.path.join(self.audio_folder, filename)
            
            # Export the audio in the requested format with appropriate bitrate
            if format.lower() == 'mp3':
                audio.export(filepath, format="mp3", bitrate="192k")
            elif format.lower() == 'wav':
                audio.export(filepath, format="wav")
            else:
                audio.export(filepath, format="mp3", bitrate="192k")  # Default to mp3
                
            # Clean up temporary file
            os.unlink(temp_path)
            
            logging.info(f"Successfully generated speech: {filename}")
            return {
                'success': True,
                'filename': filename,
                'path': f'/static/audio/{filename}',
                'language': language,
                'emotion': emotion,
                'format': format,
                'duration': len(audio) / 1000  # Duration in seconds
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
