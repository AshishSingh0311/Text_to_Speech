import os
import uuid
import logging
import random
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

# Enhanced emotion modulation parameters
EMOTION_PARAMETERS = {
    'neutral': {
        'speed': 1.0,
        'pitch': 0,
        'volume': 0,
        'emphasis': 0,
        'eq_profile': 'flat',
        'variability': 0,
        'color': '#6c757d',
        'animation': ''
    },
    'happy': {
        'speed': 1.15,        # Faster
        'pitch': 2.5,         # Higher pitch
        'volume': 2,          # Slightly louder
        'emphasis': 2,        # More emphasis on key words
        'eq_profile': 'bright', # Brighter tone
        'variability': 1.5,   # More dynamic intonation
        'color': '#ffc107',   # Yellow
        'animation': 'pulse'
    },
    'sad': {
        'speed': 0.8,         # Slower
        'pitch': -3,          # Lower pitch
        'volume': -1.5,       # Slightly quieter
        'emphasis': -1.5,     # Less emphasis
        'eq_profile': 'muffled', # Softer tone
        'variability': -0.5,  # Less dynamic
        'color': '#0d6efd',   # Blue
        'animation': 'fade'
    },
    'angry': {
        'speed': 1.2,         # Faster
        'pitch': 1.5,         # Slightly higher pitch
        'volume': 4,          # Much louder
        'emphasis': 3,        # Strong emphasis
        'eq_profile': 'sharp', # Harsh tone
        'variability': 2,     # Very dynamic intonation
        'color': '#dc3545',   # Red
        'animation': 'shake'
    },
    'excited': {
        'speed': 1.25,        # Very fast
        'pitch': 3.5,         # Very high pitch
        'volume': 3,          # Louder
        'emphasis': 2.5,      # Strong emphasis
        'eq_profile': 'bright', # Brighter tone
        'variability': 2.5,   # Very dynamic intonation
        'color': '#fd7e14',   # Orange
        'animation': 'bounce'
    },
    'calm': {
        'speed': 0.9,         # Slightly slow
        'pitch': -1.5,        # Slightly lower pitch
        'volume': -1,         # Quieter
        'emphasis': -1.5,     # Soft emphasis
        'eq_profile': 'warm', # Warm tone
        'variability': -1,    # Less dynamic
        'color': '#20c997',   # Teal
        'animation': ''
    },
    'fearful': {
        'speed': 1.1,         # Slightly faster (nervousness)
        'pitch': 1.8,         # Higher trembling pitch
        'volume': -1.5,       # Quieter
        'emphasis': 0.5,      # Slightly more emphasis
        'eq_profile': 'tinny', # Thin tone
        'variability': 2,     # Trembling voice effect
        'color': '#6f42c1',   # Purple
        'animation': 'wobble'
    },
    'whisper': {
        'speed': 0.85,        # Slow
        'pitch': -1.5,        # Lower pitch
        'volume': -4,         # Very quiet
        'emphasis': -2.5,     # Very soft emphasis
        'eq_profile': 'airy', # Airy tone
        'variability': -1,    # Less dynamic
        'color': '#6c757d',   # Gray
        'animation': 'fade'
    },
    'shouting': {
        'speed': 1.25,        # Fast
        'pitch': 2.5,         # Higher pitch
        'volume': 6,          # Extremely loud
        'emphasis': 5,        # Maximum emphasis
        'eq_profile': 'harsh', # Harsh tone
        'variability': 3,     # Extremely dynamic
        'color': '#d63384',   # Pink
        'animation': 'shake'
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
    },
    'telephone': {
        'description': 'Classic telephone/radio sound effect',
        'enabled': True
    },
    'megaphone': {
        'description': 'Loud megaphone/announcement effect',
        'enabled': True
    },
    'whisper_effect': {
        'description': 'Enhanced whisper with breathy quality',
        'enabled': True
    },
    'ethereal': {
        'description': 'Ethereal, otherworldly voice effect',
        'enabled': True
    },
    'duet': {
        'description': 'Layered voice duet effect',
        'enabled': True
    }
}

