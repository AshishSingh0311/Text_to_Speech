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
        return render_template('index.html', languages=languages, emotions=emotions)
    
    @app.route('/api/tts', methods=['POST'])
    def generate_tts():
        """API endpoint to generate TTS audio with advanced features"""
        try:
            # Get request data
            data = request.json
            text = data.get('text', '')
            language = data.get('language', 'en')
            emotion = data.get('emotion', 'neutral')
            format = data.get('format', 'mp3')
            
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
            
            logging.info(f"Generating TTS - Language: {language}, Emotion: {emotion}, Word count: {word_count}")
                
            # Generate speech
            result = tts_service.generate_speech(text, language, emotion, format)
            
            if result['success']:
                # Add word count to response
                result['word_count'] = word_count
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
        return jsonify({
            'emotions': tts_service.get_supported_emotions()
        })
        
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        return render_template('error.html', error='Page not found'), 404
        
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors"""
        return render_template('error.html', error='Server error occurred'), 500
