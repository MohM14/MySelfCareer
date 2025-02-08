import streamlit as st
import audio_recorder_streamlit as recorder  # For recording audio from the browser
import numpy as np
import librosa
import tempfile
import speech_recognition as sr
import openai

# Holland code mapping for personality (for reference)
holand_categories = {
    "واقعي": "Realistic",
    "تحليلي": "Investigative",
    "فني": "Artistic",
    "اجتماعي": "Social",
    "ريادي": "Enterprising",
    "تقليدي": "Conventional"
}

def extract_basic_features(y, sr):
    """
    Extract basic acoustic features using librosa:
      - MFCCs: Mean and Standard Deviation for 13 coefficients
      - Fundamental Frequency (Pitch): Mean and Standard Deviation using librosa.pyin
      - RMS Energy
      - Zero Crossing Rate (ZCR)
      - Spectral Centroid
    """
    # 1. MFCCs
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfccs_mean = np.mean(mfccs, axis=1).tolist()
    mfccs_std = np.std(mfccs, axis=1).tolist()
    
    # 2. Fundamental Frequency (Pitch)
    try:
        f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'),
                                     fmax=librosa.note_to_hz('C7'))
        f0_clean = f0[~np.isnan(f0)]
        if len(f0_clean) > 0:
            f0_mean = float(np.mean(f0_clean))
            f0_std = float(np.std(f0_clean))
        else:
            f0_mean, f0_std = None, None
    except Exception as e:
        st.error(f"Error extracting pitch: {e}")
        f0_mean, f0_std = None, None

    # 3. RMS Energy
    rms = librosa.feature.rms(y=y)
    rms_mean = float(np.mean(rms))
    
    # 4. Zero Crossing Rate (ZCR)
    zcr = librosa.feature.zero_crossing_rate(y)
    zcr_mean = float(np.mean(zcr))
    
    # 5. Spectral Centroid
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_centroid_mean = float(np.mean(spectral_centroid))
    
    return {
        "mfccs_mean": mfccs_mean,
        "mfccs_std": mfccs_std,
        "f0_mean": f0_mean,
        "f0_std": f0_std,
        "rms_mean": rms_mean,
        "zcr_mean": zcr_mean,
        "spectral_centroid_mean": spectral_centroid_mean
    }
def compute_jitter_shimmer_from_pitch(y, sr):
    """
    Compute approximate jitter and shimmer using pitch estimates from librosa.pyin.
    This function calculates jitter as the mean absolute difference between consecutive
    pitch periods divided by the mean pitch period, and shimmer as the relative amplitude
    differences. Note: This is a simplified approach and may not exactly match Praat's algorithms.
    """
    # Estimate pitch using pyin:
    f0, voiced_flag, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    # Remove nan values
    f0 = f0[~np.isnan(f0)]
    if len(f0) < 2:
        return None, None
    # Compute pitch periods (in seconds)
    periods = 1.0 / f0
    # Compute jitter: mean absolute difference between consecutive periods, normalized by mean period.
    jitter = np.mean(np.abs(np.diff(periods))) / np.mean(periods)
    
    # For shimmer, we need amplitude information.
    # Compute the root-mean-square (RMS) energy over short frames:
    rms = librosa.feature.rms(y=y)[0]
    # Assume that each pitch period corresponds approximately to a frame;
    # this is a rough approximation.
    if len(rms) < 2:
        shimmer = None
    else:
        shimmer = np.mean(np.abs(np.diff(rms))) / np.mean(rms)
    return jitter, shimmer

def extract_voice_quality(audio_file_path):
    """
    Extract voice quality features. First, try a Praat-based approach.
    If that fails, fall back to a manual computation using librosa.
    """
    try:
        y, sr = librosa.load(audio_file_path, sr=None)
        jitter, shimmer = compute_jitter_shimmer_from_pitch(y, sr)

    except Exception as e2:
        st.error(f"Fallback extraction failed: {e2}")
        jitter, shimmer = None, None

    return {
        "jitter": jitter,
        "shimmer": shimmer,
    }


def recognize_speech_from_audio(audio_file_path):
    """
    Convert the recorded audio to text using SpeechRecognition.
    The language is set to Arabic ("ar-SA").
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
    try:
        recognized_text = recognizer.recognize_google(audio_data, language="ar-SA")
    except sr.UnknownValueError:
        recognized_text = "لم يتمكن النظام من فهم التسجيل الصوتي."
    except sr.RequestError as e:
        recognized_text = f"حدث خطأ أثناء طلب النتائج؛ {e}"
    return recognized_text

def compute_speaking_rate(recognized_text, duration_seconds):
    """
    Compute speaking rate in words per minute.
    """
    word_count = len(recognized_text.split())
    duration_minutes = duration_seconds / 60.0
    return word_count / duration_minutes if duration_minutes > 0 else 0

def generate_prompt(recognized_text, basic_features, quality_features, speaking_rate):
    """
    Generate an Arabic prompt (with English feature names) for GPT-4,
    instructing it to analyze the recognized text and speech features to
    detect personality according to the Holland model.
    """
    prompt = f"""
أنت خبير في تحليل الشخصية. يرجى تحليل المعلومات المستخرجة من التسجيل الصوتي أدناه وتحديد رمز شخصية المتحدث باستخدام نموذج هولاند. الفئات المتاحة هي:

