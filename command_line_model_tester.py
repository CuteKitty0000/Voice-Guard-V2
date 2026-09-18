import tensorflow as tf
import argparse
import librosa
import numpy as np

#parse arguments
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument("-m", "--model", dest="model_path", required=True, help="Keras model")
arg_parser.add_argument("-c", "--clips", dest="clips", nargs="+", required=True, help="Audio clips to classify")
arg_parser.add_argument("-n", "--n-mels", default=91, dest="n_mels", help="Number of mel bands in the spectogram")

args = arg_parser.parse_args()

#load clips
import subprocess, tempfile, os as _os

def load_audio(path):
    """Load audio file, using ffmpeg to convert M4A/MP4 first if needed."""
    ext = _os.path.splitext(path)[1].lower()
    if ext in ('.m4a', '.mp4', '.aac', '.mp3'):
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp.close()
        try:
            subprocess.run(
                ['ffmpeg', '-y', '-i', path, tmp.name],
                check=True, capture_output=True
            )
            audio, sr = librosa.load(tmp.name)
        finally:
            _os.unlink(tmp.name)
    else:
        audio, sr = librosa.load(path)
    return audio

x = []
for clip in args.clips:
    try:
        audio = load_audio(clip)
        print(f"Loaded {clip}: length={len(audio)}")
        
        if len(audio) == 0:
            raise ValueError(f"Audio file {clip} is empty or could not be loaded properly")
            
        mel_spectrogram = librosa.feature.melspectrogram(y=audio, n_mels=args.n_mels)
        mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)

        max_time_steps = 150
        if mel_spectrogram.shape[1] < max_time_steps:
            mel_spectrogram = np.pad(mel_spectrogram, ((0, 0), (0, max_time_steps - mel_spectrogram.shape[1])), mode='constant')
        else:
            mel_spectrogram = mel_spectrogram[:, :max_time_steps]

        x.append(mel_spectrogram)
        
    except Exception as e:
        print(f"Error processing {clip}: {str(e)}")
        continue

if not x:
    print("No audio files were successfully processed. Exiting.")
    print("Please make sure the audio files are in a supported format (flac or m4a).")
    exit(1)

x = np.array(x)

#load keras model
# Try standard load first; fall back to legacy H5 loader for old Keras 2 .keras files
try:
    model = tf.keras.models.load_model(args.model_path)
except Exception:
    # Model is saved in HDF5 format (Keras 2) - copy to .h5 extension and reload
    import shutil, tempfile, os
    tmp = tempfile.NamedTemporaryFile(suffix=".h5", delete=False)
    tmp.close()
    shutil.copy2(args.model_path, tmp.name)
    model = tf.keras.models.load_model(tmp.name)
    os.unlink(tmp.name)

predictions = model.predict(x)

for p in predictions:
  print("prediction")
  print("chance of human: " + str(round(p[1]*100, 1)) + "%")
  print("chance of AI: " + str(round(p[0]*100, 1)) + "%")
print("keras (tensorflow) prediction object: " + str(predictions))

print("--------------------------------")

if p[1] > 0.5:
  print("Human!")
else:
  print("AI!")



