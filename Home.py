import streamlit as st
import os

# Arabic titles and instructions
st.title("تحديد التخصص")
st.write("اختر الطريقة التي تفضلها لتحديد التخصص الخاص بك:")

# Buttons for modes
mode = st.radio(
    "اختر الوضع:",
    ("عن طريق الأسئلة", "عن طريق الصوت"),
    index=0
)

# Run the appropriate page based on the user's choice
if st.button("ابدأ"):
    if mode == "عن طريق الأسئلة":
        st.write("جاري فتح وضع الأسئلة...")
        os.system("streamlit run mainAR.py")
    elif mode == "عن طريق الصوت":
        st.write("جاري فتح وضع الصوت...")
        os.system("streamlit run Sound_AR.py")