# Advanced prosody settings
PROSODY_SETTINGS = {
    'default': {
        'word_gap_variation': 0.0,    # Random variation in word gaps (0.0-1.0)
        'sentence_pause': 0.0,        # Extra pause at end of sentences (in ms)
        'punctuation_pause': 0.0,     # Pause for commas and other punctuation (in ms)
        'emphasis_words': False,      # Whether to emphasize important words
        'micro_pauses': False,        # Add micro-pauses between phrases
        'intonation_strength': 0.0,   # Strength of sentence intonation patterns (0.0-1.0)
        'breathiness': 0.0,           # Amount of breath sound to add (0.0-1.0)
    },
    'natural': {
        'word_gap_variation': 0.15,
        'sentence_pause': 350,
        'punctuation_pause': 150,
        'emphasis_words': True,
        'micro_pauses': True,
        'intonation_strength': 0.3,
        'breathiness': 0.1,
    },
    'expressive': {
        'word_gap_variation': 0.3,
        'sentence_pause': 500,
        'punctuation_pause': 250,
        'emphasis_words': True,
        'micro_pauses': True,
        'intonation_strength': 0.7,
        'breathiness': 0.2,
    },
    'dramatic': {
        'word_gap_variation': 0.5,
        'sentence_pause': 700,
        'punctuation_pause': 350,
        'emphasis_words': True,
        'micro_pauses': True,
        'intonation_strength': 1.0,
        'breathiness': 0.3,
    }
}

# Important words that often receive emphasis in natural speech
EMPHASIS_WORDS = [
    'very', 'extremely', 'absolutely', 'definitely', 'certainly',
    'important', 'critical', 'crucial', 'essential', 'vital',
    'never', 'always', 'must', 'should', 'cannot', 'needed',
    'urgent', 'immediate', 'emergency', 'danger', 'warning',
    'best', 'worst', 'greatest', 'highest', 'lowest', 'amazing'
]

