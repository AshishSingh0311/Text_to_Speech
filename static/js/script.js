document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements - Basic UI
    const inputText = document.getElementById('input-text');
    const languageSelect = document.getElementById('language-select');
    const emotionSelect = document.getElementById('emotion-select');
    const voiceSelect = document.getElementById('voice-select');
    const effectSelect = document.getElementById('effect-select');
    const formatSelect = document.getElementById('format-select');
    const generateBtn = document.getElementById('generate-btn');
    const audioSection = document.getElementById('audio-section');
    const audioPlayer = document.getElementById('audio-player');
    const downloadLink = document.getElementById('download-link');
    const regenerateBtn = document.getElementById('regenerate-btn');
    const shareBtn = document.getElementById('share-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const characterCount = document.getElementById('character-count');
    const wordCount = document.getElementById('word-count');
    const audioInfo = document.getElementById('audio-info');
    const alertContainer = document.getElementById('alert-container');
    const toggleAdvanced = document.getElementById('toggle-advanced');
    
    // Advanced slider controls
    const speedSlider = document.getElementById('speed-slider');
    const pitchSlider = document.getElementById('pitch-slider');
    const volumeSlider = document.getElementById('volume-slider');
    const speedValue = document.getElementById('speed-value');
    const pitchValue = document.getElementById('pitch-value');
    const volumeValue = document.getElementById('volume-value');
    const resetParams = document.getElementById('reset-params');
    
    // Flag to track if parameters were customized
    let usingCustomParameters = false;
    
    // Bootstrap collapse - manually initialize for advanced section
    toggleAdvanced.addEventListener('click', function() {
        const advancedOptions = document.getElementById('advancedOptions');
        if (advancedOptions.classList.contains('show')) {
            advancedOptions.classList.remove('show');
            toggleAdvanced.innerHTML = '<i class="fas fa-cogs me-1"></i> Advanced Options';
        } else {
            advancedOptions.classList.add('show');
            toggleAdvanced.innerHTML = '<i class="fas fa-minus me-1"></i> Hide Advanced Options';
        }
    });

    // Text counters
    inputText.addEventListener('input', function() {
        const text = this.value;
        const charCount = text.length;
        const words = text.trim() ? text.trim().split(/\s+/) : [];
        const wordCountValue = words.length;
        
        // Update character count
        characterCount.textContent = `${charCount} characters`;
        
        // Update word count
        wordCount.textContent = `${wordCountValue} words`;
        
        // Change colors based on limits
        if (wordCountValue > 400) {
            wordCount.className = 'badge bg-danger me-2';
        } else if (wordCountValue > 350) {
            wordCount.className = 'badge bg-warning me-2';
        } else {
            wordCount.className = 'badge bg-primary me-2';
        }
        
        if (charCount > 2000) {
            characterCount.className = 'badge bg-danger';
        } else if (charCount > 1500) {
            characterCount.className = 'badge bg-warning';
        } else {
            characterCount.className = 'badge bg-secondary';
        }
    });
    
    // Sliders for advanced parameters
    speedSlider.addEventListener('input', function() {
        speedValue.textContent = `${this.value}×`;
        usingCustomParameters = true;
    });
    
    pitchSlider.addEventListener('input', function() {
        const sign = this.value > 0 ? '+' : '';
        pitchValue.textContent = `${sign}${this.value} semitones`;
        usingCustomParameters = true;
    });
    
    volumeSlider.addEventListener('input', function() {
        const sign = this.value > 0 ? '+' : '';
        volumeValue.textContent = `${sign}${this.value} dB`;
        usingCustomParameters = true;
    });
    
    // Reset parameters to default
    resetParams.addEventListener('click', function() {
        speedSlider.value = 1.0;
        pitchSlider.value = 0;
        volumeSlider.value = 0;
        speedValue.textContent = '1.0×';
        pitchValue.textContent = '+0 semitones';
        volumeValue.textContent = '+0 dB';
        usingCustomParameters = false;
        showAlert('Parameters reset to default values', 'info');
    });

    // Voice and emotion selection events 
    voiceSelect.addEventListener('change', function() {
        updateAudioDescription();
    });
    
    emotionSelect.addEventListener('change', function() {
        updateAudioDescription();
    });
    
    effectSelect.addEventListener('change', function() {
        updateAudioDescription();
    });
    
    // Display description of current voice settings
    function updateAudioDescription() {
        const voice = voiceSelect.options[voiceSelect.selectedIndex].text;
        const emotion = emotionSelect.options[emotionSelect.selectedIndex].text;
        const effect = effectSelect.options[effectSelect.selectedIndex].text;
        
        let description = `${voice} voice with ${emotion.toLowerCase()} emotion`;
        if (effect !== 'No Effect') {
            description += ` and ${effect.toLowerCase()} effect`;
        }
        
        if (usingCustomParameters) {
            description += ' (custom parameters)';
        }
        
        showAlert(description, 'info', 3000);
    }

    // Generate speech
    generateBtn.addEventListener('click', generateSpeech);
    regenerateBtn.addEventListener('click', generateSpeech);
    
    // Share functionality
    shareBtn.addEventListener('click', copyAudioLink);

    async function generateSpeech() {
        // Validate input
        const text = inputText.value.trim();
        if (!text) {
            showAlert('Please enter some text to convert to speech.', 'warning');
            return;
        }

        // Count words
        const wordCountValue = text.split(/\s+/).length;
        if (wordCountValue > 400) {
            showAlert(`Text is too long. Please limit your text to 400 words. Current count: ${wordCountValue} words.`, 'danger');
            return;
        }

        // Get basic options
        const language = languageSelect.value;
        const emotion = emotionSelect.value;
        const voice_type = voiceSelect.value;
        const format = formatSelect.value;
        const audio_effect = effectSelect.value;
        
        // Get custom parameters if enabled
        const custom_speed = usingCustomParameters ? parseFloat(speedSlider.value) : null;
        const custom_pitch = usingCustomParameters ? parseInt(pitchSlider.value) : null;
        const custom_volume = usingCustomParameters ? parseInt(volumeSlider.value) : null;

        // Update UI
        const voiceName = voiceSelect.options[voiceSelect.selectedIndex].text;
        showAlert(`Generating ${emotion} speech with ${voiceName} voice in ${getLanguageName(language)}...`, 'info');
        loadingOverlay.classList.remove('d-none');
        audioInfo.textContent = 'Processing...';
        audioInfo.className = 'badge bg-warning';

        try {
            // Make API request with all parameters
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    language: language,
                    emotion: emotion,
                    voice_type: voice_type,
                    custom_speed: custom_speed,
                    custom_pitch: custom_pitch, 
                    custom_volume: custom_volume,
                    audio_effect: audio_effect,
                    format: format
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Update audio player and download link
                audioPlayer.src = data.path;
                downloadLink.href = data.path;
                downloadLink.download = `neural_speech_${language}_${voice_type}_${emotion}.${format}`;
                
                // Show audio section
                audioSection.classList.remove('d-none');
                
                // Update audio info
                const duration = data.duration ? ` (${Math.round(data.duration)}s)` : '';
                const voiceInfo = getVoiceName(data.voice_type);
                const effectInfo = audio_effect !== 'none' ? ` + ${capitalizeFirst(audio_effect)}` : '';
                
                audioInfo.textContent = `${getLanguageName(data.language)} - ${voiceInfo} - ${capitalizeFirst(data.emotion)}${effectInfo}${duration}`;
                audioInfo.className = 'badge bg-success';
                
                // Play audio
                audioPlayer.play();
                
                // Success message
                showAlert(`Speech successfully generated! (${Math.round(data.duration)}s)`, 'success');
            } else {
                // Show error
                audioInfo.textContent = 'Failed';
                audioInfo.className = 'badge bg-danger';
                showAlert(`Error: ${data.error || 'Failed to generate speech'}`, 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            audioInfo.textContent = 'Error';
            audioInfo.className = 'badge bg-danger';
            showAlert('Failed to connect to the server. Please try again.', 'danger');
        } finally {
            // Hide loading overlay
            loadingOverlay.classList.add('d-none');
        }
    }
    
    // Copy audio link to clipboard
    function copyAudioLink() {
        if (!audioPlayer.src) return;
        
        // Get the current URL
        const audioUrl = audioPlayer.src;
        
        // Copy to clipboard
        navigator.clipboard.writeText(audioUrl).then(() => {
            showAlert('Audio link copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            showAlert('Failed to copy link. Please try again.', 'danger');
        });
    }
    
    // Get language name from code
    function getLanguageName(code) {
        const option = languageSelect.querySelector(`option[value="${code}"]`);
        return option ? option.textContent : code;
    }
    
    // Get voice name from type
    function getVoiceName(type) {
        const option = voiceSelect.querySelector(`option[value="${type}"]`);
        return option ? option.textContent : capitalizeFirst(type);
    }
    
    // Capitalize first letter
    function capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // Show alert message
    function showAlert(message, type = 'info', duration = 5000) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.innerHTML = '';
        alertContainer.appendChild(alert);
        
        // Auto-dismiss after duration
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                if (alert.parentElement) {
                    alertContainer.removeChild(alert);
                }
            }, 150);
        }, duration);
    }

    // Handle alert dismissal without Bootstrap JS
    alertContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-close')) {
            const alert = e.target.parentElement;
            alert.classList.remove('show');
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.parentElement.removeChild(alert);
                }
            }, 150);
        }
    });
    
    // Audio player events
    audioPlayer.addEventListener('play', function() {
        audioInfo.className = 'badge bg-info animate__animated animate__pulse animate__infinite';
    });
    
    audioPlayer.addEventListener('pause', function() {
        audioInfo.className = 'badge bg-success';
    });
    
    audioPlayer.addEventListener('ended', function() {
        audioInfo.className = 'badge bg-secondary';
    });
    
    // Trigger word and character count on load
    inputText.dispatchEvent(new Event('input'));
});
