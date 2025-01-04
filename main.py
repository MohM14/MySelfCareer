import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

# Define the expanded questions dictionary with 10 questions per category
questions_dict = {
    "Realistic": [
        "Do you enjoy working with tools or machines?",
        "Do you like fixing or building things?",
        "Do you enjoy outdoor work or physical activity?",
        "Do you like working with your hands?",
        "Do you enjoy operating heavy equipment or machinery?",
        "Do you like solving physical or mechanical problems?",
        "Do you enjoy working with plants, animals, or natural resources?",
        "Do you like performing outdoor repairs or maintenance?",
        "Do you enjoy using manual tools for construction or repair?",
        "Do you like exploring nature or the outdoors?",
    ],
    "Investigative": [
        "Do you like solving puzzles or conducting research?",
        "Do you enjoy analyzing problems or experiments?",
        "Are you curious about how things work?",
        "Do you enjoy using science or math to solve problems?",
        "Do you like investigating facts or theories?",
        "Do you enjoy reading about scientific discoveries?",
        "Do you like experimenting with new ideas?",
        "Do you enjoy studying or observing natural phenomena?",
        "Do you like using logical thinking to find solutions?",
        "Do you enjoy problem-solving in technical fields?",
    ],
    "Artistic": [
        "Do you enjoy creating art, music, or writing?",
        "Do you prefer unstructured, creative activities?",
        "Do you enjoy expressing yourself through design or storytelling?",
        "Do you like working on creative projects?",
        "Do you enjoy drawing, painting, or sculpting?",
        "Do you like playing a musical instrument or singing?",
        "Do you enjoy writing poetry, stories, or scripts?",
        "Do you like performing in plays or musicals?",
        "Do you enjoy taking photographs or making videos?",
        "Do you like designing or decorating spaces?",
    ],
    "Social": [
        "Do you like helping others or teaching?",
        "Do you enjoy working with people in a team?",
        "Do you like resolving conflicts or supporting others?",
        "Do you enjoy providing advice or guidance?",
        "Do you like volunteering or helping in your community?",
        "Do you enjoy working in health or social services?",
        "Do you like teaching others new skills?",
        "Do you enjoy mentoring or coaching others?",
        "Do you like interacting with people in a meaningful way?",
        "Do you enjoy working in roles that involve empathy and communication?",
    ],
    "Enterprising": [
        "Do you enjoy leading or persuading others?",
        "Do you like setting goals and taking risks to achieve them?",
        "Do you enjoy selling ideas or products?",
        "Do you like managing projects or people?",
        "Do you enjoy making decisions and taking responsibility?",
        "Do you like negotiating or influencing others?",
        "Do you enjoy brainstorming and implementing new ideas?",
        "Do you like public speaking or presenting?",
        "Do you enjoy running a business or starting new ventures?",
        "Do you like competing to achieve success?",
    ],
    "Conventional": [
        "Do you like organizing files or working with data?",
        "Do you enjoy following established procedures?",
        "Do you prefer structured, detail-oriented tasks?",
        "Do you like maintaining records or databases?",
        "Do you enjoy working in administrative or clerical roles?",
        "Do you like managing schedules or calendars?",
        "Do you enjoy tasks that require accuracy and precision?",
        "Do you like categorizing or organizing information?",
        "Do you enjoy working with spreadsheets or financial documents?",
        "Do you like preparing reports or presentations?",
    ],
}

# Initialize session state for selected questions
if "selected_questions" not in st.session_state:
    st.session_state.selected_questions = []
    for category, questions in questions_dict.items():
        selected_questions = random.sample(questions, 3)  # Select 3 random questions per category
        for question in selected_questions:
            st.session_state.selected_questions.append({"question": question, "category": category})

# Shuffle the selected questions only once
if "shuffled_questions" not in st.session_state:
    st.session_state.shuffled_questions = random.sample(st.session_state.selected_questions, len(st.session_state.selected_questions))

# Career database
career_database = {
    "RIA": ["Engineer", "Mechanic", "Electrician"],
    "ISE": ["Scientist", "Biologist", "Data Analyst"],
    "AES": ["Artist", "Musician", "Writer"],
    "SEC": ["Teacher", "Counselor", "Nurse"],
    "ECR": ["Manager", "Salesperson", "Entrepreneur"],
    "CRI": ["Accountant", "Auditor", "Administrative Assistant"],
}

