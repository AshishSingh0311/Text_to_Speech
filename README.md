# Neural Text-to-Speech with Sound Playground

A sophisticated multilingual text-to-speech web application that transforms text into expressive, dynamically generated audio with advanced emotion modulation and interactive visualizations.

## Features

### Text-to-Speech Engine
- **Multilingual Support**: 13 languages including English and Indian regional languages (Hindi, Bengali, Tamil, Telugu, Malayalam, etc.)
- **Voice Variety**: 6 different voice types (Default, Male, Female, Child, Elderly, Robot)
- **Emotion Modulation**: 9 different emotions with custom audio profiles (Neutral, Happy, Sad, Angry, Excited, Calm, Fearful, Whisper, Shouting)
- **Audio Effects**: Apply echo, reverb, chorus, and distortion effects

### Advanced Audio Customization
- **Pitch Control**: Adjust voice pitch from -10 to +10 semitones
- **Speed Control**: Modify speech rate from 0.5x to 2.0x
- **Volume Adjustment**: Fine-tune output volume
- **EQ Controls**: Three-band equalizer for bass, mid, and treble frequencies

### Interactive Sound Playground
- **Waveform Visualization**: Real-time interactive waveform display
- **Drag-and-Drop Control Points**: Reshape audio waveforms by dragging control points
- **Live Preview**: Visualize changes before applying them
- **Preset Library**: Quick transformations with voice presets (Chipmunk, Giant, Robot, Cathedral, etc.)
- **Emotion-Based Presets**: Apply emotion-specific audio profiles with matching waveform patterns
- **Audio History**: Keep track of modifications with playback of previous versions

## Technology Stack

- **Backend**: Python with Flask framework
- **Text-to-Speech**: Google Text-to-Speech (gTTS)
- **Audio Processing**: PyDub for advanced audio manipulation
- **Frontend**: JavaScript, Bootstrap 5 with Replit dark theme
- **Audio Visualization**: Custom SVG-based waveform visualization

## Getting Started

### Installation

1. Clone the repository
2. Install the required dependencies:
```
pip install -r requirements.txt
```

### Running the Application

```
python main.py
```
The application will be available at http://localhost:5000

## Usage

### Text-to-Speech
1. Enter your text (up to 400 words)
2. Select language, voice type, and emotion
3. Adjust advanced parameters if needed (speed, pitch, volume)
4. Click "Generate Neural Speech"
5. Play, download, or further manipulate the generated audio

### Sound Playground
1. Generate speech from the main page or use existing audio
2. Navigate to the Sound Playground
3. Manipulate the waveform by dragging control points
4. Adjust audio parameters using sliders
5. Apply presets for quick transformations
6. Click "Apply Changes" to process the modified audio
7. Compare different versions in the audio history

## API Endpoints

The application provides several API endpoints:

- `/api/tts`: Generate speech from text
- `/api/languages`: Get supported languages
- `/api/emotions`: Get supported emotions and parameters
- `/api/voice-types`: Get supported voice types
- `/api/audio-effects`: Get supported audio effects
- `/api/manipulate-audio`: Process existing audio with new parameters

## License

This project is open source and available for non-commercial use.

## Acknowledgments

- [gTTS](https://github.com/gtts/gtts) for text-to-speech conversion
- [PyDub](https://github.com/jiaaro/pydub) for audio processing capabilities