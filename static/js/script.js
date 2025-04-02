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
    const loadingText = document.getElementById('loading-text');
    const loadingProgress = document.getElementById('loading-progress');
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
        
        // Start playful loading animation with fun messages
        startLoadingAnimation(text.length, emotion, voice_type);
        
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
                
                // Store emotion color and animation from server response if available
                if (data.emotion_color) {
                    emotionDisplay.dataset.emotionColor = data.emotion_color;
                }
                
                if (data.emotion_animation) {
                    emotionDisplay.dataset.emotionAnimation = data.emotion_animation;
                }
                
                // Update and show emotion display with enhanced visuals
                updateEmotionDisplay(data.emotion);
                emotionDisplay.classList.remove('d-none');
                
                // Apply emotion-specific styling to audio player
                const audioContainer = document.querySelector('.audio-player-container');
                if (audioContainer && data.emotion_color) {
                    // Add subtle border glow based on emotion color
                    audioContainer.style.boxShadow = `0 0 15px ${data.emotion_color}40`; // 40 = 25% opacity in hex
                }
                
                // The waveform will be activated when the audio starts playing
                
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
    
    // Define emotion icon mappings
    const emotionIcons = {
        'neutral': {icon: 'fa-meh', animation: ''},
        'happy': {icon: 'fa-smile-beam', animation: 'pulse'},
        'sad': {icon: 'fa-sad-tear', animation: 'fade'},
        'angry': {icon: 'fa-angry', animation: 'shake'},
        'excited': {icon: 'fa-grin-stars', animation: 'bounce'},
        'calm': {icon: 'fa-smile', animation: ''},
        'fearful': {icon: 'fa-grimace', animation: 'wobble'},
        'whisper': {icon: 'fa-hushed', animation: 'fade'},
        'shouting': {icon: 'fa-surprise', animation: 'shake'}
    };
    
    // Elements for emotion display
    const emotionDisplay = document.getElementById('emotion-display');
    const emotionIcon = document.getElementById('emotion-icon');
    const emotionLabel = document.getElementById('emotion-label');
    const waveform = document.querySelector('.waveform');
    
    // Update emotion display based on current emotion with enhanced animations
    function updateEmotionDisplay(emotion) {
        // Default icon if emotion not found
        let iconClass = 'fa-meh';
        let animationClass = '';
        
        // If we have a mapping for this emotion
        if (emotionIcons[emotion]) {
            iconClass = emotionIcons[emotion].icon;
            animationClass = emotionIcons[emotion].animation;
        }
        
        // Clear previous classes
        emotionIcon.className = '';
        
        // Remove all emotion classes from the container
        const containerClasses = ['happy', 'sad', 'angry', 'excited', 'calm', 'fearful', 'whisper', 'shouting', 'active'];
        containerClasses.forEach(cls => {
            emotionDisplay.classList.remove(cls);
        });
        
        // Add emotion class to container for background effects
        emotionDisplay.classList.add(emotion);
        emotionDisplay.classList.add('active'); // Activate glow animation
        
        // Add new icon and animation classes
        emotionIcon.classList.add('fas', iconClass, 'emotion-' + emotion);
        if (animationClass) {
            emotionIcon.classList.add(animationClass);
        }
        
        // Update label with emotion-specific styling
        emotionLabel.textContent = capitalizeFirst(emotion);
        
        // Apply emotion-specific color to label
        let badgeColorClass = 'bg-info';
        
        switch(emotion) {
            case 'happy':
                badgeColorClass = 'bg-warning text-dark';
                break;
            case 'sad':
                badgeColorClass = 'bg-primary';
                break;
            case 'angry':
                badgeColorClass = 'bg-danger';
                break;
            case 'excited':
                badgeColorClass = 'bg-orange text-dark'; // Bootstrap doesn't have orange by default
                badgeColorClass = 'bg-warning text-dark'; // Fallback to warning
                break;
            case 'calm':
                badgeColorClass = 'bg-success';
                break;
            case 'fearful':
                badgeColorClass = 'bg-purple'; // Custom class for purple
                badgeColorClass = 'bg-secondary'; // Fallback if custom not available
                break;
            case 'whisper':
                badgeColorClass = 'bg-secondary';
                break;
            case 'shouting':
                badgeColorClass = 'bg-pink text-white'; // Custom class for pink
                badgeColorClass = 'bg-danger'; // Fallback if custom not available 
                break;
        }
        
        emotionLabel.className = `badge rounded-pill ${badgeColorClass}`;
        
        // Apply dynamic styling to the audio player interface
        const audioInfoPanel = document.querySelector('.card-header');
        if (audioInfoPanel) {
            // Reset previous styles
            audioInfoPanel.style.borderColor = '';
            
            // Add subtle emotion-based accent
            if (emotion !== 'neutral') {
                const emotionColorClass = getComputedStyle(emotionIcon).color;
                audioInfoPanel.style.borderColor = emotionColorClass;
            }
        }
    }
    
    // Enhanced audio player events with dynamic emotion animations
    audioPlayer.addEventListener('play', function() {
        audioInfo.className = 'badge bg-info animate__animated animate__pulse animate__infinite';
        
        // Show emotion display when playing
        emotionDisplay.classList.remove('d-none');
        
        // Get current emotion from the emotion select or from stored data
        const currentEmotion = emotionSelect.value;
        
        // Enable dynamic animation effects on play
        updateEmotionDisplay(currentEmotion);
        emotionDisplay.classList.add('active'); // Activate glow effects
        
        // Use server-provided animation if available, otherwise use default
        let animationClass = emotionDisplay.dataset.emotionAnimation || 
                            (emotionIcons[currentEmotion] ? emotionIcons[currentEmotion].animation : '');
        
        if (animationClass && !emotionIcon.classList.contains(animationClass)) {
            emotionIcon.classList.add(animationClass);
        }
        
        // Apply dynamic color to waveform based on emotion
        if (waveform && emotionDisplay.dataset.emotionColor) {
            const emotionColor = emotionDisplay.dataset.emotionColor;
            const waveBars = waveform.querySelectorAll('.bar');
            waveBars.forEach(bar => {
                bar.style.backgroundColor = emotionColor;
                bar.style.opacity = '0.7'; // Semi-transparent
            });
        }
        
        // Activate waveform animation
        if (waveform) {
            waveform.classList.add('active');
        }
        
        // Add a dynamic border to the audio player during playback
        const audioContainer = document.querySelector('.audio-player-container');
        if (audioContainer && emotionDisplay.dataset.emotionColor) {
            audioContainer.style.borderColor = emotionDisplay.dataset.emotionColor;
            audioContainer.style.transition = 'border-color 0.3s ease';
        }
    });
    
    audioPlayer.addEventListener('pause', function() {
        audioInfo.className = 'badge bg-success';
        
        // Reduce animation intensity but keep display visible
        if (emotionDisplay.classList.contains('active')) {
            emotionDisplay.classList.remove('active');
        }
        
        // If there's an animation class, temporarily remove it on pause
        const animationClasses = ['pulse', 'shake', 'bounce', 'wobble', 'fade'];
        animationClasses.forEach(cls => {
            if (emotionIcon.classList.contains(cls)) {
                emotionIcon.dataset.pausedAnimation = cls; // Store for resuming
                emotionIcon.classList.remove(cls);
            }
        });
        
        // Pause waveform animation
        if (waveform) {
            waveform.classList.remove('active');
        }
        
        // Subtle visual indicator that playback is paused
        const audioContainer = document.querySelector('.audio-player-container');
        if (audioContainer) {
            audioContainer.style.opacity = '0.9';
        }
    });
    
    audioPlayer.addEventListener('ended', function() {
        audioInfo.className = 'badge bg-secondary';
        
        // Reduce emotion display intensity but don't hide
        emotionDisplay.classList.remove('active');
        
        // Remove animation classes
        const animationClasses = ['pulse', 'shake', 'bounce', 'wobble', 'fade'];
        animationClasses.forEach(cls => {
            emotionIcon.classList.remove(cls);
            delete emotionIcon.dataset.pausedAnimation;
        });
        
        // Stop waveform animation
        if (waveform) {
            waveform.classList.remove('active');
        }
        
        // Reset any dynamic styling
        const audioContainer = document.querySelector('.audio-player-container');
        if (audioContainer) {
            audioContainer.style.borderColor = '';
            audioContainer.style.opacity = '1';
        }
    });
    
    // Trigger word and character count on load
    inputText.dispatchEvent(new Event('input'));
    
    // Loading animation variables and messages
    let loadingInterval = null;
    let progressValue = 0;
    let loadingPhase = 0;
    
    // Fun loading messages for different emotions and phases
    const loadingMessages = {
        initializing: [
            "Warming up the neural circuits...",
            "Preparing voice generation...",
            "Initializing linguistic processors...",
            "Loading speech patterns..."
        ],
        processing: {
            neutral: ["Generating neutral speech...", "Processing with default emotional settings..."],
            happy: ["Adding a splash of joy...", "Infusing text with happiness...", "Smiling while speaking..."],
            sad: ["Adding a touch of melancholy...", "Creating gently sorrowful tones..."],
            angry: ["Heating up the voice...", "Adding a dash of intensity..."],
            excited: ["Pumping up the enthusiasm...", "Adding extra energy to speech..."],
            calm: ["Creating serene speech patterns...", "Smoothing out the voice waves..."],
            fearful: ["Adding a slight tremble to the voice...", "Creating tension in the audio..."],
            whisper: ["Lowering the volume...", "Creating gentle hushed tones..."],
            shouting: ["Amplifying voice projection...", "CRANKING UP THE VOLUME..."]
        },
        voiceTypes: {
            default: ["Configuring baseline voice parameters..."],
            male: ["Adjusting voice for masculine qualities..."],
            female: ["Tuning voice for feminine characteristics..."],
            child: ["Raising pitch for childlike qualities..."],
            elderly: ["Adding character to the voice..."],
            robot: ["Initializing synthetic voice components..."]
        },
        finalizing: [
            "Adding final touches...",
            "Polishing the audio output...",
            "Packaging the speech...",
            "Preparing for playback..."
        ]
    };
    
    // Start the loading animation
    function startLoadingAnimation(textLength, emotion, voiceType) {
        // Show the loading overlay
        loadingOverlay.classList.remove('d-none');
        
        // Reset progress
        progressValue = 0;
        loadingPhase = 0;
        loadingProgress.style.width = '0%';
        
        // Estimate total time based on text length (just for animation purposes)
        const estimatedDuration = Math.min(5000 + (textLength / 20) * 100, 12000);
        const phaseCount = 4; // initialization, processing, voice styling, finalizing
        const phaseTime = estimatedDuration / phaseCount;
        
        // Clear any existing interval
        if (loadingInterval) {
            clearInterval(loadingInterval);
        }
        
        // Set the first message
        const initMessage = loadingMessages.initializing[Math.floor(Math.random() * loadingMessages.initializing.length)];
        loadingText.textContent = initMessage;
        
        // Start the progress animation
        loadingInterval = setInterval(() => {
            // Increase progress
            progressValue += 1;
            
            // Max progress for current phase (25%, 50%, 75%, 100%)
            const phaseMax = (loadingPhase + 1) * 25;
            
            // Update progress bar
            if (progressValue <= phaseMax) {
                loadingProgress.style.width = `${progressValue}%`;
                
                // Move to next phase when current phase completes
                if (progressValue === phaseMax && loadingPhase < 3) {
                    loadingPhase++;
                    updateLoadingMessage(emotion, voiceType);
                }
            } else if (progressValue > 100) {
                // Max out at 100%
                loadingProgress.style.width = '100%';
            }
            
            // Clear interval when done or after API response
            if (progressValue >= 100) {
                clearInterval(loadingInterval);
                loadingInterval = null;
            }
        }, phaseTime / 25); // Divide phase time into 25 steps
    }
    
    // Update loading message based on current phase
    function updateLoadingMessage(emotion, voiceType) {
        let message = '';
        
        switch (loadingPhase) {
            case 0: // Initialization
                message = loadingMessages.initializing[Math.floor(Math.random() * loadingMessages.initializing.length)];
                break;
                
            case 1: // Processing - emotion specific
                const emotionMessages = loadingMessages.processing[emotion] || loadingMessages.processing.neutral;
                message = emotionMessages[Math.floor(Math.random() * emotionMessages.length)];
                break;
                
            case 2: // Voice type specific
                const voiceMessages = loadingMessages.voiceTypes[voiceType] || loadingMessages.voiceTypes.default;
                message = voiceMessages[Math.floor(Math.random() * voiceMessages.length)];
                break;
                
            case 3: // Finalizing
                message = loadingMessages.finalizing[Math.floor(Math.random() * loadingMessages.finalizing.length)];
                break;
                
            default:
                message = "Processing your request...";
        }
        
        // Update the loading text with animation
        loadingText.style.opacity = "0";
        setTimeout(() => {
            loadingText.textContent = message;
            loadingText.style.opacity = "1";
        }, 300);
    }
});