# Initialize other session states
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "scores" not in st.session_state:
    st.session_state.scores = {"Realistic": 0, "Investigative": 0, "Artistic": 0, "Social": 0, "Enterprising": 0, "Conventional": 0}
if "answers" not in st.session_state:
    st.session_state.answers = []

# Add styles for the card
def render_card(question, response=None):
    st.markdown(
        f"""
        <div style="background-color: #f4f4f9; 
                    border: 2px solid #ccccff; 
                    padding: 20px; 
                    margin: 10px 0; 
                    border-radius: 8px;">
            <h4 style="color: #3333cc;">{question}</h4>
            <p><b>Answer:</b> {response if response else "Not answered yet"}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Main logic
if st.session_state.current_question < len(st.session_state.shuffled_questions):
    # Render previous questions as cards
    for i, ans in enumerate(st.session_state.answers):
        render_card(f"Question {i + 1} of {len(st.session_state.shuffled_questions)}: {st.session_state.shuffled_questions[i]['question']}", ans)

    # Render current question
    current_q_index = st.session_state.current_question
    current_q = st.session_state.shuffled_questions[current_q_index]
    st.write(f"### Question {current_q_index + 1} of {len(st.session_state.shuffled_questions)}")
    render_card(current_q["question"])

    # Answer options
    response = st.radio("Select your answer:", options=["", "Yes", "No"], key=f"q_{current_q_index}")

    # "Next" button
    if st.button("Next"):
        if response:
            # Record the response
            st.session_state.answers.append(response)
            if response == "Yes":
                st.session_state.scores[current_q["category"]] += 1

            # Move to the next question
            st.session_state.current_question += 1

            # Immediately refresh the page to avoid double click
            st.experimental_rerun()
        else:
            st.warning("Please select an answer before proceeding.")
else:
    # Show results
    st.write("### All questions completed!")
    st.write("### Your Holland Code Personality Results")

    # Sort scores to determine the dominant personality types
    sorted_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
    top_categories = sorted_scores[:3]

    # Handle case where all scores are zero
    if all(score == 0 for _, score in sorted_scores):
        st.write("It seems you answered 'No' to all questions.")
        st.write("Based on your responses, we could not determine a strong personality match.")
        st.write("Consider answering 'Yes' to questions that resonate with you.")
    else:
        holland_code = "".join([x[0][0] for x in top_categories])
        highest_score = sorted_scores[0][1]
        best_categories = [cat for cat, score in sorted_scores if score == highest_score]

        st.write(f"**Your Holland Code is:** `{holland_code}`")
        st.write(f"**Best Category:** {', '.join(best_categories)} ({highest_score} points)")

        # Match careers based on Holland Code
        if holland_code in career_database:
            st.write("### Career Matches:")
            st.write(", ".join(career_database[holland_code]))
        else:
            st.write("No exact career matches found. Try exploring careers that fit your top categories!")

    # Visualize scores with progress bars
    st.write("### Category Scores:")
    max_score = 3
    for category, score in st.session_state.scores.items():
        st.write(f"**{category}: {score}/{max_score}**")
        st.progress(score / max_score)

    # Visualize scores with a pie chart
    st.write("### Score Distribution:")
    if all(score == 0 for score in st.session_state.scores.values()):
        st.write("No scores to display in the distribution chart. All categories scored zero.")
    else:
        fig, ax = plt.subplots()
        ax.pie(
            st.session_state.scores.values(),
            labels=st.session_state.scores.keys(),
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.
        st.pyplot(fig)

    # Prepare results for download
    results_df = pd.DataFrame(list(st.session_state.scores.items()), columns=["Category", "Score"])
    results_csv = results_df.to_csv(index=False)

    # Download button
    st.download_button(
        label="Download Your Results",
        data=results_csv,
        file_name="holland_code_results.csv",
        mime="text/csv",
    )

    # Restart button
    if st.button("Restart"):
        del st.session_state["selected_questions"]
        del st.session_state["shuffled_questions"]
        del st.session_state["current_question"]
        del st.session_state["scores"]
        del st.session_state["answers"]
        st.experimental_rerun()
