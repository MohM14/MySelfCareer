import streamlit as st
import json
import openai
openai.api_key = st.secrets["openai"]["api_key"]


# Inject custom CSS for right-to-left layout and enhanced styling
st.markdown(
    """
    <style>
    /* Set right-to-left direction for the entire page */
    body {
        direction: rtl;
    }
    /* Set a light background for the app */
    .main {
        background-color: #f0f2f6;
    }
    /* Style the title and description */
    .title {
        font-size: 2.5rem;
        color: #2E4053;
        font-weight: bold;
        text-align: center;
    }
    .description {
        font-size: 1.25rem;
        color: #34495E;
        text-align: center;
        margin-bottom: 2rem;
    }
    /* Increase font size for question headings */
    .question-heading {
        font-size: 2rem;
        color: #2E4053;
        margin-bottom: 1rem;
    }
    /* Style the answer option buttons with a blue background and white text */
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 1.2rem;
        margin: 0.25rem;
    }
    /* Style the Next button */
    .next-button > button {
        background-color: #1976D2;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1.2rem;
        margin-top: 1.5rem;
    }
    /* Increase overall font size for Markdown and alerts */
    .stMarkdown, .stText, .stAlert {
         font-size: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to load questions from a JSON file with UTF-8 encoding
def load_questions(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]

# Function to call the OpenAI API for analysis using ChatCompletion.
# The prompt now includes only the questions answered incorrectly.
def get_analysis(mistake_responses):
    prompt = "حلل الردود التالية التي تمت الإجابة عليها بشكل خاطئ لتحديد نقاط الضعف، واقترح الدورات المناسبة مع خطة دراسية.\n"
    for item in mistake_responses:
        prompt += (
            f"\nالفئة: {item['category']}\n"
            f"السؤال: {item['question']}\n"
            f"الإجابة المختارة: {item['selected_answer']}\n"
            f"الإجابة الصحيحة: {item['correct_answer']}\n"
        )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Replace with the exact model name if different
            messages=[
                {"role": "system", "content": "أنت مساعد مفيد."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        answer = response.choices[0].message['content'].strip()
    except Exception as e:
        answer = f"حدث خطأ في الاتصال بواجهة OpenAI: {e}"
    return answer

# Load questions from the JSON file
questions = load_questions("questions.json")

# Display the Arabic title and description
st.markdown('<div class="title">اختبار ذكي لاختبار معرفتك في الذكاء الاصطناعي</div>', unsafe_allow_html=True)
st.markdown('<div class="description">سيقوم النظام بتحليل نقاط ضعفك ثم يقترح عليك الدورة المناسبة من Elmway Academy مع خطة دراسية.</div>', unsafe_allow_html=True)

# Initialize session state variables if not already present
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None

# Get the current question based on session state index
current_index = st.session_state.question_index
current_question = questions[current_index]

# Display question numbering and text with enhanced font size
st.markdown(f'<div class="question-heading">السؤال {current_index + 1} من {len(questions)}</div>', unsafe_allow_html=True)
st.write(current_question["question"])

# Display answer options as individual buttons
st.write("اختر الإجابة:")
for option in current_question["options"]:
    if st.button(option, key=f"option_{current_index}_{option}"):
        st.session_state.selected_answer = option
        st.experimental_rerun()

# Display the currently selected answer if any
if st.session_state.selected_answer:
    st.markdown(
        f'<div style="font-size:1.2rem; color:#2E4053; margin-top:1rem;">'
        f'<strong>الإجابة المختارة:</strong> {st.session_state.selected_answer}</div>',
        unsafe_allow_html=True,
    )

# Next button logic
if st.button("التالي", key="next_button", help="انتقل للسؤال التالي"):
    if not st.session_state.selected_answer:
        st.warning("يرجى اختيار إجابة قبل المتابعة.")
    else:
        st.session_state.user_answers[current_question["id"]] = st.session_state.selected_answer
        st.session_state.selected_answer = None
        if current_index < len(questions) - 1:
            st.session_state.question_index += 1
            st.experimental_rerun()  # Rerun to display the next question
        else:
            st.success("اكتمل الاختبار، انتظر النتيجة!")
            # Build mistake responses for analysis (only questions answered incorrectly)
            mistake_responses = []
            for question in questions:
                if question["id"] in st.session_state.user_answers:
                    user_ans = st.session_state.user_answers[question["id"]]
                    if user_ans != question["correct_answer"]:
                        mistake_responses.append({
                            "question": question["question"],
                            "category": question["category"],
                            "selected_answer": user_ans,
                            "correct_answer": question["correct_answer"]
                        })
            if mistake_responses:
                analysis = get_analysis(mistake_responses)
                st.header("التحليل والتوصيات")
                st.write(analysis)
            else:
                st.success("أحسنت! لقد أجبت على جميع الأسئلة بشكل صحيح.")
