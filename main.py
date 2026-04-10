import streamlit as st
import PyPDF2
import os
import io
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="AI Resume Critiquer", page_icon="📄", layout="centered")

st.title("AI Resume Critiquer")
st.markdown("Upload your resume in PDF format, and the AI will provide feedback to help you improve it.")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)  ", type=["pdf","txt"])

job_role = st.text_input("Enter the job role you are applying for (optional)")

analyze_button = st.button("Analyze Resume")

def extract_text_from_pdf(file):
    Pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in Pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return  uploaded_file.read().decode("utf-8")

if analyze_button and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("The uploaded file is empty. Please upload a valid resume.")
            st.stop()

        prompt = f"""Please critique the resume and provide constructive feedback.
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience description
        4. Specific improvements for {job_role if job_role else 'general job applications'}.

        Resume content:"
        {file_content}

        Please provide your analysis in a clear, structured format with specific recommendations."""
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are an expert career coach providing feedback on resumes."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500)
        st.markdown("### AI Feedback:")
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"An error occurred while processing the resume: {str(e)}")       