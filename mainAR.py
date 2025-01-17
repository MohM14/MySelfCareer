import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import csv

# إعداد اتجاه الكتابة من اليمين إلى اليسار
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    body {
        direction: rtl;
        text-align: right;
    }
    .css-1d391kg { direction: rtl; text-align: right; }
    .css-1wbxubw { direction: rtl; text-align: right; }
    .css-1vq4p4l { direction: rtl; text-align: right; }
    </style>
    """,
    unsafe_allow_html=True,
)


# import streamlit as st
# import streamlit as st
from streamlit_audio_recorder import audio_recorder
import speech_recognition as sr
import librosa
import numpy as np
import io
from scipy.io.wavfile import write


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


# تعريف الأسئلة لكل فئة (20 سؤال لكل فئة)
questions_dict = {
    "واقعي": [
    "أستمتع بالأنشطة التي تتطلب استخدام اليدين في العمل.",
    "أستمتع بالعمل مع الأدوات الميكانيكية.",
    "أفضّل العمل في البيئات الخارجية على العمل في مكاتب مغلقة.",
    "أحب العمل في المهام التي تتطلب قوة بدنية.",
    "أستمتع بالتعامل مع المعدات والأجهزة التقنية.",
    "أفضّل العمل في الوظائف التي تشمل استخدام الآلات.",
    "أستمتع بإصلاح الأشياء التي تعطلت.",
    "أحب العمل في مجالات البناء أو التصنيع.",
    "أستمتع بالأنشطة التي تتطلب قدرًا من المخاطرة الجسدية.",
    "أفضّل العمل مع المواد الملموسة مثل المعادن أو الخشب.",
    "أحب العمل في الأماكن التي تتطلب الجهد البدني.",
    "أستمتع بالأنشطة التي تتضمن الصيانة والإصلاحات.",
    "أفضّل الوظائف التي تشمل التعامل مع الحيوانات.",
    "أحب التنقل في بيئات طبيعية مثل الغابات أو البحار.",
    "أفضّل العمل مع أدوات كهربائية أو معدات صناعية.",
    "أستمتع بالأنشطة التي تتطلب التنسيق بين الحركات اليدوية والعقلية.",
    "أحب المشاريع التي تتضمن تحسين أو بناء شيء من الصفر.",
    "أفضّل العمل في مجالات الزراعة أو التعدين.",
    "أستمتع بالحرف اليدوية أو البناء.",
    "أفضّل النشاطات التي تشمل حركة جسدية مستمرة."
    ],
    "تحليلي": [
    "أحب حل الألغاز والمسائل المعقدة.",
    "أستمتع بالبحث العلمي وحل المشكلات من خلال التجربة.",
    "أحب تعلم أشياء جديدة واكتشاف الحقائق.",
    "أفضّل الأنشطة التي تتطلب التفكير النقدي والتحليل.",
    "أستمتع بقراءة الكتب أو المقالات العلمية.",
    "أعتقد أن اكتشاف المعلومات المجهولة هو أمر مثير.",
    "أحب البحث في المواضيع التي تتطلب قدرًا كبيرًا من التفكير المنطقي.",
    "أفضّل حل المشكلات التي تتطلب استخدام الرياضيات أو العلوم.",
    "أحب القيام بالتجارب العلمية أو البحث الأكاديمي.",
    "أستمتع بتحليل البيانات وتفسير النتائج.",
    "أحب مناقشة الأفكار الفلسفية أو النظرية.",
    "أفضّل المهام التي تتطلب استكشاف الأسباب والنتائج.",
    "أستمتع بالعمل الذي يتطلب تحليلاً علميًا.",
    "أفضّل الوظائف التي تتضمن البحث عن حلول للمشكلات.",
    "أحب تعلم أشياء جديدة في مجالات العلوم والتكنولوجيا.",
    "أستمتع بمحاولة فك شفرات أو رموز معقدة.",
    "أعتقد أن المعرفة هي أداة قوية لفهم العالم من حولي.",
    "أستمتع بتطوير أفكار جديدة وتحليل نظريات مختلفة.",
    "أفضّل العمل الذي يتطلب تحليل المعلومات المعقدة.",
    "أحب تعلم كيفية عمل الأشياء بطريقة علمية."
    ],
    "فني": [
    "أستمتع برسم اللوحات أو القيام بالأعمال الفنية.",
    "أحب كتابة القصص أو الشعر.",
    "أفضّل العمل الذي يتطلب الإبداع والتخيل.",
    "أحب التقاط الصور أو إنتاج الأفلام.",
    "أستمتع بتصميم الأزياء أو الملابس.",
    "أحب أن أكون في بيئة فنية أو ثقافية.",
    "أستمتع بالأنشطة التي تتطلب التعبير عن نفسي من خلال الفن.",
    "أحب تصميم الغرف أو المساحات الداخلية.",
    "أستمتع بتأليف الموسيقى أو العزف على الآلات الموسيقية.",
    "أستمتع بالأنشطة التي تتضمن الرقص أو الأداء.",
    "أحب التعبير عن نفسي من خلال الكتابة الإبداعية.",
    "أستمتع بتطوير أفكار جديدة في الفن أو التصميم.",
    "أفضّل العمل في المجالات التي تتطلب الخيال والإبداع.",
    "أحب العمل في بيئات تشجع على الفن والابتكار.",
    "أستمتع بتطوير مشروع فني من الصفر.",
    "أستمتع بالأنشطة التي تتطلب استخدام الألوان والأشكال.",
    "أفضّل العمل في مجال يتطلب تصاميم فنية.",
    "أحب العمل في مشاريع تتضمن التعبير عن الذات.",
    "أستمتع بالأعمال التي تتطلب إبداعًا وفكرًا غير تقليدي.",
    "أفضّل الأنشطة التي تتطلب التفكير الجمالي والإبداعي."
    ],
    "اجتماعي": [
    "أستمتع بمساعدة الآخرين في حل مشكلاتهم الشخصية.",
    "أحب العمل مع الآخرين لتحقيق هدف مشترك.",
    "أستمتع بالتفاعل مع الآخرين في المواقف الاجتماعية.",
    "أحب التحدث مع الناس ومساعدتهم في اتخاذ قراراتهم.",
    "أستمتع بتوجيه وإرشاد الآخرين.",
    "أفضّل العمل في بيئات تعاونية.",
    "أحب العمل مع الأطفال أو الشباب.",
    "أستمتع بتعليم الآخرين أو تقديم المعلومات.",
    "أستمتع بالعمل في مجالات الرعاية الصحية أو الاجتماعية.",
    "أفضّل العمل مع فريق من الأشخاص لتحقيق النجاح.",
    "أستمتع بالاستماع إلى مشاعر وآراء الآخرين.",
    "أحب تقديم الدعم العاطفي للآخرين.",
    "أستمتع بتقديم المشورة للأشخاص في مواقف حياتية.",
    "أحب التدريس أو تدريب الآخرين.",
    "أستمتع بإجراء محادثات مع الناس حول قضايا اجتماعية.",
    "أفضّل الوظائف التي تتطلب التعامل مع الأشخاص بشكل مستمر.",
    "أستمتع بالعمل في الأنشطة الجماعية مثل المنظمات التطوعية.",
    "أحب إرشاد الآخرين خلال التحديات.",
    "أستمتع بمساعدة الآخرين في تعلم مهارات جديدة.",
    "أحب العمل في المجالات التي تتطلب مساعدة الآخرين على النمو الشخصي."
    ],
    "ريادي": [
    "أحب قيادة الفرق وتحفيز الآخرين لتحقيق أهدافهم.",
    "أستمتع باتخاذ القرارات الهامة في العمل.",
    "أحب التحدث أمام الجمهور أو تقديم العروض.",
    "أستمتع بتطوير مشاريع جديدة أو أفكار تجارية.",
    "أعتقد أن النجاح يعتمد على القدرة على التأثير في الآخرين.",
    "أستمتع بتحديات بيئات العمل التي تتطلب قيادة الفريق.",
    "أحب العمل في المبيعات أو التسويق.",
    "أستمتع بإنشاء مشاريع جديدة أو فرصة عمل.",
    "أفضّل العمل في المجالات التي تتطلب التفاوض أو اتخاذ قرارات سريعة.",
    "أستمتع بممارسة الأنشطة التي تتطلب المبادرة والعمل بسرعة.",
    "أحب اتخاذ المسؤوليات واتخاذ القرارات الصعبة.",
    "أستمتع بالمشاريع التي تتطلب إقناع الآخرين.",
    "أحب تقديم حلول مبتكرة في المواقف الصعبة.",
    "أستمتع بممارسة الأعمال التي تتطلب مهارات قيادية.",
    "أحب أن أكون في مكان يمكنني فيه التأثير على الآخرين.",
    "أستمتع بالتسويق للمنتجات أو الأفكار الجديدة.",
    "أحب الأنشطة التي تتطلب طموحًا قويًا وتحقيق النجاح.",
    "أستمتع بتحديات العمل التي تتطلب منافسة.",
    "أفضّل العمل في بيئات سريعة الحركة ومتغيرة.",
    "أحب القيام بأنشطة تجارية أو ريادية."
    ],
    "تقليدي": [
    "أحب تنظيم الملفات والبيانات بشكل مرتب.",
    "أستمتع بتنظيم الأعمال اليومية وفقًا للجدول الزمني.",
    "أفضّل العمل في بيئات منظمة ومرتبة.",
    "أستمتع بالأنشطة التي تتطلب الدقة والتركيز على التفاصيل.",
    "أحب إتمام المهام التي تتطلب الانضباط والالتزام بالقواعد.",
    "أستمتع بالعمل الذي يتطلب تنظيم الموارد والمعلومات.",
    "أحب العمل في الوظائف التي تشمل الحسابات أو الإدارة.",
    "أستمتع بإعداد التقارير أو الوثائق.",
    "أحب الأنشطة التي تتطلب التفاعل مع الأنظمة أو القواعد.",
    "أستمتع بتحديد وتنظيم الأنشطة اليومية.",
    "أفضّل العمل الذي يتطلب متابعة الإجراءات والروتين.",
    "أستمتع بإنشاء قوائم أو جداول لتنظيم الأمور.",
    "أحب التفاعل مع الأرقام والبيانات.",
    "أستمتع بالوظائف التي تتطلب تقديم التقارير أو البيانات.",
    "أحب العمل في بيئات تتسم بالروتين والنظام.",
    "أفضّل العمل الذي يتطلب انتباهًا شديدًا للتفاصيل.",
    "أستمتع بتحديد الأولويات وتنظيم المهام.",
    "أحب العمل في وظائف تتطلب احترام القواعد والسياسات.",
    "أستمتع بالوظائف التي تتطلب إدارة الوقت والتخطيط.",
    "أفضّل العمل في بيئات تتسم بالاستقرار والروتين."
    ],
}



# الأسئلة والأنشطة
activities = {
    "واقعي": [
        "أستمتع بالمشاركة في الأنشطة الرياضية مثل كرة القدم أو السباحة كرة الطائرة.",
        "أستمتع بالمشاركة في تحديات بدنية مثل سباقات الجري أو التمارين الرياضية.",
        "أشعر بالسعادة عند المساهمة في تنظيم الأنشطة الرياضية المدرسية.",
        "أحب المشاركة في الأعمال التطوعية التي تهدف إلى تحسين البيئة المدرسية.",
        "أشعر بالراحة عند العمل على تنظيم مسابقات رياضية.",
        "أستمتع بالمشاركة في أنشطة الميدان مثل تنظيف أو زراعة المساحات الخارجية."
    ],
    "تحليلي": [
        "أحب المشاركة في المعارض العلمية التي تعرض الابتكارات.",
        "أشعر بالإنجاز عندما أتعلم شيئًا جديدًا من خلال التجارب العلمية.",
        "أستمتع بالمشاركة في مسابقات الروبوتات أو البرمجة.",
        "أحب الأنشطة التي تتيح لي تحليل البيانات أو إيجاد حلول للمشكلات.",
        "أحب حضور ورش العمل العلمية التي تقدم معلومات جديدة.",
        "أستمتع بالمشاركة في أنشطة تشرح الظواهر الطبيعية مثل تجارب الفيزياء."
    ],
    "فني": [
        "أحب المشاركة في الأنشطة الفنية مثل الرسم أو النحت.",
        "أستمتع بالمشاركة في المسرحيات أو العروض الفنية المدرسية.",
        "أحب الأنشطة الإبداعية مثل كتابة القصص أو التصوير.",
        "أحب العمل على مشاريع فنية جماعية مثل تزيين الفصول.",
        "أحب الأنشطة التي تجمع بين التكنولوجيا والفن مثل التصميم الرقمي.",
        "أحب الكتابة الإبداعية مثل كتابة الشعر أو النصوص المسرحية."
    ],
    "اجتماعي": [
        "أحب الأنشطة التي تركز على مساعدة زملائي في تحسين أدائهم الدراسي.",
        "أستمتع بالمشاركة في تنظيم ورش عمل تدريبية للطلاب الجدد.",
        "أشعر بالسعادة عند المشاركة في الأنشطة الخيرية التي تخدم المجتمع المحلي.",
        "أحب العمل مع زملائي لتنظيم أنشطة تطوعية داخل المدرسة.",
        "أستمتع بالمشاركة في الرحلات المدرسية.",
        "أشعر بالسعادة عندما أساعد زملائي في فهم مواضيع دراسية صعبة."
    ],
    "ريادي": [
        "أحب أن أكون قائداً لفريق يعمل على تنظيم فعاليات مدرسية.",
        "أستمتع بابتكار أفكار جديدة لأنشطة مدرسية ممتعة.",
        "أحب الأنشطة التي تعتمد على روح المنافسة مثل المناظرات.",
        "أشعر بالفخر عند المساهمة في تنظيم فعاليات ريادية مبتكرة.",
        "أرى أن الأنشطة التي تتطلب قيادة الفريق ممتعة ومفيدة.",
        "أحب المشاركة في مسابقات تنمية مهارات القيادة والإقناع."
    ],
    "تقليدي": [
        "أحب ترتيب الملفات أو إعداد قوائم للمشاركين في الأنشطة المدرسية.",
        "أحب تسجيل الحضور أو متابعة سجلات الطلاب في الأنشطة.",
        "أستمتع بالمشاركة في تنظيم البيانات وتحليلها لأنشطة المدرسة.",
        "أحب العمل على إعداد تقارير عن نجاح الفعاليات التي أشارك فيها.",
        "أشعر بالراحة عند أداء مهام إدارية تساهم في تنظيم الأنشطة.",
        "أحب متابعة جداول الحصص أو الأحداث المدرسية وتنسيقها."
    ]
}



# قاعدة بيانات التخصصات بالعربية
specializations_database = {
    "واقعي": ["الهندسة الميكانيكية", "التكنولوجيا الصناعية", "إدارة البيئة", "التخصصات الزراعية"],
    "تحليلي": ["علوم البيانات", "الرياضيات", "الفيزياء", "الهندسة الكيميائية"],
    "فني": ["الفنون الجميلة", "تصميم الأزياء", "إنتاج الأفلام", "التصميم الجرافيكي"],
    "اجتماعي": ["التربية", "علم النفس", "الخدمة الاجتماعية", "الصحة العامة"],
    "ريادي": ["إدارة الأعمال", "التسويق", "ريادة الأعمال", "المالية والمحاسبة"],
    "تقليدي": ["إدارة الأعمال", "المحاسبة", "إدارة المكاتب", "الإحصاء"]
}


def save_results_to_csv(questions, answers, scores, filename="results.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["السؤال", "الإجابة", "الفئة"])
        for question, answer in zip(questions, answers):
            writer.writerow([question["question"], answer, question["category"]])
        writer.writerow([])
        writer.writerow(["الفئة", "النقاط"])
        for category, score in scores.items():
            writer.writerow([category, score])


# Streamlit App
st.title("تحديد التخصص")

# Tabs for modes
tabs = st.tabs(["عن طريق الأسئلة", "عن طريق الصوت"])

# Tab 1: Questionnaire
with tabs[0]:
# اختيار 10 أسئلة عشوائية لكل فئة
    if "selected_questions" not in st.session_state:
        st.session_state.selected_questions = []
        for category, questions in questions_dict.items():
            selected_questions = random.sample(questions, 10)  # اختيار 10 أسئلة عشوائية لكل فئة
            for question in selected_questions:
                st.session_state.selected_questions.append({"question": question, "category": category})
    
    # خلط الأسئلة مرة واحدة فقط
    if "shuffled_questions" not in st.session_state:
        st.session_state.shuffled_questions = random.sample(st.session_state.selected_questions, len(st.session_state.selected_questions))
    
    # تعريف الحالة الأخرى
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "scores" not in st.session_state:
        st.session_state.scores = {"واقعي": 0, "تحليلي": 0, "فني": 0, "اجتماعي": 0, "ريادي": 0, "تقليدي": 0}
    if "answers" not in st.session_state:
        st.session_state.answers = []
    
    # دالة حفظ النتائج في ملف CSV
    
    # دالة عرض الأسئلة
    if st.session_state.current_question < len(st.session_state.shuffled_questions):
        current_q_index = st.session_state.current_question
        current_q = st.session_state.shuffled_questions[current_q_index]
    
        # عرض السؤال الحالي
        st.markdown(f"### السؤال {current_q_index + 1}: {current_q['question']}")
    
        # خيارات الإجابة بمقياس ليكرت
        response = st.radio(
            "إجابتك:",
            options=["1 - لا أوافق بشدة", "2 - لا أوافق", "3 - محايد", "4 - أوافق", "5 - أوافق بشدة"],
            key=f"q_{current_q_index}",
        )
    
        # زر التالي
     
        if st.button("التالي"):
            if response:
                # تسجيل الإجابة وتحديث النقاط
                st.session_state.answers.append(response)
                
                # تحديث النقاط بناءً على الإجابة
                if response == "5 - أوافق بشدة":
                    st.session_state.scores[current_q["category"]] += 2
                elif response == "4 - أوافق":
                    st.session_state.scores[current_q["category"]] += 1
            
                # الانتقال إلى السؤال التالي
                st.session_state.current_question += 1
                st.experimental_rerun()
            else:
                st.warning("يرجى اختيار إجابة قبل المتابعة.")
    else:
        if all(score == 0 for score in st.session_state.scores.values()):
            st.write("يبدو أنك اخترت 'لا أوافق بشدة' أو 'غير متأكد' لمعظم الأسئلة.")
            st.write("بناءً على إجاباتك، لم نتمكن من تحديد توافق قوي مع أي نوع من الشخصيات.")
            st.write("يرجى التفكير في اختيار 'أوافق' أو 'أوافق بشدة' للأسئلة التي تشعر أنها تعبر عنك.")
        else:
        # st.write(st.session_state.scores)
            st.sidebar.write("### النتائج الأولية:")
            sorted_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
        
            categories = [item[0] for item in sorted_scores]
            scores = [item[1] for item in sorted_scores]
        
                # رسم المخطط البياني
            # st.sidebar.bar_chart(pd.DataFrame({"الفئات": categories, "النتائج": scores}).set_index("الفئات"))
        
            # اقتراح التخصصات بناءً على النتائج
        # استخراج الفئتين الأعلى
            top_two_categories = sorted_scores[:2]
            
                # عرض النتائج للفئتين الأعلى
            for i, (category, score) in enumerate(top_two_categories, start=1):
                st.sidebar.write(f"### الفئة رقم {i}: {category} بنتيجة {score}")
                if category in specializations_database:
                    st.sidebar.write(" - " + "\n - ".join(specializations_database[category]))
        
        
        st.title("استبيان الأنشطة المفضلة")
        st.write("اختر الأنشطة التي تستمتع بها من كل فئة.")
    
    
        if "checkbox_states" not in st.session_state:
            st.session_state.checkbox_states = {}
    
        for category, questions in activities.items():
            # st.subheader(category)
            for i, question in enumerate(questions):
                # إنشاء مفتاح فريد لكل سؤال
                checkbox_key = f"{category}_{i}"
    
                # عرض checkbox والحصول على حالته
                is_checked = st.checkbox(question, key=checkbox_key)
    
                # منطق تعديل النقاط بناءً على تغيير الحالة
                previous_state = st.session_state.checkbox_states.get(checkbox_key, False)
                if is_checked and not previous_state:
                    st.session_state.scores[category] += 1
                elif not is_checked and previous_state:
                    st.session_state.scores[category] -= 1
    
                # تحديث الحالة السابقة
                st.session_state.checkbox_states[checkbox_key] = is_checked
                    
        
        
        # أسئلة المواد الدراسية
        # استبيان المواد الدراسية المفضلة
        # استبيان المواد الدراسية المفضلة
        # st.session_state.setdefault("subject_states", {})
        if "subject_states" not in st.session_state:
            st.session_state.subject_states = {}
    
    
        st.write("### اختر المواد المفضلة لديك:")
        subjects = [
            "التفكير الناقد",
            "الدراسات الإسلامية",
            "الدراسات الاجتماعية",
            "الرياضيات",
            "العلوم",
            "القرآن الكريم",
            "اللغة الإنجليزية",
            "اللغة العربية",
            "المهارات الرقمية",
        ]
    
        for subject in subjects:
            subject_key = f"subject_{subject}"
            is_checked = st.checkbox(subject, key=subject_key)
            previous_state = st.session_state.subject_states.get(subject_key, False)
            if is_checked and not previous_state:
                if subject in ["المهارات الرقمية", "العلوم"]:
                    st.session_state.scores["واقعي"] += 1
                if subject in ["الرياضيات", "العلوم"]:
                    st.session_state.scores["تحليلي"] += 1
                if subject in ["الفنون", "التربية الفنية"]:
                    st.session_state.scores["فني"] += 1
                if subject in ["الدراسات الاجتماعية", "الدراسات الإسلامية", "القرآن الكريم"]:
                    st.session_state.scores["اجتماعي"] += 1
                if subject in ["التفكير الناقد"]:
                    st.session_state.scores["ريادي"] += 1
                if subject in ["اللغة العربية", "اللغة الإنجليزية"]:
                    st.session_state.scores["تقليدي"] += 1
            elif not is_checked and previous_state:
                if subject in ["المهارات الرقمية", "العلوم"]:
                    st.session_state.scores["واقعي"] -= 1
                if subject in ["الرياضيات", "العلوم"]:
                    st.session_state.scores["تحليلي"] -= 1
                if subject in ["الفنون", "التربية الفنية"]:
                    st.session_state.scores["فني"] -= 1
                if subject in ["الدراسات الاجتماعية", "الدراسات الإسلامية", "القرآن الكريم"]:
                    st.session_state.scores["اجتماعي"] -= 1
                if subject in ["التفكير الناقد"]:
                    st.session_state.scores["ريادي"] -= 1
                if subject in ["اللغة العربية", "اللغة الإنجليزية"]:
                    st.session_state.scores["تقليدي"] -= 1
            st.session_state.subject_states[subject_key] = is_checked
    
            # تحديث الحالة السابقة
            st.session_state.subject_states[subject_key] = is_checked
      
      
      # عرض النتائج النهائية بشكل بياني
        if st.button("تحديث النتيجة"):
            if all(score == 0 for score in st.session_state.scores.values()):
                st.write("يبدو أنك اخترت 'لا أوافق بشدة' أو 'غير متأكد' لمعظم الأسئلة.")
                st.write("بناءً على إجاباتك، لم نتمكن من تحديد توافق قوي مع أي نوع من الشخصيات.")
                st.write("يرجى التفكير في اختيار 'أوافق' أو 'أوافق بشدة' للأسئلة التي تشعر أنها تعبر عنك.")
            else:
                st.write("### النتائج النهائية:")
                sorted_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
            
                categories = [item[0] for item in sorted_scores]
                scores = [item[1] for item in sorted_scores]
            
                # رسم المخطط البياني
                st.bar_chart(pd.DataFrame({"الفئات": categories, "النتائج": scores}).set_index("الفئات"))
        
            # اقتراح التخصصات بناءً على النتائج
        # استخراج الفئتين الأعلى
                top_two_categories = sorted_scores[:2]
                
                # عرض النتائج للفئتين الأعلى
                for i, (category, score) in enumerate(top_two_categories, start=1):
                    st.write(f"### الفئة رقم {i}: {category} بنتيجة {score}")
                    if category in specializations_database:
                        st.write(" - " + "\n - ".join(specializations_database[category]))
    
        # حفظ النتائج في ملف CSV
        # if st.button("حفظ النتائج"):
        #     save_results_to_csv(st.session_state.selected_questions, st.session_state.answers, st.session_state.scores)
        #     st.success("تم حفظ النتائج في ملف results.csv")
# Tab 2: Sound Analysis
with tabs[1]:
    st.header("الوضع: عن طريق الصوت")
    st.warning("اضغط على زر التسجيل ثم تحدث عن هواياتك لمدة دقيقة واحدة:")

    # Record audio using browser
    audio = audio_recorder()

    if audio is not None:
        st.audio(audio, format="audio/wav")
        audio_data = io.BytesIO(audio)
        audio_data.seek(0)

        # Transcribe and extract features
        transcription = transcribe_audio(audio_data)
        st.write("النص المستخرج:", transcription)

        features = extract_speech_features(audio_data.read(), sample_rate=44100)
        if features:
            st.write("السمات الصوتية:", features)
            major = predict_major(transcription, features)
            st.write(f"التخصص المقترح: {major}")
