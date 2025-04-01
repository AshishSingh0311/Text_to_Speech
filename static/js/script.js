document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const inputText = document.getElementById('input-text');
    const languageSelect = document.getElementById('language-select');
    const emotionSelect = document.getElementById('emotion-select');
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

        // Get selected options
        const language = languageSelect.value;
        const emotion = emotionSelect.value;
        const format = formatSelect.value;

        // Update UI
        showAlert(`Generating ${emotion} speech in ${getLanguageName(language)}...`, 'info');
        loadingOverlay.classList.remove('d-none');
        audioInfo.textContent = 'Processing...';
        audioInfo.className = 'badge bg-warning';

        try {
            // Make API request
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    language: language,
                    emotion: emotion,
                    format: format
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Update audio player and download link
                audioPlayer.src = data.path;
                downloadLink.href = data.path;
                downloadLink.download = `neural_speech_${language}_${emotion}.${format}`;
                
                // Show audio section
                audioSection.classList.remove('d-none');
                
                // Update audio info
                const duration = data.duration ? ` (${Math.round(data.duration)}s)` : '';
                audioInfo.textContent = `${getLanguageName(data.language)} - ${capitalizeFirst(data.emotion)}${duration}`;
                audioInfo.className = 'badge bg-success';
                
                // Play audio
                audioPlayer.play();
                
                // Success message
                showAlert(`Speech successfully generated with ${capitalizeFirst(emotion)} emotion!`, 'success');
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
    
    // Capitalize first letter
    function capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // Show alert message
    function showAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.innerHTML = '';
        alertContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alertContainer.removeChild(alert);
            }, 150);
        }, 5000);
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
