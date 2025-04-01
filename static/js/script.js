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
    const loadingOverlay = document.getElementById('loading-overlay');
    const characterCount = document.getElementById('character-count');
    const alertContainer = document.getElementById('alert-container');

    // Character counter
    inputText.addEventListener('input', function() {
        const count = this.value.length;
        characterCount.textContent = `${count}/800 characters`;
        
        // Change color if approaching or exceeding limit
        if (count > 800) {
            characterCount.className = 'badge bg-danger';
        } else if (count > 700) {
            characterCount.className = 'badge bg-warning';
        } else {
            characterCount.className = 'badge bg-secondary';
        }
    });

    // Generate speech
    generateBtn.addEventListener('click', generateSpeech);
    regenerateBtn.addEventListener('click', generateSpeech);

    async function generateSpeech() {
        // Validate input
        const text = inputText.value.trim();
        if (!text) {
            showAlert('Please enter some text to convert to speech.', 'warning');
            return;
        }

        if (text.length > 800) {
            showAlert('Text is too long. Please limit your text to 800 characters.', 'danger');
            return;
        }

        // Get selected options
        const language = languageSelect.value;
        const emotion = emotionSelect.value;
        const format = formatSelect.value;

        // Show loading overlay
        loadingOverlay.classList.remove('d-none');

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
                downloadLink.download = `speech-${emotion}-${language}.${format}`;
                
                // Show audio section
                audioSection.classList.remove('d-none');
                
                // Play audio
                audioPlayer.play();
            } else {
                // Show error
                showAlert(`Error: ${data.error || 'Failed to generate speech'}`, 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Failed to connect to the server. Please try again.', 'danger');
        } finally {
            // Hide loading overlay
            loadingOverlay.classList.add('d-none');
        }
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
});
