import streamlit as st
import json
import openai
openai.api_key = st.secrets["openai"]["api_key"]
import random


# حقن CSS للتنسيق (من اليمين لليسار، وألوان وتصميم متناسق)
st.markdown(
    """
    <style>
    @font-face {
        font-family: 'Sakkal Majalla';
        src: local('Sakkal Majalla'), local('SakkalMajalla');
    }
    body {
        direction: rtl;
        background-color: #F8F9FA;
        color: #333;
        font-family: 'Sakkal Majalla', sans-serif;
        margin: 0;
        padding: 0;
    }
    .header {
        background-color: #003B70;
        padding: 1rem 2rem;
        text-align: center;
        color: #f5f5f5;
        position: relative;
    }
    .header h1 {
        margin: 0;
        font-size: 2.2rem;
        color: #ffffff;
    }
    .header .subtitle {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        color: #e0e0e0;
    }
    .hero-container {
        background-color: #F8F9FA;
        padding: 2rem;
        margin-bottom: 1rem;
    }
    .hero-content {
        max-width: 700px;
        margin: 0 auto;
        text-align: center;
        border-radius: 15px;
        background: #fff;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        padding: 2rem;
    }
    .hero-title {
        font-size: 2rem;
        color: #003B70;
        margin-bottom: 1rem;
    }
    .hero-text {
        font-size: 1.2rem;
        color: #444;
        margin-bottom: 1rem;
    }
    /* زر hero-btn تم حذفه من الكود HTML */
    .description {
        font-size: 1.2rem;
        color: #444;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-heading {
        font-size: 1.5rem;
        color: #003B70;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background-color: #00A1E0;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1rem;
        margin: 0.25rem;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #008BC3;
    }
    .next-btn > button {
        background-color: #FF5722;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1rem;
        margin: 0.25rem;
        cursor: pointer;
    }
    .next-btn > button:hover {
        background-color: #e64a19;
    }
    .stProgress > div > div > div {
        background-color: #003B70;
    }
    .intro-container {
        background-color: #fff;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    }
    .intro-title {
        font-size: 2rem;
        color: #003B70;
        font-weight: bold;
    }
    .intro-text {
        font-size: 1.2rem;
        color: #444;
        margin-top: 1rem;
    }
    .report-container {
        background-color: #fff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .feedback-container {
        background-color: #fff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stAlert.success {
        background-color: #e7f3ec !important;
        color: #2e654f !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# نوع الامتحان مع ملفات بنك الأسئلة داخل مجلد QBank
exam_files = {
    "التحصيلي": "QBank/Tahsail.json",
    "القدرات": "QBank/Qodrat.json"
}

def load_questions(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]

# التحليل عبر OpenAI API
import openai

def get_analysis_online(mistake_responses):
    prompt = "حلل الردود التالية التي تمت الإجابة عليها بشكل خاطئ لتحديد نقاط الضعف حاول يكون التحليل مختصر ومركز ويتم تعريف الطالب بالضعف في اي مجال (الرياضيات، الاحياء، الكيمياء، الفيزياء)  بدون تحليل كل سؤال على حده، وانصح الطالب الالتحاق بالدوات في اكاديمية طريق العلم.\n"
    for item in mistake_responses:
        prompt += (
            f"\nالسؤال: {item['question']}\n"
            f"الإجابة المختارة: {item['selected_answer']}\n"
            f"الإجابة الصحيحة: {item.get('correct_answer', 'غير محددة')}\n"
        )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت مساعد مفيد."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"حدث خطأ في الاتصال بواجهة OpenAI: {e}"

def get_analysis(mistake_responses):
    return get_analysis_online(mistake_responses)

# تهيئة متغيرات الحالة
if "intro_shown" not in st.session_state:
    st.session_state.intro_shown = False
if "selected_exam" not in st.session_state:
    st.session_state.selected_exam = ""
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None
if "report_shown" not in st.session_state:
    st.session_state.report_shown = False

# ترويسة التطبيق
st.markdown(
    """
    <div class="header">
        <h1>أكاديمية طريق العلم - ElmWay Academy</h1>
        <div class="subtitle">التعليم الذكي في أي وقت ومن أي مكان</div>
    </div>
    """,
    unsafe_allow_html=True
)

# الصفحة الأولى: المقدمة التعريفية
if not st.session_state.intro_shown:
    st.markdown(
        """
        <div class='hero-container'>
            <div class='hero-content'>
                <div class='hero-title'>مرحباً بكم في الاختبار الذكي!</div>
                <div class='hero-text'>
                    اختر نوع الامتحان الذي ترغب به من بين خيارين:<br>
                    <strong>التحصيلي</strong> أو <strong>القدرات</strong>.<br>
                    سيتم اختيار 10 أسئلة عشوائيًا من بنك الأسئلة المناسب.<br>
                    بعد انتهاء الاختبار ستحصل على تقرير تحليلي واستبيان لتقييم تجربتك.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # زر واحد فقط (حذفنا الزر الأول من HTML)
    if st.button("ابدأ الآن"):
        st.session_state.intro_shown = True
        st.experimental_rerun()
else:
    # الخطوة 1: اختيار نوع الامتحان
    if st.session_state.selected_exam == "":
        exam_choice = st.selectbox("اختر الامتحان", list(exam_files.keys()))
        if st.button("ابدأ الامتحان"):
            st.session_state.selected_exam = exam_choice
            all_questions = load_questions(exam_files[st.session_state.selected_exam])
            if len(all_questions) >= 10:
                st.session_state.quiz_questions = random.sample(all_questions, 20)
            else:
                st.session_state.quiz_questions = all_questions
            st.experimental_rerun()
    else:
        # الخطوة 2: عرض الاختبار
        st.markdown(f"<div class='description'>الامتحان: {st.session_state.selected_exam}</div>", unsafe_allow_html=True)
        
        progress = int((st.session_state.question_index / len(st.session_state.quiz_questions)) * 100)
        st.progress(progress)
        
        if st.session_state.question_index < len(st.session_state.quiz_questions):
            current_index = st.session_state.question_index
            current_question = st.session_state.quiz_questions[current_index]
            st.markdown(f"<div class='question-heading'>السؤال {current_index + 1} من {len(st.session_state.quiz_questions)}</div>", unsafe_allow_html=True)
            st.write(current_question["question"])
            
            st.write("اختر الإجابة:")
            for idx, option in enumerate(current_question["options"]):
                if st.button(option, key=f"option_{current_index}_{idx}"):
                    st.session_state.selected_answer = option
                    st.experimental_rerun()
            
            if st.session_state.selected_answer:
                st.markdown(
                    f"<div style='font-size:1.2rem; color:#003B70; margin-top:1rem;'><strong>الإجابة المختارة:</strong> {st.session_state.selected_answer}</div>", 
                    unsafe_allow_html=True
                )
            
            if st.button("التالي", key="next_button"):
                if not st.session_state.selected_answer:
                    st.warning("يرجى اختيار إجابة قبل المتابعة.")
                else:
                    st.session_state.user_answers[current_question["id"]] = st.session_state.selected_answer
                    st.session_state.selected_answer = None
                    st.session_state.question_index += 1
                    st.experimental_rerun()
        else:
            st.success("اكتمل الاختبار!")
            if st.button("عرض التقرير"):
                # جمع الأسئلة التي تمت الإجابة عليها بشكل خاطئ فقط
                mistakes = []
                for q in st.session_state.quiz_questions:
                    if q["id"] in st.session_state.user_answers:
                        user_ans = st.session_state.user_answers[q["id"]]
                        correct_ans = q.get("correct_answer", "غير محددة")
                        if user_ans != correct_ans:
                            mistakes.append({
                                "question": q["question"],
                                "selected_answer": user_ans,
                                "correct_answer": correct_ans
                            })
                
                analysis = get_analysis(mistakes)
                st.markdown("<div class='report-container'>", unsafe_allow_html=True)
                st.header("التحليل والتوصيات (للأسئلة الخاطئة)")
                st.write(analysis)
                st.markdown("</div>", unsafe_allow_html=True)
                st.session_state.report_shown = True
            
            if st.session_state.report_shown:
                st.markdown("<div class='feedback-container'>", unsafe_allow_html=True)
                st.header("استبيان التغذية الراجعة")
                survey_options = ["أوافق بشدة", "موافق", "محايد", "لا أوافق", "لا أوافق أبداً"]
                s1 = st.radio("1. هل وجدت الاختبار مفيداً؟", options=survey_options, key="survey_q1")
                s2 = st.radio("2. هل كانت أسئلة الاختبار واضحة؟", options=survey_options, key="survey_q2")
                s3 = st.radio("3. هل كان التقرير مفيداً لتحسين مهاراتك؟", options=survey_options, key="survey_q3")
                open_feedback = st.text_area("يرجى تقديم ملاحظاتك واقتراحاتك", key="open_feedback")
                
                if st.button("إرسال التغذية الراجعة", key="submit_feedback"):
                    st.success("شكراً لتعليقاتك!")
                # طلب الإيميل لحفظه وإرسال الروابط
                user_email = st.text_input("أدخل بريدك الإلكتروني للحصول على روابط الدورات المقترحة والمذكرات وكوبون الخصم", key="user_email")
                if st.button("حفظ البريد الإلكتروني"):
                    # هنا يمكنك إضافة منطق إرسال الإيميل أو حفظه في قاعدة بيانات
                    st.success(f"تم حفظ بريدك الإلكتروني: {user_email}")
                    st.session_state.email_saved = True
                
                if st.button("إعادة الاختبار"):
                    st.session_state.clear()
                    st.experimental_rerun()
                st.markdown("</div>", unsafe_allow_html=True)