- واقعي
- تحليلي
- فني
- اجتماعي
- ريادي
- تقليدي

فيما يلي البيانات المستخرجة من التسجيل الصوتي:

**Recognized Text:**  
{recognized_text}

**Extracted Basic Speech Features:**  
- MFCCs (Mean): {basic_features.get('mfccs_mean', 'N/A')}
- MFCCs (Standard Deviation): {basic_features.get('mfccs_std', 'N/A')}
- Fundamental Frequency (Mean): {basic_features.get('f0_mean', 'N/A')}
- Fundamental Frequency (Standard Deviation): {basic_features.get('f0_std', 'N/A')}
- RMS Energy: {basic_features.get('rms_mean', 'N/A')}
- Zero Crossing Rate: {basic_features.get('zcr_mean', 'N/A')}
- Spectral Centroid: {basic_features.get('spectral_centroid_mean', 'N/A')}

**Extracted Voice Quality Features:**  
- Jitter: {quality_features.get('jitter', 'N/A')}
- Shimmer: {quality_features.get('shimmer', 'N/A')}

**Additional Feature:**  
- Speaking Rate (words per minute): {speaking_rate:.2f}

بناءً على هذه البيانات، يرجى تقديم تحليل مفصل وتحديد أي فئة (أو فئات) من الفئات المذكورة أعلاه تصف شخصية المتحدث وفقًا لنموذج هولاند. كما يرجى توضيح الأسباب والاعتبارات التي استندت إليها في تحليل الشخصية.
"""
    return prompt

def main():
    st.title("كشف الشخصية من خلال الصوت")
    st.write(
        """
        **تعليمات:**  
        1. قم بتسجيل صوتك باللغة العربية لمدة تقارب الدقيقة أثناء الحديث عن نفسك.  
        2. سيقوم التطبيق بتخزين التسجيل؛ ثم اضغط على "ابدأ تحليل التسجيل" لبدء استخراج الميزات وتحليل التسجيل.  
        3. سيتم تحليل الشخصية باستخدام LLMs.
        """
    )
    
    st.info("اضغط على الزر أدناه للبدء في التسجيل. عند الانتهاء، سيظهر زر لتحليل التسجيل.")

    # Step 1: Record audio using audio-recorder-streamlit
    audio_bytes = recorder.audio_recorder()
    
    if audio_bytes is not None:
        st.audio(audio_bytes, format="audio/wav")
        
        # Step 2: Analysis button appears after recording
        if st.button("ابدأ تحليل التسجيل"):
            # Save recording to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
                temp_audio_file.write(audio_bytes)
                temp_audio_file.flush()
                audio_file_path = temp_audio_file.name

            # Load audio using librosa to extract basic features
            try:
                y, sr_rate = librosa.load(audio_file_path, sr=None)
            except Exception as e:
                st.error(f"حدث خطأ أثناء تحميل التسجيل: {e}")
                return
            
            # Compute audio duration
            duration_seconds = len(y) / sr_rate

            st.write("جارٍ استخراج الميزات الأساسية...")
            basic_features = extract_basic_features(y, sr_rate)
            # st.subheader("الميزات الأساسية المستخرجة")
            # st.json(basic_features)

            st.write("جارٍ استخراج ميزات جودة الصوت...")
            quality_features = extract_voice_quality(audio_file_path)
            # st.subheader("ميزات جودة الصوت المستخرجة")
            # st.json(quality_features)

            st.write("جارٍ تحويل التسجيل الصوتي إلى نص...")
            recognized_text = recognize_speech_from_audio(audio_file_path)
            st.subheader("النص الذي تم التعرف عليه")
            st.write(recognized_text)

            # Compute speaking rate
            speaking_rate = compute_speaking_rate(recognized_text, duration_seconds)
            # st.subheader("معدل الكلام (كلمة في الدقيقة)")
            # st.write(f"{speaking_rate:.2f} كلمة في الدقيقة")

            # # Form the payload
            # payload = {
            #     "recognized_text": recognized_text,
            #     "basic_speech_features": basic_features,
            #     "voice_quality_features": quality_features,
            #     "speaking_rate": speaking_rate,
            #     "holand_categories": holand_categories
            # }
            # st.subheader("حمولة البيانات")
            # st.json(payload)

            # Generate the prompt and store it in session state
            prompt = generate_prompt(recognized_text, basic_features, quality_features, speaking_rate)
            st.session_state.prompt = prompt  # Save the prompt for later use
            st.subheader("المطالبة الموجهة لـ GPT-4")
            st.code(prompt, language="markdown")
        
        # Step 3: Use the stored prompt for sending to OpenAI
        if "prompt" in st.session_state and st.button("إرسال الطلب إلى OpenAI"):
            try:
                openai.api_key = st.secrets["openai"]["api_key"]
                # Retrieve prompt from session state
                saved_prompt = st.session_state.prompt
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",  # Use "gpt-3.5-turbo" if GPT-4 is not available
                    messages=[
                        {"role": "system", "content": "أنت مساعد تحليل شخصية."},
                        {"role": "user", "content": saved_prompt}
                    ]
                )
                gpt_response = response.choices[0].message.content.strip()
                st.subheader("رد GPT:")
                st.write(gpt_response)
            except Exception as e:
                st.error(f"حدث خطأ أثناء إرسال الطلب إلى OpenAI: {e}")

if __name__ == "__main__":
    main()
