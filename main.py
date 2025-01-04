import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Define the questions and categories
questions = [
    {"question": "Do you enjoy working with tools or machines?", "category": "Realistic"},
    {"question": "Do you like fixing or building things?", "category": "Realistic"},
    {"question": "Do you enjoy outdoor work or physical activity?", "category": "Realistic"},
    {"question": "Do you like solving puzzles or conducting research?", "category": "Investigative"},
    {"question": "Do you enjoy analyzing problems or experiments?", "category": "Investigative"},
    {"question": "Are you curious about how things work?", "category": "Investigative"},
    {"question": "Do you enjoy creating art, music, or writing?", "category": "Artistic"},
    {"question": "Do you prefer unstructured, creative activities?", "category": "Artistic"},
    {"question": "Do you enjoy expressing yourself through design or storytelling?", "category": "Artistic"},
    {"question": "Do you like helping others or teaching?", "category": "Social"},
    {"question": "Do you enjoy working with people in a team?", "category": "Social"},
    {"question": "Do you like resolving conflicts or supporting others?", "category": "Social"},
    {"question": "Do you enjoy leading or persuading others?", "category": "Enterprising"},
    {"question": "Do you like setting goals and taking risks to achieve them?", "category": "Enterprising"},
    {"question": "Do you enjoy selling ideas or products?", "category": "Enterprising"},
    {"question": "Do you like organizing files or working with data?", "category": "Conventional"},
    {"question": "Do you enjoy following established procedures?", "category": "Conventional"},
    {"question": "Do you prefer structured, detail-oriented tasks?", "category": "Conventional"},
]

# Career database
career_database = {
    "RIA": ["Engineer", "Mechanic", "Electrician"],
    "ISE": ["Scientist", "Biologist", "Data Analyst"],
    "AES": ["Artist", "Musician", "Writer"],
    "SEC": ["Teacher", "Counselor", "Nurse"],
    "ECR": ["Manager", "Salesperson", "Entrepreneur"],
    "CRI": ["Accountant", "Auditor", "Administrative Assistant"],
}

# Initialize session state
if "current_question" not in st.session_state:
    st.session_state.current_question = 0  # Start with the first question
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
if st.session_state.current_question < len(questions):
    # Render previous questions as cards
    for i, ans in enumerate(st.session_state.answers):
        render_card(f"Question {i + 1} of {len(questions)}: {questions[i]['question']}", ans)

    # Render current question
    current_q_index = st.session_state.current_question
    current_q = questions[current_q_index]
    st.write(f"### Question {current_q_index + 1} of {len(questions)}")
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
    top_categories = sorted_scores[:3]  # Get the top 3 categories
    holland_code = "".join([x[0][0] for x in top_categories])  # Generate Holland Code from initials

    # Highlight the best category (or categories in case of a tie)
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

    # Visualize scores with progress bars (showing category names and scores)
    st.write("### Category Scores:")
    max_score = len([q for q in questions if q["category"] in st.session_state.scores])  # Max possible score per category
    for category, score in st.session_state.scores.items():
        st.write(f"**{category}: {score}/{max_score}**")
        st.progress(score / max_score)  # Normalize progress to the maximum score

    # Visualize scores with a pie chart
    st.write("### Score Distribution:")
    fig, ax = plt.subplots()
    ax.pie(st.session_state.scores.values(), labels=st.session_state.scores.keys(), autopct="%1.1f%%", startangle=90)
    ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.
    st.pyplot(fig)

    # Prepare results for download
    results_df = pd.DataFrame(list(st.session_state.scores.items()), columns=["Category", "Score"])
    results_df.loc[len(results_df)] = ["Holland Code", holland_code]  # Add Holland Code as a row
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
        del st.session_state["current_question"]
        del st.session_state["scores"]
        del st.session_state["answers"]
        st.experimental_rerun()