class TextToSpeechService:
    def __init__(self, static_folder):
        self.static_folder = static_folder
        self.audio_folder = os.path.join(static_folder, 'audio')
        
        # Create audio directory if it doesn't exist
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)
            
    def generate_speech(self, text, language='en', emotion='neutral', voice_type='default', 
                      custom_speed=None, custom_pitch=None, custom_volume=None, audio_effect='none', 
                      prosody_level='default', enable_emphasis=True, micro_pauses=False, 
                      sentence_analysis=False, voice_layering=False, spectral_enhancement=False, format='mp3'):
        """
        Generate speech from text with customized parameters and advanced speech enhancements
        
        Args:
            text (str): The text to convert to speech (supports up to 400 words)
            language (str): The language code (e.g., 'en', 'hi')
            emotion (str): The emotion name (e.g., 'neutral', 'happy')
            voice_type (str): The voice type (e.g., 'default', 'male', 'female')
            custom_speed (float): Optional custom speed override (0.5-2.0)
            custom_pitch (int): Optional custom pitch override (-10 to 10 semitones)
            custom_volume (int): Optional custom volume override (-10 to 10 dB)
            audio_effect (str): Audio effect to apply (e.g., 'none', 'echo')
            prosody_level (str): Prosody enhancement level ('default', 'natural', 'expressive', 'dramatic')
            enable_emphasis (bool): Whether to emphasize important words and phrases
            micro_pauses (bool): Whether to add natural micro-pauses between phrases
            sentence_analysis (bool): Whether to analyze sentences for dynamic emphasis
            voice_layering (bool): Whether to apply voice layering effects
            spectral_enhancement (bool): Whether to apply spectral enhancements for clarity
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
            
            # Apply EQ profile based on emotion
            eq_profile = EMOTION_PARAMETERS[emotion]['eq_profile']
            logging.debug(f"Applying EQ profile: {eq_profile}")
            
            try:
                # Apply different EQ profiles for each emotion type
                if eq_profile == 'flat':
                    # Neutral profile - no adjustments
                    pass
                
                elif eq_profile == 'bright':
                    # Bright profile for happy/excited emotions - boost highs, cut lows
                    audio = audio.high_pass_filter(180)  # Cut very low frequencies
                    audio = audio.high_shelf_filter(4000, 3)  # Boost highs
                
                elif eq_profile == 'muffled':
                    # Muffled profile for sad emotions - boost lows, cut highs
                    audio = audio.low_shelf_filter(200, 2)   # Boost lows
                    audio = audio.high_shelf_filter(3000, -2)  # Cut highs
                
                elif eq_profile == 'sharp':
                    # Sharp profile for angry emotions - boost mids
                    audio = audio.high_pass_filter(150)  # Cut very low frequencies
                    audio = audio.low_shelf_filter(400, -1)  # Cut some lows
                    audio = audio.high_shelf_filter(3000, 4)  # Boost highs significantly
                
                elif eq_profile == 'warm':
                    # Warm profile for calm emotions - subtle boost to lows and low-mids
                    audio = audio.low_shelf_filter(250, 2)  # Boost lows
                    audio = audio.high_shelf_filter(8000, -1)  # Slightly cut highs
                
                elif eq_profile == 'tinny':
                    # Tinny profile for fearful emotions - cut lows, boost high-mids
                    audio = audio.high_pass_filter(300)  # Cut more lows
                    audio = audio.high_shelf_filter(4000, 3)  # Boost highs
                
                elif eq_profile == 'airy':
                    # Airy profile for whisper - cut lows, boost very high frequencies
                    audio = audio.high_pass_filter(500)  # Cut lows significantly
                    audio = audio.high_shelf_filter(6000, 4)  # Boost very high frequencies
                
                elif eq_profile == 'harsh':
                    # Harsh profile for shouting - boost everything for intensity
                    audio = audio.high_pass_filter(200)  # Cut very low rumble
                    audio = audio.low_shelf_filter(300, 2)  # Boost low-mids
                    audio = audio.high_shelf_filter(2000, 3)  # Boost highs
            except Exception as e:
                logging.warning(f"Error applying EQ profile: {str(e)}")
            
            # Apply variability/jitter based on emotion intensity
            variability = EMOTION_PARAMETERS[emotion]['variability']
            if variability != 0:
                logging.debug(f"Applying pitch variability: {variability}")
                try:
                    if variability > 0:
                        # Apply pitch variations for more expressive emotions (happy, excited, angry)
                        # This creates a more dynamic, animated speech pattern
                        segment_length = min(400, int(len(audio) / 10))  # Reasonable segment size
                        
                        # Split audio into segments to apply varied processing
                        segments = []
                        for i in range(0, len(audio), segment_length):
                            segment = audio[i:i+segment_length]
                            
                            # Random pitch variation based on variability
                            if random.random() > 0.5:  # 50% chance of pitch change
                                pitch_var = (random.random() * 2 - 1) * variability * 0.5  # -var/2 to +var/2
                                if abs(pitch_var) > 0.1:  # Only apply if significant
                                    try:
                                        var_rate = segment.frame_rate * (2 ** (pitch_var / 12.0))
                                        segment = segment._spawn(segment.raw_data, overrides={
                                            "frame_rate": int(var_rate)
                                        }).set_frame_rate(audio.frame_rate)
                                    except Exception:
                                        pass  # Skip if issue with this segment
                            
                            segments.append(segment)
                        
                        # Combine segments
                        if segments:
                            audio = segments[0]
                            for segment in segments[1:]:
                                audio += segment
                except Exception as e:
                    logging.warning(f"Error applying variability: {str(e)}")
            
            # Apply audio effects if enabled
            if audio_effect != 'none' and AUDIO_EFFECTS[audio_effect]['enabled']:
                logging.debug(f"Applying audio effect: {audio_effect}")
                
                if audio_effect == 'echo':
                    # Enhanced echo effect with multiple delays
                    try:
                        echo_sound = audio - 6  # Lower volume for echo
                        delay_ms = 300  # 300ms delay
                        audio = audio.overlay(echo_sound, position=delay_ms)
                        
                        # Add a secondary, quieter echo for richer effect
                        echo2 = audio - 12
                        audio = audio.overlay(echo2, position=delay_ms * 2)
                    except Exception as e:
                        logging.warning(f"Error in echo effect: {str(e)}")
                
                elif audio_effect == 'reverb':
                    # Enhanced reverb simulation with multiple echos
                    try:
                        reverb_sound = audio - 10
                        delays = [50, 100, 150, 200, 250, 300, 350]
                        for delay in delays:
                            echo = reverb_sound - (delay // 20)
                            audio = audio.overlay(echo, position=delay)
                    except Exception as e:
                        logging.warning(f"Error in reverb effect: {str(e)}")
                
                elif audio_effect == 'chorus':
                    # Enhanced chorus effect with multiple layers
                    try:
                        chorus1 = audio._spawn(audio.raw_data, overrides={
                            "frame_rate": int(audio.frame_rate * 1.007)  # +7 cents
                        }).set_frame_rate(audio.frame_rate) - 6
                        
                        chorus2 = audio._spawn(audio.raw_data, overrides={
                            "frame_rate": int(audio.frame_rate * 0.993)  # -7 cents
                        }).set_frame_rate(audio.frame_rate) - 6
                        
                        chorus3 = audio._spawn(audio.raw_data, overrides={
                            "frame_rate": int(audio.frame_rate * 1.012)  # +12 cents
                        }).set_frame_rate(audio.frame_rate) - 9
                        
                        audio = audio.overlay(chorus1, position=15)
                        audio = audio.overlay(chorus2, position=30)
                        audio = audio.overlay(chorus3, position=45)
                    except Exception as e:
                        logging.warning(f"Error in chorus effect: {str(e)}")
                
                elif audio_effect == 'distortion':
                    # Enhanced distortion effect with better safeguards
                    try:
                        # Compression with safe parameters
                        audio = audio.compress_dynamic_range(threshold=-20.0, ratio=10.0, attack=0.1, release=10.0)
                        
                        # Bass boost for more intense distortion effect
                        filter_freq = 100  # Hz
                        low_shelf_gain = 5.0  # dB
                        audio = audio.low_shelf_filter(filter_freq, low_shelf_gain)
                        
                        # Add high-frequency enhancement for "edge"
                        audio = audio.high_shelf_filter(4000, 3.0)
                        
                        # Increase volume to compensate for distortion
                        audio = audio + 3
                    except Exception as e:
                        logging.warning(f"Error in distortion effect: {str(e)}")
                
                elif audio_effect == 'telephone':
                    # Create classic telephone/radio sound effect
                    try:
                        # Apply band-pass filter to simulate telephone frequency response (300Hz-3.4kHz)
                        audio = audio.high_pass_filter(300)
                        audio = audio.low_pass_filter(3400)
                        # Add mild distortion
                        audio = audio.compress_dynamic_range(threshold=-15, ratio=4.0)
                        # Add subtle noise
                        noise = AudioSegment.silent(duration=len(audio)).overlay(
                            AudioSegment.from_mono_audiosegments(
                                *[AudioSegment.silent(duration=50).low_pass_filter(1000) 
                                  for _ in range(len(audio) // 50 + 1)]
                            ) - 26
                        )
                        audio = audio.overlay(noise)
                    except Exception as e:
                        logging.warning(f"Error in telephone effect: {str(e)}")
                
                elif audio_effect == 'megaphone':
                    # Create megaphone/announcement effect
                    try:
                        # Apply band-pass filter with resonant mids
                        audio = audio.high_pass_filter(600)
                        audio = audio.low_pass_filter(4000)
                        # Heavy compression for "shouting" effect
                        audio = audio.compress_dynamic_range(threshold=-18, ratio=8.0, attack=0.01)
                        # Slight distortion for megaphone character
                        audio = audio + 4  # Increase volume
                    except Exception as e:
                        logging.warning(f"Error in megaphone effect: {str(e)}")
                
                elif audio_effect == 'whisper_effect':
                    # Create whisper effect
                    try:
                        # Reduce volume
                        audio = audio - 6
                        # High-pass filter to remove lower frequencies
                        audio = audio.high_pass_filter(800)
                        # Add breathiness
                        noise = AudioSegment.silent(duration=len(audio)).overlay(
                            AudioSegment.from_mono_audiosegments(
                                *[AudioSegment.silent(duration=50).high_shelf_filter(2000, 6) 
                                  for _ in range(len(audio) // 50 + 1)]
                            ) - 20
                        )
                        audio = audio.overlay(noise)
                    except Exception as e:
                        logging.warning(f"Error in whisper effect: {str(e)}")
                
                elif audio_effect == 'ethereal':
                    # Create ethereal voice effect
                    try:
                        # Add reverb-like effect with long tail
                        reverb = audio - 12
                        delays = [100, 200, 300, 400, 500, 600, 700, 800]
                        for i, delay in enumerate(delays):
                            echo = reverb - (2 * i)
                            audio = audio.overlay(echo, position=delay)
                        
                        # Add chorus for dreamy quality
                        chorus = audio._spawn(audio.raw_data, overrides={
                            "frame_rate": int(audio.frame_rate * 1.005)
                        }).set_frame_rate(audio.frame_rate) - 6
                        audio = audio.overlay(chorus, position=25)
                        
                        # Add high shimmer
                        audio = audio.high_shelf_filter(6000, 3)
                    except Exception as e:
                        logging.warning(f"Error in ethereal effect: {str(e)}")
                
                elif audio_effect == 'duet':
                    # Create voice layering duet effect
                    try:
                        # Create slightly modified copies of the original
                        voice1 = audio - 6
                        voice2 = audio._spawn(audio.raw_data, overrides={
                            "frame_rate": int(audio.frame_rate * 1.03)  # Up a minor third
                        }).set_frame_rate(audio.frame_rate) - 6
                        
                        voice3 = audio._spawn(audio.raw_data, overrides={
                            "frame_rate": int(audio.frame_rate * 0.84)  # Down a fifth
                        }).set_frame_rate(audio.frame_rate) - 9
                        
                        # Overlay with slight delays for chorus effect
                        audio = audio.overlay(voice1.fade_in(20), position=20)
                        audio = audio.overlay(voice2.fade_in(30), position=15)
                        audio = audio.overlay(voice3.fade_in(40), position=10)
                    except Exception as e:
                        logging.warning(f"Error in duet effect: {str(e)}")
            
            # Apply advanced prosody enhancements if enabled
            if prosody_level != 'default':
                try:
                    logging.debug(f"Applying prosody enhancements: {prosody_level}")
                    
                    # Get prosody settings for the selected level
                    if prosody_level not in PROSODY_SETTINGS:
                        prosody_level = 'natural'  # Fallback to natural if level not found
                    
                    settings = PROSODY_SETTINGS[prosody_level]
                    
                    # Apply sentence pause and micro-pause enhancements
                    if settings['sentence_pause'] > 0 or settings['punctuation_pause'] > 0 or settings['micro_pauses']:
                        # Split audio into smaller segments - estimate words by duration
                        # Assuming average word length ~300ms
                        avg_word_ms = 300
                        est_words = int(len(audio) / avg_word_ms)
                        
                        # Create realistic word boundaries by using variable segment lengths
                        segment_count = min(est_words, 20)  # Reasonable number of segments
                        base_segment_ms = len(audio) // segment_count
                        
                        # Create segments with natural variation
                        segments = []
                        position = 0
                        
                        for i in range(segment_count):
                            # Add variation to segment length
                            variation = 0
                            if settings['word_gap_variation'] > 0:
                                variation = int((random.random() * 2 - 1) * settings['word_gap_variation'] * base_segment_ms)
                            
                            segment_length = max(100, base_segment_ms + variation)
                            
                            # Ensure we don't exceed audio length
                            end_pos = min(position + segment_length, len(audio))
                            segments.append(audio[position:end_pos])
                            
                            # Add pause after segment
                            if i < segment_count - 1:  # Not the last segment
                                # Decide if this is a sentence boundary, punctuation, or just a word break
                                if random.random() < 0.15 and settings['sentence_pause'] > 0:
                                    # Sentence pause (~15% chance)
                                    pause_duration = int(settings['sentence_pause'])
                                    segments.append(AudioSegment.silent(duration=pause_duration))
                                elif random.random() < 0.3 and settings['punctuation_pause'] > 0:
                                    # Punctuation pause (~30% chance)
                                    pause_duration = int(settings['punctuation_pause'])
                                    segments.append(AudioSegment.silent(duration=pause_duration))
                                elif settings['micro_pauses'] and random.random() < 0.2:
                                    # Micro-pause (~20% chance if enabled)
                                    segments.append(AudioSegment.silent(duration=int(random.randint(30, 80))))
                            
                            position = end_pos
                        
                        # Combine segments to create new audio with natural pauses
                        if segments:
                            audio = segments[0]
                            for segment in segments[1:]:
                                audio += segment
                
                    # Apply word emphasis if enabled
                    if settings['emphasis_words'] and enable_emphasis:
                        # We'll simulate word emphasis by applying volume variations
                        # This is a simplified approach since we can't easily detect words in audio
                        segment_length = min(300, int(len(audio) / 30))  # Approximate word size
                        
                        segments = []
                        for i in range(0, len(audio), segment_length):
                            segment = audio[i:i+segment_length]
                            
                            # Randomly emphasize some segments (~20% chance)
                            if random.random() < 0.2 and settings['intonation_strength'] > 0:
                                # Apply emphasis by increasing volume for important words
                                emphasis_db = settings['intonation_strength'] * 3  # 0-3dB boost
                                segment = segment + emphasis_db
                            
                            segments.append(segment)
                        
                        # Combine segments
                        if segments:
                            audio = segments[0]
                            for segment in segments[1:]:
                                audio += segment
                    
                    # Add breathiness if enabled
                    if settings['breathiness'] > 0:
                        try:
                            breath_intensity = settings['breathiness']
                            
                            # Create breath noise
                            breath_noise = AudioSegment.silent(duration=len(audio)).overlay(
                                AudioSegment.from_mono_audiosegments(
                                    *[AudioSegment.silent(duration=50).high_shelf_filter(3000, 10) 
                                      for _ in range(len(audio) // 50 + 1)]
                                ) - int(30 - (breath_intensity * 10))  # Adjust volume based on intensity
                            )
                            
                            # Apply breath noise
                            audio = audio.overlay(breath_noise)
                        except Exception as e:
                            logging.warning(f"Error applying breathiness: {str(e)}")
                
                except Exception as e:
                    logging.warning(f"Error applying prosody enhancements: {str(e)}")
            
            # Apply sentence analysis for dynamic emphasis if enabled
            if sentence_analysis:
                try:
                    logging.debug("Applying sentence analysis for dynamic emphasis")
                    
                    # Split text into sentences (simplified approach)
                    sentences = [s.strip() for s in text.split('.') if s.strip()]
                    
                    if sentences and len(sentences) > 1:
                        # Estimate audio duration per sentence
                        avg_sentence_ms = len(audio) // len(sentences)
                        
                        if avg_sentence_ms > 500:  # Only process if sentences are long enough
                            sentence_segments = []
                            
                            for i, sentence in enumerate(sentences):
                                # Calculate approximate position in audio for this sentence
                                start_pos = i * avg_sentence_ms
                                end_pos = min(start_pos + avg_sentence_ms, len(audio))
                                
                                if end_pos > start_pos:
                                    sentence_audio = audio[start_pos:end_pos]
                                    
                                    # Check if sentence contains emphasis words
                                    contains_emphasis = any(word.lower() in sentence.lower() for word in EMPHASIS_WORDS)
                                    
                                    # Apply processing based on sentence characteristics
                                    if contains_emphasis:
                                        # Boost important sentences
                                        sentence_audio = sentence_audio + 2  # +2dB
                                        
                                        # Add slight compression for clarity
                                        sentence_audio = sentence_audio.compress_dynamic_range(
                                            threshold=-20, ratio=2.0, attack=5.0, release=50.0
                                        )
                                    
                                    # Check for questions (simplified)
                                    if '?' in sentence:
                                        # Modify question intonation by increasing pitch towards the end
                                        half_point = len(sentence_audio) // 2
                                        first_half = sentence_audio[:half_point]
                                        second_half = sentence_audio[half_point:]
                                        
                                        # Increase pitch slightly at the end of questions
                                        modified_half = second_half._spawn(second_half.raw_data, overrides={
                                            "frame_rate": int(second_half.frame_rate * 1.03)
                                        }).set_frame_rate(audio.frame_rate)
                                        
                                        sentence_audio = first_half + modified_half
                                    
                                    sentence_segments.append(sentence_audio)
                            
                            # Combine sentence segments
                            if sentence_segments:
                                audio = sentence_segments[0]
                                for segment in sentence_segments[1:]:
                                    audio += segment
                
                except Exception as e:
                    logging.warning(f"Error applying sentence analysis: {str(e)}")
            
            # Apply voice layering for richness if enabled
            if voice_layering:
                try:
                    logging.debug("Applying voice layering effects")
                    
                    # Create a slightly detuned duplicate of the audio for richness
                    layer1 = audio._spawn(audio.raw_data, overrides={
                        "frame_rate": int(audio.frame_rate * 1.002)  # +2 cents
                    }).set_frame_rate(audio.frame_rate) - 12  # -12dB (much quieter)
                    
                    layer2 = audio._spawn(audio.raw_data, overrides={
                        "frame_rate": int(audio.frame_rate * 0.998)  # -2 cents
                    }).set_frame_rate(audio.frame_rate) - 12
                    
                    # Apply slight EQ differences to each layer
                    layer1 = layer1.high_shelf_filter(5000, 2)
                    layer2 = layer2.low_shelf_filter(300, 2)
                    
                    # Mix the layers with the original
                    audio = audio.overlay(layer1, position=5)
                    audio = audio.overlay(layer2, position=10)
                
                except Exception as e:
                    logging.warning(f"Error applying voice layering: {str(e)}")
            
            # Apply spectral enhancement for clarity if enabled
            if spectral_enhancement:
                try:
                    logging.debug("Applying spectral enhancement for clarity")
                    
                    # Enhance speech intelligibility by boosting key frequency ranges
                    
                    # Mild high-pass to remove rumble
                    audio = audio.high_pass_filter(100)
                    
                    # Boost speech "presence" range (around 3-4kHz)
                    audio = audio.high_shelf_filter(3000, 2)
                    
                    # Slight boost to articulation range (5-8kHz)
                    audio = audio.high_shelf_filter(5000, 1)
                    
                    # Apply subtle multi-band compression for balanced sound
                    audio = audio.compress_dynamic_range(threshold=-25, ratio=1.5, attack=5.0, release=100.0)
                    
                    # Normalize to ensure consistent volume level
                    audio = audio.normalize(headroom=0.5)
                
                except Exception as e:
                    logging.warning(f"Error applying spectral enhancement: {str(e)}")
            
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
        
    def get_prosody_settings(self):
        """Return the dictionary of supported prosody settings"""
        return PROSODY_SETTINGS
        
    def get_advanced_features(self):
        """Return a dictionary of available advanced speech features"""
        return {
            'prosody': {
                'levels': list(PROSODY_SETTINGS.keys()),
                'description': 'Natural speech rhythm enhancements'
            },
            'emphasis': {
                'description': 'Emphasis on important words and phrases'
            },
            'micro_pauses': {
                'description': 'Natural micro-pauses between phrases'
            },
            'sentence_analysis': {
                'description': 'Dynamic emphasis based on sentence content'
            },
            'voice_layering': {
                'description': 'Rich voice layering for fuller sound'
            },
            'spectral_enhancement': {
                'description': 'Enhanced audio clarity and presence'
            }
        }
