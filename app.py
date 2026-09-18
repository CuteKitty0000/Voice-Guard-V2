import os
import tempfile
import subprocess
import traceback
import warnings
from collections import deque

import numpy as np
import librosa
import onnxruntime as ort

from flask import Flask, render_template, request, jsonify, make_response
from flask.json.provider import DefaultJSONProvider
from flask_socketio import SocketIO, emit

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==============================================================================
# CONFIG & GLOBALS
# ==============================================================================
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "dhwani_model_fast.onnx")
ALLOWED_EXTENSIONS = {".flac", ".wav", ".m4a", ".mp4", ".aac", ".mp3", ".ogg", ".webm"}
N_MELS, MAX_TS = 91, 150
BUFFER_SIZE = 4

# State
session_buffers = {}
voiceprints = {}

# ==============================================================================
# FLASK INIT & CUSTOM JSON PROVIDER
# ==============================================================================
class NumpySafeJSONProvider(DefaultJSONProvider):
    """Ensures any stray numpy types are converted to native Python for JSON."""
    def default(self, obj):
        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app = Flask(__name__)
app.config["SECRET_KEY"] = "voiceguard-secret"
app.json_provider_class = NumpySafeJSONProvider
app.json = NumpySafeJSONProvider(app)
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=20*1024*1024, async_mode="threading")

print("Loading Dhwani ONNX model...", flush=True)
ort_session = ort.InferenceSession(MODEL_PATH)
input_name = ort_session.get_inputs()[0].name
print("Model ready!", flush=True)

# ==============================================================================
# AUDIO & ML PIPELINE
# ==============================================================================
def safe_convert_audio(source_path, target_path):
    """Run FFmpeg safely."""
    cmd = ["ffmpeg", "-y", "-i", source_path, "-ar", "22050", "-ac", "1", target_path]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {res.stderr.decode()}")

def file_to_audio(path, ext):
    """Load audio file safely, converting with FFmpeg if not native to librosa."""
    if ext not in (".wav", ".flac"):
        # Create temp file safely for Windows
        fd, temp_wav = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            safe_convert_audio(path, temp_wav)
            audio, _ = librosa.load(temp_wav, sr=22050)
            return audio
        finally:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
    else:
        audio, _ = librosa.load(path, sr=22050)
        return audio

def extract_features(audio, sr=22050):
    """Extract interpretable audio features."""
    rms = np.sqrt(np.mean(audio**2) + 1e-12)
    silence_ratio = np.mean(np.abs(audio) < 10 ** (-40 / 20))
    spec = np.abs(np.fft.rfft(audio, n=2048)) + 1e-9
    freqs = np.fft.rfftfreq(2048, d=1.0 / sr)
    spec_norm = spec / spec.sum()
    centroid = (freqs * spec_norm).sum()
    spread = np.sqrt(((freqs - centroid) ** 2 * spec_norm).sum())
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)

    return {
        "duration_sec": round(len(audio) / sr, 3),
        "rms_db": round(20 * np.log10(rms), 2),
        "silence_ratio": round(float(silence_ratio), 3),
        "spectral_centroid_hz": round(float(centroid), 1),
        "spectral_spread_hz": round(float(spread), 1),
        "mfcc_mean": [round(float(v), 3) for v in np.mean(mfcc, axis=1)],
        "mfcc_std": [round(float(v), 3) for v in np.std(mfcc, axis=1)],
    }

def get_visualizations(audio):
    """Compute waveform and mel spectrogram for UI."""
    # Waveform (3000 pts max)
    target_pts = 3000
    step = max(1, len(audio) // target_pts)
    waveform = audio[::step][:target_pts].tolist()

    # Mel Spectrogram
    m = librosa.feature.melspectrogram(y=audio, sr=22050, n_mels=64, n_fft=1024, hop_length=256)
    m_db = librosa.power_to_db(m, ref=np.max)
    if m_db.shape[1] < 150:
        m_db = np.pad(m_db, ((0, 0), (0, 150 - m_db.shape[1])), mode="constant", constant_values=-80)
    else:
        m_db = m_db[:, :150]
    mn, mx = m_db.min(), m_db.max()
    m_norm = (m_db - mn) / (mx - mn + 1e-8)

    return {
        "waveform": [float(v) for v in waveform],
        "mel": {
            "data": [float(v) for v in m_norm.flatten()],
            "rows": 64,
            "cols": 150
        }
    }

def analyze_audio(audio, sid=None, include_visuals=False):
    """Core inference pipeline."""
    # 1. Preprocess & Silence Guard
    rms = float(np.sqrt(np.mean(audio**2)))
    rdb = round(20 * np.log10(rms + 1e-9), 1)
    if rms < 0.003:
        return {"error": f"Audio too quiet ({rdb} dB) — check microphone level", "risk_level": "LOW"}

    t, _ = librosa.effects.trim(audio, top_db=25)
    if len(t) < 2048: t = audio
    pk = np.max(np.abs(t))
    if pk > 1e-6: t = t / pk

    # 2. Run ONNX Model
    y_16k = librosa.resample(t, orig_sr=22050, target_sr=16000)
    max_len = 48000
    if len(y_16k) > max_len: y_16k = y_16k[:max_len]
    else: y_16k = np.pad(y_16k, (0, max_len - len(y_16k)), mode='constant')
    y_16k = (y_16k - np.mean(y_16k)) / np.sqrt(np.var(y_16k) + 1e-5)
    y_16k = y_16k.astype(np.float32).reshape(1, max_len)

    logits = ort_session.run(None, {input_name: y_16k})[0]
    probs = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)
    ai_raw = float(probs[0][1]) * 100
    hu_raw = float(probs[0][0]) * 100

    # 3. Rolling Average (Live Mode)
    buf_count = 1
    if sid:
        if sid not in session_buffers:
            session_buffers[sid] = deque(maxlen=BUFFER_SIZE)
        session_buffers[sid].append((ai_raw, hu_raw))
        buf = session_buffers[sid]
        buf_count = len(buf)
        weights = list(range(1, buf_count + 1))
        ai = sum(w * v[0] for w, v in zip(weights, buf)) / sum(weights)
        hu = sum(w * v[1] for w, v in zip(weights, buf)) / sum(weights)
    else:
        ai, hu = ai_raw, hu_raw

    verdict = "AI" if ai > 50 else "Human"
    risk_level = "HIGH" if ai >= 70 else "MEDIUM" if ai >= 45 else "LOW"

    # 4. Construct Result
    result = {
        "ai_pct": round(ai, 1),
        "human_pct": round(hu, 1),
        "verdict": verdict,
        "risk_level": risk_level,
        "rms_db": rdb,
        "buf_count": buf_count,
        "buf_size": BUFFER_SIZE,
        "low_confidence": (max(ai, hu) / 100) < 0.65
    }

    # Extract detailed features & visuals if requested
    try:
        result["features"] = extract_features(audio)
        if include_visuals:
            result.update(get_visualizations(audio))
    except Exception as e:
        print(f"[ERROR] Extracting features: {e}", flush=True)

    # Convert all numpy types to native Python types for safe SocketIO/Flask JSON serialization
    def to_native(obj):
        if isinstance(obj, dict):
            return {k: to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list) or isinstance(obj, tuple):
            return [to_native(v) for v in obj]
        elif isinstance(obj, np.generic):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    return to_native(result)

