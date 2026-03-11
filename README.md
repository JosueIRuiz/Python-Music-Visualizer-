# 🎵 Python Audio Visualizer Suite

A robust, multi-tool audio visualization suite built in Python. This project features a central UI Hub that allows users to launch real-time microphone visualizers, or process pre-recorded audio files and automatically export them as high-quality `.mp4` videos.

## ✨ Features

* **🎛️ Central UI Hub:** A sleek, dark-themed control panel to manage all visualizers, select files, and tweak settings.
* **🎨 Universal Theme Engine:** Apply vibrant color palettes to any visualizer. Choose from *Rainbow, Ocean, Fire, Matrix, Sunset, Cyberpunk, Forest,* or *Monochrome*. Includes a built-in **Style Gallery** with live previews.
* **📹 Auto-Export to MP4:** File-based visualizers automatically capture their frames and use a bundled FFmpeg library to mux the high-quality audio and video together. No manual FFmpeg installation required!
* **👻 Background Rendering:** Need a video fast? Check "Run in Background" to process the visualizer silently without opening a window, outputting directly to an MP4.
* **🔇 Live Mute Toggle:** Press `M` to toggle the audio on or off while a file visualizer is running.
* **🎚️ Playback Controller:** A custom streaming-style dashboard to scrub through tracks and adjust volume.

## 📂 Project Structure

To keep things organized, the project is split into dedicated directories:
* `hub.py` - The main application file. Run this to start the suite!
* `live_visualizers/` - Contains scripts that use your system's microphone for real-time audio reactivity. Includes noise-gating to prevent static bouncing.
* `file_visualizers/` - Contains scripts that read `.mp3`, `.wav`, or `.ogg` files, perfectly sync them to the visuals, and export the results.
* `video_output/` - The destination folder where all your finished `.mp4` videos are automatically saved.

## 👁️ Visualizer Styles

1. **Circular Visualizer:** A 360-degree ring of frequencies that pulses outward. Available with or without real-time Pitch/Note detection text.
2. **Bar Graph:** A classic horizontal spectrum analyzer. Best for detailed frequency tracking. Available with or without Pitch detection.
3. **Classic Waveform:** A sweeping oscilloscope line showing the raw audio pulse.
4. **Spectrogram (Live Only):** A scrolling waterfall chart showing the history of audio frequencies.

## 🚀 Installation & Setup

This project requires Python 3. It relies on several external libraries like `pygame`, `numpy`, `opencv-python`, `librosa`, and `pyaudio`.

1. **Clone or Download** this repository to your local machine.
2. Open your terminal or command prompt, navigate to the project folder, and run the following command to install all necessary dependencies automatically:

```bash
pip install -r requirements.txt

