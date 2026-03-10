# 🎵 Python Audio Visualizer Suite

A robust, multi-tool audio visualization suite built in Python. This project features a central UI Hub that allows users to launch real-time microphone visualizers, or process pre-recorded audio files and automatically export them as high-quality `.mp4` videos.

## ✨ Features

### 🎤 Live Microphone Tools
Real-time audio processing using your system's default microphone. Features include noise gating to ignore background static.
* **Main Visualizer (Pitch):** Circular waveform with real-time true-pitch note detection.
* **Spectrogram:** A scrolling waterfall display of audio frequencies.
* **Color / Average Frequency:** Bar graphs mapping frequencies to a dynamic color space.
* **Waveform:** Classic oscilloscope-style waveform display.

### 📁 File Tools & Video Export
Select an `.mp3`, `.wav`, or `.ogg` file to generate a visualizer perfectly synced to the track. 
* **Audio Playback Controller:** A custom streaming-style dashboard to scrub through the track.
* **Auto-Export to MP4:** When a file visualizer finishes, it automatically captures the frames and uses a bundled FFmpeg library to mux the audio and video together into a ready-to-share `.mp4` file.
* Includes both Pitch-detecting (FFT) and Raw Waveform (Amplitude) visualizers in Circular and Bar Graph formats.

## 🚀 Installation & Setup

This project requires Python 3 to be installed on your system. It relies on several external libraries like `pygame`, `numpy`, `opencv-python`, and `librosa`. 

1. **Clone or Download** this repository to your local machine.
2. Open your terminal or command prompt, navigate to the project folder, and run the following command to install all necessary dependencies automatically:

```bash
pip install -r requirements.txt