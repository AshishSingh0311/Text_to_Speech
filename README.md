Neural Text-to-Speech with Sound Playground
A sophisticated multilingual text-to-speech (TTS) web application that transforms written text into expressive, dynamically generated audio. Featuring advanced emotion modulation, voice customization, and interactive visualizations, this platform offers a powerful and creative sound manipulation experience.

🔊 Features
🎤 Text-to-Speech Engine
Multilingual Support: Supports 13 languages, including English and major Indian languages (Hindi, Bengali, Tamil, Telugu, Malayalam, and more).

Voice Variety: Choose from 6 unique voice types:

Default

Male

Female

Child

Elderly

Robot

Emotion Modulation: Choose from 9 different emotional tones with custom audio profiles:

Neutral

Happy

Sad

Angry

Excited

Calm

Fearful

Whisper

Shouting

Audio Effects: Apply professional sound effects including:

Echo

Reverb

Chorus

Distortion

🎚️ Advanced Audio Customization
Pitch Control: Adjust pitch from -10 to +10 semitones.

Speed Control: Modify speech rate from 0.5x to 2.0x.

Volume Adjustment: Fine-tune the audio output level.

EQ Controls: Three-band equalizer to adjust bass, midrange, and treble frequencies.

🧩 Interactive Sound Playground
Waveform Visualization: Real-time, interactive waveform display.

Drag-and-Drop Control Points: Directly reshape the waveform by dragging control points.

Live Preview: Preview audio changes in real-time before applying.

Preset Library: Instantly transform audio with presets like:

Chipmunk

Giant

Robot

Cathedral

Emotion-Based Presets: Match waveform patterns with emotional profiles.

Audio History: Track and replay previous versions of the audio with a built-in history log.

🛠️ Technology Stack
Backend: Python with Flask framework

Text-to-Speech Engine: Google Text-to-Speech (gTTS)

Audio Processing: PyDub for real-time audio manipulation

Frontend: JavaScript with Bootstrap 5 (Replit dark theme)

Audio Visualization: Custom SVG-based waveform rendering

🚀 Getting Started
📦 Installation
bash
Copy
Edit
git clone <repository_url>
cd <repository_folder>
pip install -r requirements.txt
▶️ Running the Application
bash
Copy
Edit
python main.py
Visit http://localhost:5000 in your browser to start using the application.

📘 Usage Guide
🗣️ Text-to-Speech
Enter your text (up to 400 words).

Select language, voice type, and emotion.

Customize parameters like speed, pitch, and volume.

Click "Generate Neural Speech".

Play, download, or send the audio to the Sound Playground.

🎛️ Sound Playground
Use audio from the TTS module or upload your own.

Drag waveform control points to manipulate the shape.

Adjust pitch, EQ, speed, and effects via sliders.

Apply presets or save your changes.

Compare modified versions using the audio history.

📡 API Endpoints
POST /api/tts: Generate speech from text.

GET /api/languages: Retrieve supported languages.

GET /api/emotions: List available emotions and their parameters.

GET /api/voice-types: List all supported voice types.

GET /api/audio-effects: Get available sound effects.

POST /api/manipulate-audio: Apply changes to existing audio.
