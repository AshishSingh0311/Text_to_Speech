/* Sound Wave Playground JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const waveformElement = document.getElementById('waveform');
    const audioPlayer = document.getElementById('audio-player');
    const playButton = document.getElementById('play-btn');
    const stopButton = document.getElementById('stop-btn');
    const applyChangesButton = document.getElementById('apply-changes-btn');
    const resetButton = document.getElementById('reset-btn');
    const audioHistoryList = document.getElementById('audio-history');
    
    // Slider controls
    const speedSlider = document.getElementById('speed-slider');
    const pitchSlider = document.getElementById('pitch-slider');
    const volumeSlider = document.getElementById('volume-slider');
    const eqBassSlider = document.getElementById('eq-bass-slider');
    const eqMidSlider = document.getElementById('eq-mid-slider');
    const eqTrebleSlider = document.getElementById('eq-treble-slider');
    const effectIntensitySlider = document.getElementById('effect-intensity-slider');
    
    // Value displays
    const speedValue = document.getElementById('speed-value');
    const pitchValue = document.getElementById('pitch-value');
    const volumeValue = document.getElementById('volume-value');
    const eqBassValue = document.getElementById('eq-bass-value');
    const eqMidValue = document.getElementById('eq-mid-value');
    const eqTrebleValue = document.getElementById('eq-treble-value');
    const effectIntensityValue = document.getElementById('effect-intensity-value');
    
    // Effect buttons
    const effectButtons = document.querySelectorAll('[data-effect-type]');
    
    // Preset buttons
    const presetButtons = document.querySelectorAll('.preset-btn');
    const emotionPresets = document.querySelectorAll('.emotion-preset');
    
    // SVG elements for wave visualization
    const svgNS = "http://www.w3.org/2000/svg";
    
    // Audio visualizer
    const visualizerBars = document.querySelector('.visualizer-bars');
    const bars = [];
    
    // Current audio state
    let currentAudioPath = null;
    let currentEffect = 'none';
    let audioHistoryItems = [];
    let isPlaying = false;
    let wavePoints = [];
    let currentWavePath = null;
    let draggingPoint = null;
    
    // Constants
    const DEFAULT_SAMPLE_COUNT = 40;
    const DEFAULT_WAVE_COLOR = '#0d6efd';
    const VISUALIZER_BAR_COUNT = 32;
    
    // Initialize the audio visualizer
    function initializeVisualizer() {
        if (!visualizerBars) return;
        
        // Clear existing bars
        visualizerBars.innerHTML = '';
        
        // Create visualizer bars
        for (let i = 0; i < VISUALIZER_BAR_COUNT; i++) {
            const bar = document.createElement('div');
            bar.className = 'visualizer-bar';
            visualizerBars.appendChild(bar);
            bars.push(bar);
        }
    }
    
    // Create the initial waveform
    function initializeWaveform() {
        if (!waveformElement) return;
        
        // Clear any existing SVG
        waveformElement.innerHTML = '';
        
        // Create SVG element
        const svg = document.createElementNS(svgNS, "svg");
        svg.setAttribute("width", "100%");
        svg.setAttribute("height", "100%");
        svg.setAttribute("viewBox", "0 0 1000 200");
        svg.setAttribute("preserveAspectRatio", "none");
        waveformElement.appendChild(svg);
        
        // Create a background path for the wave
        const pathBg = document.createElementNS(svgNS, "path");
        pathBg.setAttribute("class", "wave-path-bg");
        pathBg.setAttribute("stroke", "#0d6efd33");
        svg.appendChild(pathBg);
        
        // Create the main wave path
        const path = document.createElementNS(svgNS, "path");
        path.setAttribute("class", "wave-path");
        path.setAttribute("stroke", DEFAULT_WAVE_COLOR);
        svg.appendChild(path);
        currentWavePath = path;
        
        // Generate initial wave points
        generateRandomWave();
        
        // Add interactive points
        addDraggablePoints(svg);
        
        // Initially update the SVG path from points
        updateWavePath();
    }
    
    // Generate a random wave shape
    function generateRandomWave() {
        wavePoints = [];
        const width = 1000;
        const segmentWidth = width / (DEFAULT_SAMPLE_COUNT - 1);
        
        for (let i = 0; i < DEFAULT_SAMPLE_COUNT; i++) {
            const x = i * segmentWidth;
            let y = 100; // Center position
            
            // Add some randomness to the y-position
            if (i > 0 && i < DEFAULT_SAMPLE_COUNT - 1) {
                y += (Math.random() * 60) - 30;
            }
            
            wavePoints.push({ x, y });
        }
    }
    
    // Add draggable points to the wave
    function addDraggablePoints(svg) {
        // Remove any existing points
        const existingPoints = svg.querySelectorAll(".wave-point");
        existingPoints.forEach(point => point.remove());
        
        // Add points at each control point
        wavePoints.forEach((point, index) => {
            const circleElement = document.createElementNS(svgNS, "circle");
            circleElement.setAttribute("cx", point.x);
            circleElement.setAttribute("cy", point.y);
            circleElement.setAttribute("r", 4);
            circleElement.setAttribute("class", "wave-point");
            circleElement.setAttribute("data-index", index);
            svg.appendChild(circleElement);
            
            // Add drag event listeners
            circleElement.addEventListener("mousedown", startDragging);
            circleElement.addEventListener("touchstart", startDragging, { passive: true });
        });
    }
    
    // Update the SVG path based on the current points
    function updateWavePath() {
        if (!currentWavePath) return;
        
        // Create path string
        let pathStr = "";
        wavePoints.forEach((point, i) => {
            if (i === 0) {
                pathStr += `M ${point.x} ${point.y}`;
            } else {
                // Use a smooth curve
                const prevPoint = wavePoints[i - 1];
                const cpx1 = prevPoint.x + (point.x - prevPoint.x) / 4;
                const cpy1 = prevPoint.y;
                const cpx2 = point.x - (point.x - prevPoint.x) / 4;
                const cpy2 = point.y;
                
                pathStr += ` C ${cpx1} ${cpy1}, ${cpx2} ${cpy2}, ${point.x} ${point.y}`;
            }
        });
        
        // Update both the foreground and background paths
        currentWavePath.setAttribute("d", pathStr);
        
        const pathBg = waveformElement.querySelector(".wave-path-bg");
        if (pathBg) {
            pathBg.setAttribute("d", pathStr);
        }
        
        // Update the positions of the draggable points
        wavePoints.forEach((point, index) => {
            const pointElement = waveformElement.querySelector(`.wave-point[data-index="${index}"]`);
            if (pointElement) {
                pointElement.setAttribute("cx", point.x);
                pointElement.setAttribute("cy", point.y);
            }
        });
    }
    
    // Handle starting to drag a point
    function startDragging(event) {
        event.preventDefault();
        
        const point = event.target;
        point.classList.add("active");
        draggingPoint = {
            element: point,
            index: parseInt(point.getAttribute("data-index"))
        };
        
        // Add move and end listeners to the document
        document.addEventListener("mousemove", movePoint);
        document.addEventListener("touchmove", movePoint, { passive: false });
        document.addEventListener("mouseup", stopDragging);
        document.addEventListener("touchend", stopDragging);
    }
    
    // Handle moving a point during drag
    function movePoint(event) {
        if (!draggingPoint) return;
        
        event.preventDefault();
        
        // Get the SVG coordinates
        const svg = waveformElement.querySelector("svg");
        const svgRect = svg.getBoundingClientRect();
        
        // Get the event position
        const clientX = event.type.includes("touch") ? 
            event.touches[0].clientX : event.clientX;
        const clientY = event.type.includes("touch") ? 
            event.touches[0].clientY : event.clientY;
            
        // Convert to SVG coordinates
        const svgX = ((clientX - svgRect.left) / svgRect.width) * 1000;
        let svgY = ((clientY - svgRect.top) / svgRect.height) * 200;
        
        // Constrain y value to be within the SVG
        svgY = Math.max(10, Math.min(190, svgY));
        
        // Update the point position (only Y can be changed)
        const pointIndex = draggingPoint.index;
        wavePoints[pointIndex].y = svgY;
        
        // Update the wave path
        updateWavePath();
        
        // Preview the change in real-time by updating visualizer
        updateVisualizerFromWave();
    }
    
    // Handle stopping dragging a point
    function stopDragging() {
        if (!draggingPoint) return;
        
        draggingPoint.element.classList.remove("active");
        draggingPoint = null;
        
        // Remove the event listeners
        document.removeEventListener("mousemove", movePoint);
        document.removeEventListener("touchmove", movePoint);
        document.removeEventListener("mouseup", stopDragging);
        document.removeEventListener("touchend", stopDragging);
    }
    
    // Play/pause the audio
    function togglePlay() {
        if (audioPlayer.paused) {
            audioPlayer.play();
            playButton.innerHTML = '<i class="bi bi-pause-fill"></i> Pause';
            startVisualization();
        } else {
            audioPlayer.pause();
            playButton.innerHTML = '<i class="bi bi-play-fill"></i> Play';
            stopVisualization();
        }
    }
    
    // Stop the audio
    function stopAudio() {
        audioPlayer.pause();
        audioPlayer.currentTime = 0;
        playButton.innerHTML = '<i class="bi bi-play-fill"></i> Play';
        stopVisualization();
    }
    
    // Apply the current settings to the audio
    function applyChanges() {
        if (!currentAudioPath) {
            showAlert("No audio file selected. Please generate speech first.", "warning");
            return;
        }
        
        // Get the current settings
        const settings = {
            audio_path: currentAudioPath,
            speed: parseFloat(speedSlider.value),
            pitch: parseInt(pitchSlider.value),
            volume: parseInt(volumeSlider.value),
            eq_bass: parseFloat(eqBassSlider.value),
            eq_mid: parseFloat(eqMidSlider.value),
            eq_treble: parseFloat(eqTrebleSlider.value),
            effect_type: currentEffect,
            effect_intensity: parseFloat(effectIntensitySlider.value)
        };
        
        // Show loading indicator
        showAlert("Processing audio...", "info");
        
        // Make API request
        fetch('/api/manipulate-audio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update audio player
                const previousTime = audioPlayer.currentTime;
                const wasPlaying = !audioPlayer.paused;
                
                // Store in history
                addToHistory(data.path, settings);
                
                // Update audio player
                audioPlayer.src = data.path;
                currentAudioPath = data.path;
                
                // If it was playing, continue playback
                if (wasPlaying) {
                    audioPlayer.currentTime = previousTime;
                    audioPlayer.play();
                }
                
                showAlert("Audio processed successfully!", "success");
            } else {
                showAlert("Error: " + data.error, "danger");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert("Failed to process audio. Please try again.", "danger");
        });
    }
    
    // Reset all settings to default
    function resetSettings() {
        speedSlider.value = 1.0;
        pitchSlider.value = 0;
        volumeSlider.value = 0;
        eqBassSlider.value = 0;
        eqMidSlider.value = 0;
        eqTrebleSlider.value = 0;
        effectIntensitySlider.value = 0.5;
        
        // Update displays
        updateValueDisplays();
        
        // Reset effect buttons
        effectButtons.forEach(button => {
            button.classList.remove('active');
        });
        
        // Reset current effect
        currentEffect = 'none';
        const noneButton = document.querySelector('[data-effect-type="none"]');
        if (noneButton) {
            noneButton.classList.add('active');
        }
        
        // Reset wave
        generateRandomWave();
        updateWavePath();
        
        showAlert("Settings reset to default.", "info");
    }
    
    // Add an item to the audio history
    function addToHistory(audioPath, settings) {
        // Create a timestamp
        const now = new Date();
        const timestamp = now.toLocaleTimeString();
        
        // Create a history item
        const historyItem = {
            path: audioPath,
            timestamp: timestamp,
            settings: settings
        };
        
        // Add to the history array
        audioHistoryItems.unshift(historyItem);
        
        // Keep only the last 5 items
        if (audioHistoryItems.length > 5) {
            audioHistoryItems.pop();
        }
        
        // Update the UI
        updateHistoryUI();
    }
    
    // Update the history list in the UI
    function updateHistoryUI() {
        if (!audioHistoryList) return;
        
        // Clear the list
        audioHistoryList.innerHTML = '';
        
        // Add items
        audioHistoryItems.forEach((item, index) => {
            const listItem = document.createElement('div');
            listItem.className = 'audio-history-item';
            listItem.innerHTML = `
                <div class="me-2">
                    <button class="btn btn-sm btn-outline-primary play-history" data-index="${index}">
                        <i class="bi bi-play-fill"></i>
                    </button>
                </div>
                <div>
                    <div>Version ${audioHistoryItems.length - index}</div>
                    <small class="text-muted">Speed: ${item.settings.speed}x, Pitch: ${item.settings.pitch}</small>
                </div>
                <div class="history-timestamp">${item.timestamp}</div>
            `;
            audioHistoryList.appendChild(listItem);
        });
        
        // Add event listeners
        const playButtons = document.querySelectorAll('.play-history');
        playButtons.forEach(button => {
            button.addEventListener('click', () => {
                const index = parseInt(button.getAttribute('data-index'));
                const item = audioHistoryItems[index];
                
                // Load and play the audio
                audioPlayer.src = item.path;
                currentAudioPath = item.path;
                audioPlayer.play();
                playButton.innerHTML = '<i class="bi bi-pause-fill"></i> Pause';
                
                // Update settings
                updateSettingsFromHistory(item.settings);
            });
        });
    }
    
    // Update the settings based on a history item
    function updateSettingsFromHistory(settings) {
        // Update sliders
        speedSlider.value = settings.speed;
        pitchSlider.value = settings.pitch;
        volumeSlider.value = settings.volume;
        eqBassSlider.value = settings.eq_bass;
        eqMidSlider.value = settings.eq_mid;
        eqTrebleSlider.value = settings.eq_treble;
        effectIntensitySlider.value = settings.effect_intensity;
        
        // Update effect buttons
        effectButtons.forEach(button => {
            button.classList.remove('active');
            if (button.getAttribute('data-effect-type') === settings.effect_type) {
                button.classList.add('active');
            }
        });
        
        // Update current effect
        currentEffect = settings.effect_type;
        
        // Update displays
        updateValueDisplays();
    }
    
    // Update slider value displays
    function updateValueDisplays() {
        if (speedValue) speedValue.textContent = speedSlider.value + 'x';
        if (pitchValue) {
            const sign = pitchSlider.value >= 0 ? '+' : '';
            pitchValue.textContent = sign + pitchSlider.value;
        }
        if (volumeValue) {
            const sign = volumeSlider.value >= 0 ? '+' : '';
            volumeValue.textContent = sign + volumeSlider.value + ' dB';
        }
        if (eqBassValue) {
            const sign = eqBassSlider.value >= 0 ? '+' : '';
            eqBassValue.textContent = sign + eqBassSlider.value + ' dB';
        }
        if (eqMidValue) {
            const sign = eqMidSlider.value >= 0 ? '+' : '';
            eqMidValue.textContent = sign + eqMidSlider.value + ' dB';
        }
        if (eqTrebleValue) {
            const sign = eqTrebleSlider.value >= 0 ? '+' : '';
            eqTrebleValue.textContent = sign + eqTrebleSlider.value + ' dB';
        }
        if (effectIntensityValue) effectIntensityValue.textContent = Math.round(effectIntensitySlider.value * 100) + '%';
    }
    
    // Set a preset configuration
    function applyPreset(presetName) {
        switch(presetName) {
            case 'chipmunk':
                speedSlider.value = 1.5;
                pitchSlider.value = 7;
                eqTrebleSlider.value = 3;
                break;
                
            case 'giant':
                speedSlider.value = 0.7;
                pitchSlider.value = -6;
                eqBassSlider.value = 3;
                break;
                
            case 'robot':
                speedSlider.value = 1.1;
                pitchSlider.value = 0;
                currentEffect = 'distortion';
                effectIntensitySlider.value = 0.8;
                break;
                
            case 'cathedral':
                speedSlider.value = 0.9;
                currentEffect = 'reverb';
                effectIntensitySlider.value = 0.7;
                break;
                
            case 'telephone':
                eqBassSlider.value = -5;
                eqTrebleSlider.value = -3;
                eqMidSlider.value = 4;
                break;
                
            case 'megaphone':
                eqMidSlider.value = 5;
                eqBassSlider.value = -4;
                eqTrebleSlider.value = -2;
                volumeSlider.value = 3;
                break;
        }
        
        // Update displays
        updateValueDisplays();
        
        // Update effect buttons
        effectButtons.forEach(button => {
            button.classList.remove('active');
            if (button.getAttribute('data-effect-type') === currentEffect) {
                button.classList.add('active');
            }
        });
        
        showAlert(`Applied "${presetName}" preset`, "info");
    }
    
    // Apply an emotion preset
    function applyEmotionPreset(emotion, parameters) {
        // Update emotion preset buttons
        emotionPresets.forEach(preset => {
            preset.classList.remove('active');
            if (preset.getAttribute('data-emotion') === emotion) {
                preset.classList.add('active');
            }
        });
        
        // Set the wave color
        if (parameters.color && currentWavePath) {
            currentWavePath.setAttribute("stroke", parameters.color);
            
            // Also update the background path with a transparent version
            const pathBg = waveformElement.querySelector(".wave-path-bg");
            if (pathBg) {
                // Convert hex to rgba with 0.2 opacity
                let rgba = hexToRgba(parameters.color, 0.2);
                pathBg.setAttribute("stroke", rgba);
            }
        }
        
        // Apply the parameters
        speedSlider.value = parameters.speed;
        pitchSlider.value = parameters.pitch;
        volumeSlider.value = parameters.volume;
        
        // Emotion-specific EQ settings
        switch(emotion) {
            case 'happy':
                eqBassSlider.value = 1;
                eqMidSlider.value = 1;
                eqTrebleSlider.value = 3;
                break;
                
            case 'sad':
                eqBassSlider.value = 2;
                eqMidSlider.value = -1;
                eqTrebleSlider.value = -2;
                break;
                
            case 'angry':
                eqBassSlider.value = -1;
                eqMidSlider.value = 2;
                eqTrebleSlider.value = 4;
                break;
                
            case 'excited':
                eqBassSlider.value = 1;
                eqMidSlider.value = 2;
                eqTrebleSlider.value = 3;
                break;
                
            case 'calm':
                eqBassSlider.value = 2;
                eqMidSlider.value = 0;
                eqTrebleSlider.value = -1;
                break;
                
            case 'fearful':
                eqBassSlider.value = -2;
                eqMidSlider.value = 0;
                eqTrebleSlider.value = 3;
                break;
                
            case 'whisper':
                eqBassSlider.value = -2;
                eqMidSlider.value = -1;
                eqTrebleSlider.value = 4;
                break;
                
            case 'shouting':
                eqBassSlider.value = 2;
                eqMidSlider.value = 3;
                eqTrebleSlider.value = 3;
                break;
                
            default:
                eqBassSlider.value = 0;
                eqMidSlider.value = 0;
                eqTrebleSlider.value = 0;
        }
        
        // Update displays
        updateValueDisplays();
        
        // Apply a suitable audio effect
        switch(emotion) {
            case 'calm':
            case 'sad':
                currentEffect = 'reverb';
                effectIntensitySlider.value = 0.3;
                break;
                
            case 'angry':
            case 'shouting':
                currentEffect = 'distortion';
                effectIntensitySlider.value = 0.3;
                break;
                
            case 'whisper':
                currentEffect = 'reverb';
                effectIntensitySlider.value = 0.5;
                break;
                
            case 'fearful':
                currentEffect = 'chorus';
                effectIntensitySlider.value = 0.3;
                break;
                
            default:
                currentEffect = 'none';
                effectIntensitySlider.value = 0.5;
        }
        
        // Update effect buttons
        effectButtons.forEach(button => {
            button.classList.remove('active');
            if (button.getAttribute('data-effect-type') === currentEffect) {
                button.classList.add('active');
            }
        });
        
        // Generate a wave pattern that matches the emotion
        generateEmotionWave(emotion, parameters);
        
        showAlert(`Applied "${emotion}" emotion preset`, "info");
    }
    
    // Generate a wave pattern based on an emotion
    function generateEmotionWave(emotion, parameters) {
        const variability = parameters.variability || 0;
        const emphasis = parameters.emphasis || 0;
        
        wavePoints = [];
        const width = 1000;
        const segmentWidth = width / (DEFAULT_SAMPLE_COUNT - 1);
        
        for (let i = 0; i < DEFAULT_SAMPLE_COUNT; i++) {
            const x = i * segmentWidth;
            let y = 100; // Center position
            
            if (i > 0 && i < DEFAULT_SAMPLE_COUNT - 1) {
                // Add variability based on emotion
                if (emotion === 'happy' || emotion === 'excited') {
                    // More energetic, higher frequency waves
                    y += Math.sin(i * 0.5) * 30 * (1 + variability/2);
                } else if (emotion === 'sad' || emotion === 'calm') {
                    // Smoother, low frequency waves
                    y += Math.sin(i * 0.2) * 20 * (1 - variability/2);
                } else if (emotion === 'angry' || emotion === 'shouting') {
                    // Jagged waves with sharp peaks
                    y += (Math.sin(i * 0.4) * 25 + (Math.random() * 10)) * (1 + emphasis/2);
                } else if (emotion === 'fearful') {
                    // Trembling effect
                    y += Math.sin(i * 0.3) * 15 + Math.sin(i * 2) * 10 * variability;
                } else if (emotion === 'whisper') {
                    // Low amplitude, gentle waves
                    y += Math.sin(i * 0.3) * 10 * (1 - emphasis/2);
                } else {
                    // Neutral - slight randomness
                    y += (Math.random() * 30) - 15;
                }
            }
            
            wavePoints.push({ x, y });
        }
        
        // Update the SVG
        updateWavePath();
        addDraggablePoints(waveformElement.querySelector("svg"));
    }
    
    // Start audio visualization
    function startVisualization() {
        isPlaying = true;
        updateVisualizerFromWave();
    }
    
    // Stop audio visualization
    function stopVisualization() {
        isPlaying = false;
    }
    
    // Update the audio visualizer from the current wave
    function updateVisualizerFromWave() {
        if (!isPlaying || !visualizerBars || bars.length === 0) return;
        
        // Sample the wave points to update visualizer
        const sampleCount = wavePoints.length;
        const barCount = bars.length;
        
        for (let i = 0; i < barCount; i++) {
            // Find the corresponding wave point
            const waveIndex = Math.floor((i / barCount) * sampleCount);
            const wavePoint = wavePoints[waveIndex];
            
            // Convert y position (0-200) to bar height (0-100%)
            // Invert because SVG y is top-down but we want bar height bottom-up
            const normalizedHeight = (200 - wavePoint.y) / 2;
            
            // Set the bar height
            bars[i].style.height = `${normalizedHeight}%`;
        }
        
        // Continue animation if still playing
        if (isPlaying) {
            requestAnimationFrame(updateVisualizerFromWave);
        }
    }
    
    // Helper function to convert hex color to rgba
    function hexToRgba(hex, alpha = 1) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    // Display alert messages
    function showAlert(message, type = 'info', duration = 3000) {
        const alertContainer = document.getElementById('alert-container');
        if (!alertContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.innerHTML = '';
        alertContainer.appendChild(alert);
        
        if (duration > 0) {
            setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => {
                    if (alert.parentElement) {
                        alertContainer.removeChild(alert);
                    }
                }, 300);
            }, duration);
        }
    }
    
    // Event Listeners
    
    // Audio player controls
    if (playButton) {
        playButton.addEventListener('click', togglePlay);
    }
    
    if (stopButton) {
        stopButton.addEventListener('click', stopAudio);
    }
    
    if (applyChangesButton) {
        applyChangesButton.addEventListener('click', applyChanges);
    }
    
    if (resetButton) {
        resetButton.addEventListener('click', resetSettings);
    }
    
    // Slider events
    const sliders = [speedSlider, pitchSlider, volumeSlider, eqBassSlider, eqMidSlider, eqTrebleSlider, effectIntensitySlider];
    sliders.forEach(slider => {
        if (slider) {
            slider.addEventListener('input', updateValueDisplays);
        }
    });
    
    // Effect button events
    effectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const effectType = this.getAttribute('data-effect-type');
            currentEffect = effectType;
            
            // Update UI
            effectButtons.forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            showAlert(`Selected "${effectType}" effect`, "info");
        });
    });
    
    // Preset button events
    presetButtons.forEach(button => {
        button.addEventListener('click', function() {
            const presetName = this.getAttribute('data-preset');
            applyPreset(presetName);
        });
    });
    
    // Emotion preset events
    emotionPresets.forEach(preset => {
        preset.addEventListener('click', function() {
            const emotion = this.getAttribute('data-emotion');
            
            // Get parameters from data attributes
            const parameters = {
                speed: parseFloat(this.getAttribute('data-speed') || 1.0),
                pitch: parseInt(this.getAttribute('data-pitch') || 0),
                volume: parseInt(this.getAttribute('data-volume') || 0),
                emphasis: parseInt(this.getAttribute('data-emphasis') || 0),
                variability: parseFloat(this.getAttribute('data-variability') || 0),
                color: this.getAttribute('data-color') || DEFAULT_WAVE_COLOR
            };
            
            applyEmotionPreset(emotion, parameters);
        });
    });
    
    // Audio player events
    if (audioPlayer) {
        audioPlayer.addEventListener('play', function() {
            isPlaying = true;
            playButton.innerHTML = '<i class="bi bi-pause-fill"></i> Pause';
            startVisualization();
        });
        
        audioPlayer.addEventListener('pause', function() {
            isPlaying = false;
            playButton.innerHTML = '<i class="bi bi-play-fill"></i> Play';
            stopVisualization();
        });
        
        audioPlayer.addEventListener('ended', function() {
            isPlaying = false;
            playButton.innerHTML = '<i class="bi bi-play-fill"></i> Play';
            stopVisualization();
        });
    }
    
    // Main initialization
    function init() {
        // Initialize slider displays
        updateValueDisplays();
        
        // Initialize visualizer
        initializeVisualizer();
        
        // Initialize waveform
        initializeWaveform();
        
        // Set default audio path from query parameter if available
        const urlParams = new URLSearchParams(window.location.search);
        const audioPath = urlParams.get('audio');
        if (audioPath) {
            currentAudioPath = audioPath;
            audioPlayer.src = audioPath;
            
            showAlert("Audio loaded. Use the controls to modify and play.", "info");
        }
    }
    
    // Run initialization
    init();
});