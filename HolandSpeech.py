import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px

# Set Streamlit page config
st.set_page_config(page_title="Holland Code Assessment", page_icon="🎨", layout="wide")

# Define custom CSS for background color and font styling
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #eef2f3, #8e9eab);
        font-family: 'Segoe UI', sans-serif;
    }
    .stSlider > div {
        font-size: 18px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        border-radius: 5px;
    }
    .card {
        background-color: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define the personality questions
questions = {
    "Openness": [
        "I enjoy exploring new ideas and concepts.",
        "I often seek out creative or imaginative activities.",
        "I am curious about new and unconventional experiences.",
        "I value creativity and innovation in my work.",
    ],
    "Conscientiousness": [
        "I prefer tasks that are well-organized and follow clear rules.",
        "I enjoy working on projects that require attention to detail.",
        "I like setting goals and achieving them through structured plans.",
        "I take pride in completing tasks on time and with precision.",
    ],
    "Extraversion": [
        "I enjoy meeting and interacting with new people.",
        "I feel energized when leading a group discussion or project.",
        "I find social gatherings exciting and fun.",
        "I enjoy working in environments with a lot of collaboration.",
    ],
    "Agreeableness": [
        "I like helping others solve their problems.",
        "I prefer collaborative work over competitive environments.",
        "I find satisfaction in supporting others' success.",
        "I enjoy resolving conflicts and fostering harmony in groups.",
    ],
    "Neuroticism": [
        "I often feel stressed or anxious in challenging situations.",
        "I frequently worry about future events.",
        "I am sensitive to criticism and emotional feedback.",
        "I find it hard to stay calm under pressure.",
    ],
}

# Define RIASEC mapping based on traits
riasec_mapping = {
    "Openness": ["Artistic", "Investigative"],
    "Conscientiousness": ["Conventional", "Realistic"],
    "Extraversion": ["Social", "Enterprising"],
    "Agreeableness": ["Social", "Conventional"],
    "Neuroticism": ["None"],  # No direct mapping, but it can influence results
}

# Function to calculate Holland Code scores
def calculate_holland_code(scores):
    riasec_scores = {"Realistic": 0, "Investigative": 0, "Artistic": 0, "Social": 0, "Enterprising": 0, "Conventional": 0}
    
    for trait, value in scores.items():
        for code in riasec_mapping.get(trait, []):
            if code != "None":
                riasec_scores[code] += value

    return riasec_scores

# Visualize the Holland Code scores (Interactive)
def plot_riasec_scores_radar(riasec_scores):
    categories = list(riasec_scores.keys())
    values = list(riasec_scores.values())
    values += values[:1]  # Close the radar chart

    fig = px.line_polar(
        r=values, theta=categories + [categories[0]],
        line_close=True, title="RIASEC Theme Radar Chart",
        labels={"r": "Scores", "theta": "RIASEC Themes"}
    )
    fig.update_traces(fill="toself")
    st.plotly_chart(fig)

# Streamlit App
st.title("Holland Code Assessment App")
st.header("Discover your Holland Code and Career Recommendations")

# Progress bar
progress = 0
progress_bar = st.progress(progress)

# Store scores for each trait
trait_scores = {}

# Display questions and collect responses
for trait, qs in questions.items():
    st.subheader(trait)
    with st.expander(f"Answer questions for {trait}"):
        total_score = 0
        for q in qs:
            st.markdown(f"<div class='card'>{q}</div>", unsafe_allow_html=True)
            score = st.slider("", min_value=1, max_value=5, step=1, key=f"{trait}-{q}")
            total_score += score
        trait_scores[trait] = total_score / len(qs)  # Average score
        progress += int(100 / len(questions))
        progress_bar.progress(progress)

st.write("---")

# Calculate Holland Code scores if user clicks the button
if st.button("Get My Holland Code"):
    # Normalize scores to a scale of 0-1
    scaler = MinMaxScaler()
    traits_array = np.array(list(trait_scores.values())).reshape(-1, 1)
    normalized_scores = scaler.fit_transform(traits_array).flatten()

    # Map normalized scores back to traits
    normalized_trait_scores = dict(zip(trait_scores.keys(), normalized_scores))

    # Calculate RIASEC scores
    riasec_scores = calculate_holland_code(normalized_trait_scores)

    # Display results
    st.subheader("Your Holland Code Results")
    st.write(riasec_scores)

    # Plot RIASEC scores
    plot_riasec_scores_radar(riasec_scores)

    # Recommend careers based on top themes
    top_themes = sorted(riasec_scores, key=riasec_scores.get, reverse=True)[:2]
    st.subheader("Recommended Career Areas")
    if "Artistic" in top_themes:
        st.write("Consider careers in art, design, or creative writing.")
    if "Investigative" in top_themes:
        st.write("Explore fields like science, research, or data analysis.")
    if "Social" in top_themes:
        st.write("Look into teaching, counseling, or social work.")
    if "Enterprising" in top_themes:
        st.write("Consider careers in business, sales, or leadership roles.")
    if "Conventional" in top_themes:
        st.write("Explore opportunities in accounting, administration, or logistics.")
    if "Realistic" in top_themes:
        st.write("Look into engineering, skilled trades, or outdoor careers.")
