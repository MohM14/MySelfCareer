import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import librosa

# Function to record audio
def record_audio(filename="speech.wav", duration=30, fs=44100):
    st.write("جارٍ التسجيل...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    write(filename, fs, audio)
    st.write("تم التسجيل بنجاح!")

# Function to transcribe audio
def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language="ar-SA")
    except sr.UnknownValueError:
        return "لم أتمكن من فهم الصوت."
    except sr.RequestError:
        return "حدث خطأ في خدمة التعرف على الصوت."
    except Exception as e:
        return f"خطأ: {str(e)}"

# Function to extract speech features
def extract_speech_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)
        features = {
            "tempo": librosa.beat.tempo(y, sr=sr)[0],  # Speech speed
            "energy": librosa.feature.rms(y=y).mean(),  # Loudness
            "pitch": librosa.yin(y, fmin=50, fmax=300).mean(),  # Average pitch
        }
        return features
    except Exception as e:
        st.error(f"خطأ أثناء استخراج خصائص الصوت: {str(e)}")
        return None

# Rule-based major prediction
def predict_major(transcription, features):
    # Rule 1: Keywords in the transcription
    if any(word in transcription for word in ["رياضة", "نشاط بدني", "الحركة"]):
        return "واقعي"
    if any(word in transcription for word in ["تحليل", "بحث", "استنتاج"]):
        return "تحليلي"
    if any(word in transcription for word in ["فن", "رسم", "تصميم"]):
        return "فني"
    if any(word in transcription for word in ["أصدقاء", "اجتماعي", "تفاعل"]):
        return "اجتماعي"
    if any(word in transcription for word in ["ريادة", "مشروع", "قيادة"]):
        return "ريادي"
    if any(word in transcription for word in ["إدارة", "تنظيم", "ترتيب"]):
        return "تقليدي"
    
    # Rule 2: Based on speech features
    if features["tempo"] > 150:
        return "اجتماعي"
    if features["energy"] > 0.1:
        return "ريادي"
    if features["pitch"] < 100:
        return "تحليلي"
    
    # Default rule
    return "غير محدد"

# Streamlit App
st.title("تحديد التخصص بناءً على حديثك عن هواياتك")
st.warning("تحدث عن هواياتك لمدة نصف دقيقة")
# Record button
if st.button("ابدأ التسجيل"):
    record_audio()

# Analyze button
if st.button("تحليل الصوت"):
    try:
        # Transcribe audio
        transcription = transcribe_audio("speech.wav")
        st.write("النص المستخرج:", transcription)

        # Extract speech features
        features = extract_speech_features("speech.wav")
        if features:
            st.write("السمات الصوتية:", features)

            # Predict major
            major = predict_major(transcription, features)
            st.write(f"التخصص المقترح: {major}")
    except Exception as e:
        st.error(f"حدث خطأ أثناء التحليل: {str(e)}")
