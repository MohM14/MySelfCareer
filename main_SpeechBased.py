import streamlit as st
import librosa
import numpy as np
import soundfile as sf
import tempfile
from streamlit_mic_recorder import mic_recorder

# Define Holland Code Rules
def classify_holland_code(features):
    pitch, speech_rate, intensity, prosody_variation, pause_duration = features

    if pitch < 200 and 2 <= speech_rate <= 4 and intensity == "steady":
        reason = "Pitch is low, speech rate is moderate, and intensity is steady."
        return "Realistic", reason
    elif 150 <= pitch <= 300 and pause_duration <= 0.8:
        reason = "Pitch is in the medium range, and pause duration is short."
        return "Investigative", reason
    elif prosody_variation > 20 and intensity == "dynamic":
        reason = "Prosody variation is high, and intensity is dynamic."
        return "Artistic", reason
    elif 200 <= pitch <= 350 and speech_rate >= 3:
        reason = "Pitch is medium to high, and speech rate is fast."
        return "Social", reason
    elif pitch >= 250 and speech_rate > 4 and intensity == "strong":
        reason = "Pitch is high, speech rate is very fast, and intensity is strong."
        return "Enterprising", reason
    elif pitch <= 200 and speech_rate <= 4 and prosody_variation <= 10:
        reason = "Pitch is low, speech rate is slow, and prosody variation is minimal."
        return "Conventional", reason
    else:
        reason = "Features do not strongly match any category."
        return "Uncertain", reason

# Speech feature extraction
def extract_features(audio_file):
    y, sr = librosa.load(audio_file, sr=None)
    
    # Ensure proper handling of silence
    y, _ = librosa.effects.trim(y)
    
    # Extract pitch using yin
    try:
        pitch = np.mean(librosa.yin(y, librosa.note_to_hz('C2'), librosa.note_to_hz('C7'), sr=sr))
    except:
        pitch = 0.0  # Handle silent audio
    
    # Calculate speech rate
    intervals = librosa.effects.split(y, top_db=20)
    speech_duration = sum((end - start) for start, end in intervals) / sr
    total_duration = len(y) / sr
    speech_rate = (len(intervals) / speech_duration) if speech_duration > 0 else 0.0

    # Intensity (Root Mean Square Energy)
    rms = librosa.feature.rms(y=y)
    intensity = "dynamic" if np.std(rms) > 0.05 else "steady"

    # Prosody variation (MFCC standard deviation)
    prosody_variation = np.std(librosa.feature.mfcc(y=y, sr=sr))

    # Average pause duration
    pauses = [(start - end) for end, start in zip(intervals[1:], intervals[:-1])]
    pause_duration = np.mean(pauses) / sr if pauses else 0.0

    return pitch, speech_rate, intensity, prosody_variation, pause_duration

# Streamlit Interface
st.title("Holland Code Speech Classifier")

# Mic Recorder Integration
st.write("### Record Your Voice")
recorded_audio = mic_recorder(start_prompt="⏺️", stop_prompt="⏹️", key='recorder')

if recorded_audio:
    # Save recorded audio to a temporary file
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(temp_audio_file.name, "wb") as f:
        f.write(recorded_audio['bytes'])
    st.session_state["audio_file"] = temp_audio_file.name
    st.audio(temp_audio_file.name, format='audio/wav')
    st.success("Recording saved. Proceed to analysis.")

# Main page for analysis
st.write("Once you've recorded your voice, analyze it here.")

if "audio_file" in st.session_state and st.session_state["audio_file"]:
    if st.button("Analyze Holland Code"):
        try:
            features = extract_features(st.session_state["audio_file"])
            category, reason = classify_holland_code(features)

            st.success(f"Your Holland Code category is: {category}")
            st.write(f"### Reason: {reason}")

            st.write("### Extracted Features:")
            st.write(f"- Pitch: {features[0]:.2f} Hz")
            st.write(f"- Speech Rate: {features[1]:.2f} words/sec")
            st.write(f"- Intensity: {features[2]}")
            st.write(f"- Prosody Variation: {features[3]:.2f}")
            st.write(f"- Pause Duration: {features[4]:.2f} seconds")
        except Exception as e:
            st.error(f"Error analyzing the audio: {e}")

