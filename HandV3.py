import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
import openai
# from utils import OPENAI_API_KEY
# openai.api_key = OPENAI_API_KEY
# Configure Matplotlib for Right-to-Left text support
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False
openai.api_key = st.secrets["openai"]["api_key"]

# Load Data
questions_df = pd.read_csv("questions_dict.csv")
activities_df = pd.read_csv("activities.csv")
subjects_df = pd.read_csv("subject_category_mapping.csv")

# English mapping for categories
category_english_mapping = {
    "واقعي": "Realistic",
    "تحليلي": "Investigative",
    "فني": "Artistic",
    "اجتماعي": "Social",
    "ريادي": "Enterprising",
    "تقليدي": "Conventional"
}

# App Config
st.set_page_config(page_title="اختبار الشخصية", layout="wide", initial_sidebar_state="expanded")
st.title("اختبار تحديد الشخصية")
st.markdown("<style>body { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)

# Initialize session state
if "scores" not in st.session_state:
    st.session_state.scores = {"واقعي": 0, "تحليلي": 0, "فني": 0, "اجتماعي": 0, "ريادي": 0, "تقليدي": 0}
if "step" not in st.session_state:
    st.session_state.step = 1
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "questions" not in st.session_state:
    st.session_state.questions = None
if "selected_activities" not in st.session_state:
    st.session_state.selected_activities = []
if "selected_subjects" not in st.session_state:
    st.session_state.selected_subjects = []
if "sampled_activities" not in st.session_state:
    st.session_state.sampled_activities = None

# Helper Functions
def get_random_questions(df, n=10):
    return df.groupby("Category").apply(lambda x: x.sample(n=min(n, len(x)))).reset_index(drop=True)

def update_scores_from_response(category, response):
    if response == "أوافق بشدة":
        st.session_state.scores[category] += 4
    elif response == "أوافق":
        st.session_state.scores[category] += 3
    elif response == "غير متأكد":
        st.session_state.scores[category] += 2
    elif response == "لا أوافق":
        st.session_state.scores[category] += 1

def get_activities_sample(df, n_per_category=2):
    return df.groupby("Category").apply(lambda x: x.sample(n=min(n_per_category, len(x)))).reset_index(drop=True)

# Step 1: Questions
if st.session_state.step == 1:
    st.header("الجزء الأول: الأسئلة")

    if st.session_state.questions is None:
        st.session_state.questions = get_random_questions(questions_df, 10)

    questions = st.session_state.questions
    total_questions = len(questions)
    current_index = st.session_state.question_index

    if current_index < total_questions:
        current_q = questions.iloc[current_index]
        st.markdown(f"""
        <div style="background-color:#f9f9f9; padding:20px; border-radius:10px; margin-bottom:20px;">
            <h3 style="text-align:center; font-size:20px; color:#555;">السؤال {current_index + 1} من {total_questions}</h3>
            <h2 style="text-align:center; font-size:24px; color:#333;">{current_q["Question"]}</h2>
        </div>
        """, unsafe_allow_html=True)
        temp_response = st.radio("اختر إجابتك:", [
            "لا أوافق بشدة", "لا أوافق", "غير متأكد", "أوافق", "أوافق بشدة"
        ], key=f"temp_response_{current_index}", index=0)

        if st.button("التالي", key=f"next_{current_index}"):
            st.session_state[f"response_{current_index}"] = temp_response  # حفظ الإجابة
            update_scores_from_response(current_q["Category"], temp_response)
            st.session_state.question_index += 1
            st.experimental_rerun()
    else:
        st.session_state.step = 2

# Step 2: Activities
if st.session_state.step == 2:
    st.header("الجزء الثاني: الأنشطة")
    st.write("يرجى اختيار الأنشطة التي تفضلها من الخيارات التالية:")

    if st.session_state.sampled_activities is None:
        st.session_state.sampled_activities = get_activities_sample(activities_df, n_per_category=2)

    sampled_activities = st.session_state.sampled_activities

    cols = st.columns(3)
    for i, (_, row) in enumerate(sampled_activities.iterrows()):
        with cols[i % 3]:
            if st.checkbox(row["Activity"], key=f"activity_{i}"):
                if row["Activity"] not in st.session_state.selected_activities:
                    st.session_state.selected_activities.append(row["Activity"])
                    category = row["Category"]
                    st.session_state.scores[category] += 1

    if st.button("التالي"):
        if st.session_state.selected_activities:
            st.session_state.step = 3
            st.experimental_rerun()
        else:
            st.error("يرجى اختيار نشاط واحد على الأقل قبل المتابعة.")

# Step 3: Subjects
if st.session_state.step == 3:
    st.header("الجزء الثالث: المواد الدراسية")
    st.write("يرجى اختيار المواد التي تفضلها:")

    selected_subject_checkboxes = []
    for _, row in subjects_df.iterrows():
        selected_subject_checkboxes.append(
            st.checkbox(row["Subject"], key=f"subject_{row.name}")
        )

    if st.button("عرض النتيجة"):
        for idx, selected in enumerate(selected_subject_checkboxes):
            if selected:
                subject = subjects_df.iloc[idx]["Subject"]
                if subject not in st.session_state.selected_subjects:
                    st.session_state.selected_subjects.append(subject)
                    category = subjects_df.iloc[idx]["Category"]
                    st.session_state.scores[category] += 1
        st.session_state.step = 4
        st.experimental_rerun()

# Step 4: Results
if st.session_state.step == 4:
    st.header("النتيجة النهائية")

    # Calculate percentages
    total_score = sum(st.session_state.scores.values())
    percentages = {category: (score / total_score) * 100 for category, score in st.session_state.scores.items()}

    # Map categories to English
    percentages_english = {category_english_mapping[cat]: val for cat, val in percentages.items()}

    # Configure the Horizontal Bar Chart
    fig, ax = plt.subplots()
    ax.barh(list(percentages_english.keys()), list(percentages_english.values()), color='skyblue')
    ax.set_title("Distribution of Scores by Personality", fontsize=16, horizontalalignment='center')
    ax.set_xlabel("Percentage", fontsize=14, horizontalalignment='center')
    ax.set_ylabel("Personality Types", fontsize=14, horizontalalignment='center')
    ax.invert_yaxis()  # Reverse the order of categories

    # Add percentage labels
    for i, v in enumerate(list(percentages_english.values())):
        ax.text(v, i, f"{v:.2f}%", color='blue', va='center', ha='left')

    st.pyplot(fig)

    # Display personality code
    sorted_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
    top_two = sorted_scores[:2]
    code = f"{category_english_mapping[top_two[0][0]][0]}{category_english_mapping[top_two[1][0]][0]}"
    st.subheader(f"Personality Code: {code}")

    # # Interpretation
    # if st.button("تفسير النتيجة"):
    #     st.write("### تفسير نتيجتك:")
    #     for category, _ in top_two:
    #         with st.expander(f"**{category}**:"):
    #             st.markdown("#### - الأسئلة المؤثرة:")
    #             for idx, row in st.session_state.questions.iterrows():
    #                 response = st.session_state.get(f"response_{idx}")
    #                 if row["Category"] == category and response in ["أوافق", "أوافق بشدة"]:
    #                     st.write(f"- {row['Question']}")

    #             st.markdown("#### - الأنشطة التي اخترتها:")
    #             for activity in st.session_state.selected_activities:
    #                 activity_category = activities_df[activities_df["Activity"] == activity]["Category"].values[0]
    #                 if activity_category == category:
    #                     st.write(f"- {activity}")

    #             st.markdown("#### - المواد التي اخترتها:")
    #             for subject in st.session_state.selected_subjects:
    #                 subject_category = subjects_df[subjects_df["Subject"] == subject]["Category"].values[0]
    #                 if subject_category == category:
    #                     st.write(f"- {subject}")

    # Academic and Career Guidance
    if st.button("عرض الإرشاد الأكاديمي والمهني"):
        personality_code = code
        selected_questions = [
            row["Question"]
            for idx, row in st.session_state.questions.iterrows()
            if st.session_state.get(f"response_{idx}") in ["أوافق", "أوافق بشدة"]
        ]
        selected_activities = st.session_state.selected_activities
        selected_subjects = st.session_state.selected_subjects

        # Prompt for ChatGPT
        prompt = f"""
        الطالب حصل على الكود الشخصي: {personality_code}.
        - الأسئلة التي أجاب عليها بـ "أوافق" أو "أوافق بشدة":
        {', '.join(selected_questions)}

        - الأنشطة التي اختارها:
        {', '.join(selected_activities)}

        - المواد الدراسية التي اختارها:
        {', '.join(selected_subjects)}

        قدم نصيحة أكاديمية ومهنية للطالب، تشمل:
1. الدورات الاحترافية التي يستحين ان الطالب يأخذها    
            2. نصائح للنجاح في هذه المجالات.
       حاول الاجابة لاتتعدي 500 توكنز 
    
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Replace with the exact model name if different
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        # Extract the answer from the response object
        answer = response.choices[0].message['content'].strip()

        st.info(answer)

        
