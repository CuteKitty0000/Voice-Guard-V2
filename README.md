# VoiceGuard Engine - Smart India Hackathon 2026 🏆

**Team Name:** MicroStar  
**Project:** Real-Time Deepfake Audio Detection System  

## 🌟 Overview
VoiceGuard Engine is an advanced, hyper-dense cybersecurity tool designed to detect AI-generated voice synthesis and audio deepfakes in real-time. Built for the **Smart India Hackathon 2026**, it features live microphone stream processing and advanced telemetry extraction.

## ✨ Key Features
- **Live Real-Time Detection:** Stream microphone input and analyze it chunk-by-chunk for AI synthesis.
- **Batch Data Ingestion:** Upload multiple audio files (`.wav`, `.flac`, `.m4a`, `.mp3`) for automated batch processing.
- **Advanced Telemetry:** Extracts crucial acoustic features in real-time including RMS Energy, Spectral Centroid, Spectral Spread, Silence Ratio, and MFCCs.
- **Live Visualizers:** Renders downsampled waveforms and Mel Spectrograms (Inferno) directly in the browser via HTML5 Canvas.

## 🚀 Technology Stack
- **Backend:** Python, Flask, Flask-SocketIO
- **Audio Processing:** Librosa, NumPy, FFmpeg
- **Machine Learning:** ONNX Runtime / Keras
- **Frontend:** HTML5, Vanilla JavaScript, CSS3, Socket.io, Lucide Icons

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CuteKitty0000/Voice-Guard-V2.git
   cd Voice-Guard-V2
   ```

2. **Install dependencies:**
   Make sure you have Python 3.9+ installed. You also need to install **FFmpeg** on your system and add it to your system PATH.
   ```bash
   pip install flask flask-socketio numpy librosa onnxruntime
   ```

3. **Model Setup:**
   Ensure the necessary trained model file is present in the `model/` directory (e.g., `dhwani_model_fast.onnx`).

4. **Run the Application:**
   ```bash
   python app.py
   ```
   The dashboard will be automatically available at `http://localhost:5000`.

## 📸 Dashboard Interface
The application features a dark, cyber-security-themed interface designed for dense information tracking:
- **Stream Tab:** Real-time gauges for Human/Synthesis probability, AI Copilot logs, and live streaming spectral visualizers.
- **Batch Tab:** Drag-and-drop file ingestion and individual probability tracks.

## 🤝 Team MicroStar
- Navaneetha krishnan 
- RAKSHITA
- PREETHIKA 
- NANDESH
- SHIFANI 
- Santhiya

---
*Built with ❤️ for Smart India Hackathon 2026*