# ==============================================================================
# FLASK ROUTES
# ==============================================================================
@app.route("/")
def index():
    resp = make_response(render_template("index.html"))
    # Strictly disable caching
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

@app.route("/simulate/<audio_type>")
def simulate(audio_type):
    """Test endpoint for the UI 'Inject Payload' buttons."""
    fname = "ai_sample.flac" if audio_type == "ai" else "human_sample.m4a"
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", fname)
    if not os.path.exists(path):
        return jsonify({"error": "Sample file not found"}), 404
    
    try:
        audio = file_to_audio(path, os.path.splitext(path)[1].lower())
        res = analyze_audio(audio, include_visuals=False)
        return jsonify(res)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/predict", methods=["POST"])
def predict():
    """Endpoint for File Analysis batch uploads."""
    files = request.files.getlist("audio")
    if not files: return jsonify({"error": "No files"}), 400
    
    results = []
    for f in files:
        fname = f.filename or "unknown"
        ext = os.path.splitext(fname)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            results.append({"filename": fname, "error": f"Unsupported extension: {ext}"})
            continue

        # Save uploaded file safely
        fd, tmp_path = tempfile.mkstemp(suffix=ext)
        os.close(fd) # Close handle BEFORE Flask saves to it
        
        try:
            f.save(tmp_path)
            audio = file_to_audio(tmp_path, ext)
            res = analyze_audio(audio, include_visuals=True)
            res["filename"] = fname
            results.append(res)
        except Exception as e:
            traceback.print_exc()
            results.append({"filename": fname, "error": str(e)})
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return jsonify({"results": results})

# ==============================================================================
# SOCKET.IO ROUTES
# ==============================================================================
user_audio_bytes = {}

@socketio.on("audio_chunk")
def on_chunk(data):
    sid = request.sid
    if sid not in user_audio_bytes:
        user_audio_bytes[sid] = bytearray()
    
    user_audio_bytes[sid].extend(data)
    
    # Safety reset if buffer gets too large (e.g., > 10MB)
    if len(user_audio_bytes[sid]) > 10 * 1024 * 1024:
        user_audio_bytes[sid] = bytearray(data)

    try:
        fd_in, in_path = tempfile.mkstemp(suffix=".webm")
        fd_out, out_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd_in); os.close(fd_out)

        with open(in_path, "wb") as f:
            f.write(user_audio_bytes[sid])
        
        safe_convert_audio(in_path, out_path)
        audio, _ = librosa.load(out_path, sr=22050)
        
        # Only analyze the most recent 3 seconds of audio to keep it real-time
        if len(audio) > 22050 * 3:
            audio = audio[-22050 * 3:]
        
        if len(audio) >= 100:
            res = analyze_audio(audio, sid=sid, include_visuals=True)
            emit("risk_update", res)

    except Exception as e:
        print(f"[ERROR] Live stream chunk failed: {e}", flush=True)
        emit("analysis_error", {"error": str(e)})
    finally:
        for p in [in_path, out_path]:
            if 'p' in locals() and os.path.exists(p):
                try: os.remove(p)
                except: pass

@socketio.on("reset_stream")
def on_reset():
    sid = request.sid
    user_audio_bytes[sid] = bytearray()
    session_buffers.pop(sid, None)

@socketio.on("disconnect")
def on_disc():
    sid = request.sid
    session_buffers.pop(sid, None)
    user_audio_bytes.pop(sid, None)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
