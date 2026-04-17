import streamlit as st
import PyPDF2
import os
import io
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Custom CSS for modern UI
css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #333;
        margin: 0;
        padding: 0;
    }
    
    .stApp {
        background: transparent;
    }
    
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px 20px;
        text-align: center;
        border-radius: 0 0 20px 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .header p {
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .main-card {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 20px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 30px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102,126,234,0.4);
    }
    
    .stFileUploader {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 30px;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #f0f2ff 0%, #e0eaff 100%);
    }
    
    .stTextInput input {
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        padding: 12px 16px;
        font-size: 16px;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }
    
    .feedback-card {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
        padding: 30px;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin-top: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .feedback-card h3 {
        color: #667eea;
        margin-top: 0;
        font-size: 1.5rem;
    }
    
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        color: #666;
        font-size: 14px;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-card {
            padding: 20px;
            margin: 10px;
        }
        
        .header {
            padding: 30px 15px;
        }
        
        .header h1 {
            font-size: 2rem;
        }
    }
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ℹ️ About")
    st.markdown("This AI-powered tool analyzes your resume and provides constructive feedback to help you improve it.")
    st.markdown("---")
    st.markdown("**Features:**")
    st.markdown("- 📄 PDF & TXT support")
    st.markdown("- 🎯 Job-specific feedback")
    st.markdown("- 🤖 AI-powered analysis")
    st.markdown("- 📊 Structured suggestions")

# Header
st.markdown("""
<div class="header">
    <h1>📄 AI Resume Critiquer</h1>
    <p>Upload your resume and get intelligent feedback to enhance your job applications</p>
</div>
""", unsafe_allow_html=True)

# Main content in centered card
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 Choose your resume file (PDF or TXT)", 
        type=["pdf", "txt"],
        help="Upload a PDF or text file containing your resume"
    )
    
    job_role = st.text_input(
        "🎯 Job role (optional)", 
        placeholder="e.g., Software Engineer, Data Analyst...",
        help="Specify the job you're applying for to get tailored feedback"
    )
    
    analyze_button = st.button("🔍 Analyze Resume", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def extract_text_from_pdf(file):
    Pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in Pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")


if analyze_button and uploaded_file:
    try:
        with st.spinner("🔄 Analyzing your resume... Please wait."):
            file_content = extract_text_from_file(uploaded_file)

            if not file_content.strip():
                st.error("❌ The uploaded file appears to be empty. Please upload a valid resume.")
                st.stop()

            prompt = f"""
            Please critique the resume and provide constructive feedback.

            Focus on:
            1. Content clarity and impact
            2. Skills presentation
            3. Experience description
            4. Improvements for {job_role if job_role else 'general job applications'}

            Resume content:
            {file_content}

            Give structured, actionable suggestions.
            """

            # Gemini model
            model = genai.GenerativeModel("gemini-flash-latest")
            response = model.generate_content(prompt)

        # Display feedback in styled card
        st.markdown("""
        <div class="feedback-card">
            <h3>🤖 AI Feedback</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(response.text)

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("""
<div class="footer">
    <hr style="border: none; border-top: 1px solid #e1e5e9; margin-bottom: 15px;">
    Made with ❤️ using Streamlit and Google Gemini
</div>
""", unsafe_allow_html=True)