import streamlit as st
import librosa
import numpy as np
import sounddevice as sd
import wavio

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
# Speech feature extraction (remove @st.cache)
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

# Record audio
def record_audio(duration=5, samplerate=44100, filename="recorded_audio.wav"):
    st.info("Recording... Speak into the microphone.")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()  # Wait for the recording to finish
    wavio.write(filename, audio_data, samplerate, sampwidth=2)
    st.success("Recording complete!")
    return filename

# Streamlit Interface
st.title("Holland Code Speech Classifier")

# Option to record or upload audio
record_option = st.radio("How would you like to provide audio?", ("Record your voice", "Upload an audio file"))

if record_option == "Record your voice":
    duration = st.slider("Select recording duration (seconds):", min_value=3, max_value=10, value=5)
    if st.button("Start Recording"):
        audio_file = record_audio(duration=duration)
        st.audio(audio_file, format='audio/wav')
        st.write("Analyzing your speech...")

        try:
            features = extract_features(audio_file)
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
            st.error(f"Error analyzing the audio file: {e}")

elif record_option == "Upload an audio file":
    uploaded_file = st.file_uploader("Upload your audio file", type=["wav", "mp3"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
        st.write("Analyzing your speech...")

        try:
            features = extract_features(uploaded_file)
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
            st.error(f"Error analyzing the audio file: {e}")
else:
    st.info("Please provide an audio input to proceed.")
