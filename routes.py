from flask import render_template, request, jsonify, send_from_directory
import os
import logging
from tts_service import TextToSpeechService

def register_routes(app):
    """Register all routes with the Flask app"""
    
    # Initialize TTS service
    tts_service = TextToSpeechService(os.path.join(app.root_path, 'static'))
    
    @app.route('/')
    def index():
        """Render the main page"""
        languages = tts_service.get_supported_languages()
        emotions = tts_service.get_supported_emotions()
        voice_types = tts_service.get_voice_types()
        audio_effects = tts_service.get_audio_effects()
        advanced_features = tts_service.get_advanced_features()
        prosody_settings = tts_service.get_prosody_settings()
        
        return render_template('index.html', 
                              languages=languages, 
                              emotions=emotions,
                              voice_types=voice_types,
                              audio_effects=audio_effects,
                              advanced_features=advanced_features,
                              prosody_settings=prosody_settings)
                              
    @app.route('/playground')
    def sound_playground():
        """Render the interactive sound wave playground"""
        # Pass the emotion parameters to the template for visualization
        from tts_service import EMOTION_PARAMETERS
        emotions = tts_service.get_supported_emotions()
        voice_types = tts_service.get_voice_types()
        audio_effects = tts_service.get_audio_effects()
        advanced_features = tts_service.get_advanced_features()
        prosody_settings = tts_service.get_prosody_settings()
        
        return render_template('playground.html',
                              emotions=emotions,
                              emotion_parameters=EMOTION_PARAMETERS,
                              voice_types=voice_types,
                              audio_effects=audio_effects,
                              advanced_features=advanced_features,
                              prosody_settings=prosody_settings)
    
    @app.route('/api/tts', methods=['POST'])
    def generate_tts():
        """API endpoint to generate TTS audio with advanced features"""
        try:
            # Get request data
            data = request.json
            text = data.get('text', '')
            language = data.get('language', 'en')
            emotion = data.get('emotion', 'neutral')
            voice_type = data.get('voice_type', 'default')
            format = data.get('format', 'mp3')
            
            # Get optional advanced parameters
            custom_speed = data.get('custom_speed')
            custom_pitch = data.get('custom_pitch') 
            custom_volume = data.get('custom_volume')
            audio_effect = data.get('audio_effect', 'none')
            
            # Get advanced speech enhancement parameters
            prosody_level = data.get('prosody_level', 'default')
            enable_emphasis = data.get('enable_emphasis', True)
            micro_pauses = data.get('micro_pauses', False)
            sentence_analysis = data.get('sentence_analysis', False)
            voice_layering = data.get('voice_layering', False)
            spectral_enhancement = data.get('spectral_enhancement', False)
            
            # Convert numeric parameters if provided as strings
            if custom_speed is not None:
                try:
                    custom_speed = float(custom_speed)
                except (ValueError, TypeError):
                    custom_speed = None
                    
            if custom_pitch is not None:
                try:
                    custom_pitch = int(custom_pitch)
                except (ValueError, TypeError):
                    custom_pitch = None
                    
            if custom_volume is not None:
                try:
                    custom_volume = int(custom_volume)
                except (ValueError, TypeError):
                    custom_volume = None
            
            # Validate input
            if not text or len(text.strip()) == 0:
                return jsonify({
                    'success': False,
                    'error': 'Text cannot be empty'
                }), 400
                
            # Count words (rough approximation)
            word_count = len(text.split())
            
            # Check text length - allow up to 400 words
            if word_count > 400:
                return jsonify({
                    'success': False,
                    'error': f'Text exceeds maximum length of 400 words (current: {word_count} words)'
                }), 400
            
            # Log the generation with basic and advanced parameters
            logging.info(
                f"Generating TTS - Language: {language}, Voice: {voice_type}, " 
                f"Emotion: {emotion}, Effect: {audio_effect}, Word count: {word_count}, "
                f"Advanced Features: [Prosody: {prosody_level}, Sentence Analysis: {sentence_analysis}, "
                f"Voice Layering: {voice_layering}, Spectral Enhancement: {spectral_enhancement}]"
            )
                
            # Generate speech with all parameters
            result = tts_service.generate_speech(
                text=text,
                language=language,
                emotion=emotion,
                voice_type=voice_type,
                custom_speed=custom_speed,
                custom_pitch=custom_pitch,
                custom_volume=custom_volume,
                audio_effect=audio_effect,
                prosody_level=prosody_level,
                enable_emphasis=enable_emphasis,
                micro_pauses=micro_pauses,
                sentence_analysis=sentence_analysis,
                voice_layering=voice_layering,
                spectral_enhancement=spectral_enhancement,
                format=format
            )
            
            if result['success']:
                # Add word count to response
                result['word_count'] = word_count
                
                # Add visual emotion parameters for enhanced UI
                from tts_service import EMOTION_PARAMETERS
                if emotion in EMOTION_PARAMETERS:
                    result['emotion_color'] = EMOTION_PARAMETERS[emotion]['color']
                    result['emotion_animation'] = EMOTION_PARAMETERS[emotion]['animation']
                
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logging.error(f"Error in TTS API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    @app.route('/api/languages', methods=['GET'])
    def get_languages():
        """API endpoint to get supported languages"""
        return jsonify({
            'languages': tts_service.get_supported_languages()
        })
        
    @app.route('/api/emotions', methods=['GET'])
    def get_emotions():
        """API endpoint to get supported emotions"""
        from tts_service import EMOTION_PARAMETERS
        
        # Return both simple list and detailed parameters
        emotions_simple = tts_service.get_supported_emotions()
        
        # Create an enhanced version with visual attributes
        emotions_enhanced = {}
        for emotion in emotions_simple:
            if emotion in EMOTION_PARAMETERS:
                emotions_enhanced[emotion] = {
                    'color': EMOTION_PARAMETERS[emotion]['color'],
                    'animation': EMOTION_PARAMETERS[emotion]['animation'],
                    'variability': EMOTION_PARAMETERS[emotion]['variability'],
                    'speed': EMOTION_PARAMETERS[emotion]['speed'],
                    'pitch': EMOTION_PARAMETERS[emotion]['pitch'],
                    'volume': EMOTION_PARAMETERS[emotion]['volume'],
                    'emphasis': EMOTION_PARAMETERS[emotion]['emphasis']
                }
        
        return jsonify({
            'emotions': emotions_simple,
            'emotion_parameters': emotions_enhanced
        })
        
    @app.route('/api/voice-types', methods=['GET'])
    def get_voice_types():
        """API endpoint to get supported voice types"""
        return jsonify({
            'voice_types': tts_service.get_voice_types()
        })
        
    @app.route('/api/audio-effects', methods=['GET'])
    def get_audio_effects():
        """API endpoint to get supported audio effects"""
        return jsonify({
            'audio_effects': tts_service.get_audio_effects()
        })
        
    @app.route('/api/advanced-features', methods=['GET'])
    def get_advanced_features():
        """API endpoint to get supported advanced speech features"""
        return jsonify({
            'advanced_features': tts_service.get_advanced_features(),
            'prosody_settings': tts_service.get_prosody_settings()
        })
        
    @app.route('/api/manipulate-audio', methods=['POST'])
    def manipulate_audio():
        """API endpoint to manipulate an existing audio file with new parameters"""
        try:
            # Get request data
            data = request.json
            audio_path = data.get('audio_path', '')
            
            # Get manipulation parameters
            speed = data.get('speed')
            pitch = data.get('pitch')
            volume = data.get('volume')
            eq_bass = data.get('eq_bass')
            eq_mid = data.get('eq_mid')
            eq_treble = data.get('eq_treble')
            effect_type = data.get('effect_type', 'none')
            effect_intensity = data.get('effect_intensity', 0.5)
            
            # Convert numeric parameters if provided as strings
            if speed is not None:
                try:
                    speed = float(speed)
                except (ValueError, TypeError):
                    speed = 1.0
                    
            if pitch is not None:
                try:
                    pitch = int(pitch)
                except (ValueError, TypeError):
                    pitch = 0
                    
            if volume is not None:
                try:
                    volume = int(volume)
                except (ValueError, TypeError):
                    volume = 0
                    
            # Validate input
            if not audio_path or len(audio_path.strip()) == 0:
                return jsonify({
                    'success': False,
                    'error': 'Audio path cannot be empty'
                }), 400
                
            # Remove /static/ prefix if it exists
            if audio_path.startswith('/static/'):
                audio_path = audio_path[8:]  # Remove "/static/" prefix
                
            # Check if the audio file exists
            full_path = os.path.join(app.root_path, 'static', audio_path)
            if not os.path.exists(full_path):
                return jsonify({
                    'success': False,
                    'error': 'Audio file not found'
                }), 404
                
            logging.info(f"Manipulating audio: {audio_path}, Speed: {speed}, Pitch: {pitch}, Volume: {volume}, Effect: {effect_type}")
                
            # Process the audio with pydub
            from pydub import AudioSegment
            import uuid
            
            try:
                # Load the audio file
                audio = AudioSegment.from_file(full_path)
                
                # Apply speed modification
                if speed and speed != 1.0:
                    speed = max(0.5, min(2.0, speed))  # Clamp between 0.5 and 2.0
                    audio = audio._spawn(audio.raw_data, overrides={
                        "frame_rate": int(audio.frame_rate * speed)
                    })
                    audio = audio.set_frame_rate(44100)  # Reset to standard frame rate
                
                # Apply pitch modification
                if pitch and pitch != 0:
                    pitch = max(-10, min(10, pitch))  # Clamp between -10 and 10
                    new_sample_rate = int(audio.frame_rate * (2 ** (pitch / 12.0)))
                    audio = audio._spawn(audio.raw_data, overrides={
                        "frame_rate": new_sample_rate
                    })
                    audio = audio.set_frame_rate(44100)  # Reset to standard frame rate
                
                # Apply volume adjustment
                if volume and volume != 0:
                    volume = max(-10, min(10, volume))  # Clamp between -10 and 10
                    audio = audio + volume
                
                # Apply EQ adjustments
                if eq_bass is not None:
                    eq_bass = float(eq_bass)
                    audio = audio.low_shelf_filter(200, eq_bass)
                
                if eq_mid is not None:
                    eq_mid = float(eq_mid)
                    if eq_mid > 0:
                        audio = audio.band_pass_filter(1000, q=1.0)
                        audio = audio + eq_mid
                    else:
                        audio = audio.band_pass_filter(1000, q=1.0)
                        audio = audio - abs(eq_mid)
                
                if eq_treble is not None:
                    eq_treble = float(eq_treble)
                    audio = audio.high_shelf_filter(4000, eq_treble)
                
                # Apply audio effect
                if effect_type and effect_type != 'none':
                    effect_intensity = max(0.1, min(1.0, effect_intensity))
                    
                    if effect_type == 'echo':
                        # Create echo effect with dynamic delay
                        delay_ms = int(300 * effect_intensity)
                        echo_sound = audio - (6 * effect_intensity)
                        audio = audio.overlay(echo_sound, position=delay_ms)
                    
                    elif effect_type == 'reverb':
                        # Apply reverb with dynamic intensity
                        reverb_count = int(5 * effect_intensity) + 1
                        reverb_sound = audio - (10 * effect_intensity)
                        delays = [50, 100, 150, 200, 250, 300, 350]
                        for i in range(reverb_count):
                            if i < len(delays):
                                delay = delays[i]
                                echo = reverb_sound - (delay // 20)
                                audio = audio.overlay(echo, position=delay)
                    
                    elif effect_type == 'chorus':
                        # Apply chorus with dynamic intensity
                        chorus1 = audio._spawn(audio.raw_data, overrides={
                            "frame_rate": int(audio.frame_rate * (1 + 0.007 * effect_intensity))
                        }).set_frame_rate(audio.frame_rate) - (6 * effect_intensity)
                        
                        chorus2 = audio._spawn(audio.raw_data, overrides={
                            "frame_rate": int(audio.frame_rate * (1 - 0.007 * effect_intensity))
                        }).set_frame_rate(audio.frame_rate) - (6 * effect_intensity)
                        
                        audio = audio.overlay(chorus1, position=15)
                        audio = audio.overlay(chorus2, position=30)
                    
                    elif effect_type == 'distortion':
                        # Apply distortion with dynamic intensity
                        audio = audio.compress_dynamic_range(threshold=-20.0, ratio=10.0 * effect_intensity)
                        audio = audio.low_shelf_filter(100, 5.0 * effect_intensity)
                        audio = audio + (3 * effect_intensity)
                
                # Generate a unique filename for the modified audio
                filename = f"modified_{uuid.uuid4()}.mp3"
                filepath = os.path.join(app.root_path, 'static', 'audio', filename)
                
                # Export the audio
                audio.export(filepath, format="mp3", bitrate="192k")
                
                # Return the path to the modified audio
                return jsonify({
                    'success': True,
                    'path': f'/static/audio/{filename}',
                    'duration': len(audio) / 1000  # Duration in seconds
                })
                
            except Exception as e:
                logging.error(f"Error processing audio: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f"Error processing audio: {str(e)}"
                }), 500
                
        except Exception as e:
            logging.error(f"Error in manipulate audio API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        return render_template('error.html', error='Page not found'), 404
        
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors"""
        return render_template('error.html', error='Server error occurred'), 500
