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

# Voice type parameters
VOICE_TYPES = {
    'default': {
        'base_pitch': 0,
        'timbre': 0,
        'clarity': 0,
        'name': 'Default'
    },
    'male': {
        'base_pitch': -2,
        'timbre': -1,
        'clarity': 1,
        'name': 'Male'
    },
    'female': {
        'base_pitch': 2,
        'timbre': 1,
        'clarity': 2,
        'name': 'Female'
    },
    'child': {
        'base_pitch': 4,
        'timbre': 2,
        'clarity': 3,
        'name': 'Child'
    },
    'elderly': {
        'base_pitch': -1,
        'timbre': -2,
        'clarity': -1,
        'name': 'Elderly'
    },
    'robot': {
        'base_pitch': 0,
        'timbre': -3,
        'clarity': 5,
        'name': 'Robot'
    }
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
    },
    'whisper': {
        'speed': 0.9,    # Slightly slow
        'pitch': -1,     # Lower pitch
        'volume': -3,    # Very quiet
        'emphasis': -2   # Very soft emphasis
    },
    'shouting': {
        'speed': 1.2,    # Fast
        'pitch': 2,      # Higher pitch
        'volume': 5,     # Very loud
        'emphasis': 4    # Very strong emphasis
    }
}

# Audio effects
AUDIO_EFFECTS = {
    'none': {
        'description': 'No effects',
        'enabled': False
    },
    'echo': {
        'description': 'Echo effect with slight delay',
        'enabled': True
    },
    'reverb': {
        'description': 'Reverb effect for spacious sound',
        'enabled': True
    },
    'chorus': {
        'description': 'Chorus effect for richer sound',
        'enabled': True
    },
    'distortion': {
        'description': 'Distortion effect for robotic sound',
        'enabled': True
    }
}

class TextToSpeechService:
    def __init__(self, static_folder):
        self.static_folder = static_folder
        self.audio_folder = os.path.join(static_folder, 'audio')
        
        # Create audio directory if it doesn't exist
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)
            
    def generate_speech(self, text, language='en', emotion='neutral', voice_type='default', 
                      custom_speed=None, custom_pitch=None, custom_volume=None, audio_effect='none', format='mp3'):
        """
        Generate speech from text with customized parameters
        
        Args:
            text (str): The text to convert to speech (supports up to 400 words)
            language (str): The language code (e.g., 'en', 'hi')
            emotion (str): The emotion name (e.g., 'neutral', 'happy')
            voice_type (str): The voice type (e.g., 'default', 'male', 'female')
            custom_speed (float): Optional custom speed override (0.5-2.0)
            custom_pitch (int): Optional custom pitch override (-10 to 10 semitones)
            custom_volume (int): Optional custom volume override (-10 to 10 dB)
            audio_effect (str): Audio effect to apply (e.g., 'none', 'echo')
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
            
        if voice_type not in VOICE_TYPES:
            logging.warning(f"Unsupported voice type: {voice_type}. Falling back to default.")
            voice_type = 'default'
            
        if audio_effect not in AUDIO_EFFECTS:
            logging.warning(f"Unsupported audio effect: {audio_effect}. Falling back to none.")
            audio_effect = 'none'
            
        try:
            # Generate basic speech with gTTS
            logging.debug(f"Generating speech for text: {text[:50]}... in language: {language}")
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                tts.save(temp_file.name)
                temp_path = temp_file.name
            
            # Apply advanced audio processing with pydub
            audio = AudioSegment.from_mp3(temp_path)
            
            # Calculate final parameters by combining emotion, voice type, and custom values
            # Speed modification (use custom value if provided)
            speed = custom_speed if custom_speed is not None else EMOTION_PARAMETERS[emotion]['speed']
            speed = max(0.5, min(2.0, speed))  # Clamp between 0.5 and 2.0
            
            # Apply speed modification
            if speed != 1.0:
                logging.debug(f"Applying speed modification: {speed}")
                # Speed change is performed by modifying the frame rate
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * speed)
                })
            
            # Calculate final pitch by combining emotion and voice type parameters
            base_pitch = VOICE_TYPES[voice_type]['base_pitch']
            emotion_pitch = EMOTION_PARAMETERS[emotion]['pitch']
            final_pitch = custom_pitch if custom_pitch is not None else (base_pitch + emotion_pitch)
            final_pitch = max(-10, min(10, final_pitch))  # Clamp between -10 and 10
            
            # Apply pitch modification
            if final_pitch != 0:
                logging.debug(f"Applying pitch modification: {final_pitch} semitones")
                new_sample_rate = int(audio.frame_rate * (2 ** (final_pitch / 12.0)))
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": new_sample_rate
                })
                audio = audio.set_frame_rate(44100)  # Reset to standard frame rate
            
            # Calculate final volume
            volume_db = custom_volume if custom_volume is not None else EMOTION_PARAMETERS[emotion]['volume']
            volume_db = max(-10, min(10, volume_db))  # Clamp between -10 and 10
            
            # Apply volume adjustment
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
                    ratio = min(8.0, 2.0 + emphasis)
                    threshold = -20.0 - (emphasis * 2)
                    audio = audio.compress_dynamic_range(
                        threshold=threshold, 
                        ratio=ratio,
                        attack=5.0, 
                        release=50.0 + (emphasis * 10)
                    )
                else:
                    # For negative emphasis, add subtle normalization
                    audio = audio.normalize(headroom=abs(emphasis))
            
            # Apply voice timbre modifications
            timbre = VOICE_TYPES[voice_type]['timbre']
            if timbre != 0:
                logging.debug(f"Applying timbre modification: {timbre}")
                # Simplified timbre adjustment
                if timbre > 0:
                    # Increase high frequencies for clearer voice
                    audio = audio.high_pass_filter(800)
                else:
                    # Increase low frequencies for deeper voice
                    audio = audio.low_pass_filter(3000)
            
            # Apply audio effects if enabled
            if audio_effect != 'none' and AUDIO_EFFECTS[audio_effect]['enabled']:
                logging.debug(f"Applying audio effect: {audio_effect}")
                
                if audio_effect == 'echo':
                    # Create echo effect by adding delayed version of the audio
                    echo_sound = audio - 6  # Lower volume for echo
                    delay_ms = 300  # 300ms delay
                    silence = AudioSegment.silent(duration=delay_ms)
                    audio = audio.overlay(echo_sound, position=delay_ms)
                
                elif audio_effect == 'reverb':
                    # Simple reverb simulation with multiple echos
                    reverb_sound = audio - 10
                    for delay in [50, 100, 150, 200, 250]:
                        echo = reverb_sound - (delay // 20)
                        audio = audio.overlay(echo, position=delay)
                
                elif audio_effect == 'chorus':
                    # Chorus effect - overlay slightly modified versions
                    chorus1 = audio._spawn(audio.raw_data, overrides={
                        "frame_rate": int(audio.frame_rate * 1.007)  # +7 cents
                    }).set_frame_rate(audio.frame_rate) - 6
                    
                    chorus2 = audio._spawn(audio.raw_data, overrides={
                        "frame_rate": int(audio.frame_rate * 0.993)  # -7 cents
                    }).set_frame_rate(audio.frame_rate) - 6
                    
                    audio = audio.overlay(chorus1, position=15)
                    audio = audio.overlay(chorus2, position=30)
                
                elif audio_effect == 'distortion':
                    # Basic distortion effect
                    audio = audio.compress_dynamic_range(threshold=-20.0, ratio=10.0, attack=0.0, release=10.0)
                    audio = audio + 3  # Increase volume to compensate for distortion
            
            # Generate a unique filename
            filename = f"{language}_{voice_type}_{emotion}_{uuid.uuid4()}.{format}"
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
                'voice_type': voice_type,
                'emotion': emotion,
                'speed': speed,
                'pitch': final_pitch,
                'volume': volume_db,
                'audio_effect': audio_effect,
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
        
    def get_voice_types(self):
        """Return the dictionary of supported voice types"""
        return VOICE_TYPES
        
    def get_audio_effects(self):
        """Return the dictionary of supported audio effects"""
        return {k: v for k, v in AUDIO_EFFECTS.items() if k == 'none' or v['enabled']}
