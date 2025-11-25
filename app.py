from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
from PIL import Image
import pdf2image
import google.generativeai as genai
import io       
import base64   # Necessary for encoding image data

# --- GLOBAL CONFIGURATION ---
# CRITICAL FIX: Define the exact path to the folder containing pdfinfo.exe, pdftocairo.exe, etc.
# This variable is now used in input_pdf_setup to resolve the PDFInfoNotInstalledError.
POPPLER_PATH = r'C:\Users\lenovo\Desktop\Release-25.11.0-0\poppler-25.11.0\Library\bin' 


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(input_prompt, pdf_content, job_description):
    # Consolidate the instructions and the job description into one text input
    full_prompt_text = f"{input_prompt}\n\nJob Description:\n{job_description}"
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    # The input list contains the text prompt and the image content
    response = model.generate_content([full_prompt_text, pdf_content[0]])
    return response.text


def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            # FIX IMPLEMENTED: Use poppler_path to point to the executables
            images = pdf2image.convert_from_bytes(
                uploaded_file.read(), 
                poppler_path=POPPLER_PATH 
            )
            
        except Exception as e:
            st.error(f"Error converting PDF. Please ensure Poppler is installed and configured correctly. Details: {e}")
            return None # Return None on failure
            
        first_page = images[0]

        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        # Added a graceful exit for missing file to avoid calling Streamlit error
        st.warning("Please upload a resume PDF file.")
        return None
    

### Streamlit App ###
st.set_page_config(page_title="Application Tracking System with Gemini Pro Vision", layout="wide")
st.header("Application Tracking System with Gemini Pro Vision 🤖")
input_text = st.text_area("Job Description:", key="input")
uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

if uploaded_file is not None:
    st.success("Resume Uploaded Successfully!")

# Reorganized button order for better flow
submit1=st.button("1. Evaluate Resume (HR Review)")
submit2=st.button("2. Percentage Match (ATS Score)")
submit3=st.button("3. How can I improve my skills?")

# --- PROMPT DEFINITIONS ---
input_prompt1="""You are an experienced HR With Tech Experience in the field of Data Science, Full stack Web development, Big Data Engineering, DEVOPS, and Data Analyst roles. Your task is to review the provided resume against the following Job Description.
Please share your professional evaluation on whether the candidate's profile aligns with the specified job requirements. Highlight the strengths and weaknesses of the applicant in relation to the specified job role.
"""

# ADDED PROMPT 2
input_prompt2="""Based on the provided resume and the Job Description, act as a career coach. Identify the key skills and keywords that are missing or weak in the resume compared to the job requirements. Provide a specific, actionable list of technical skills, tools, and projects the candidate should focus on to significantly improve their profile for this kind of role. Structure your advice clearly by topic (e.g., Programming, Cloud, Tools).
"""

input_prompt3="""You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of Data Science, Full stack Web development, Big Data Engineering, DEVOPS, Data Analyst and deep ATS functionality. Your task is to evaluate the resume against the following Job Description.
Give me the percentage match between the resume and the job description. First the output should come as percentage (e.g., 78%) and then a list of keywords missing in the resume compared to the job description."""


# --- LOGIC FLOW ---

# 1. HR Review (Submit 1)
if submit1:
    if uploaded_file is not None and input_text:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_prompt1, pdf_content, input_text)
            st.subheader("The HR Review is:")
            st.write(response)
    elif not input_text:
        st.warning("Please paste a Job Description before submitting.")
    else:
        st.warning("Please upload a resume PDF file.")

# 2. ATS Percentage Match (Submit 2)
elif submit2:
    if uploaded_file is not None and input_text:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_prompt3, pdf_content, input_text)
            st.subheader("ATS Percentage Match:")
            st.write(response)
    elif not input_text:
        st.warning("Please paste a Job Description before submitting.")
    else:
        st.warning("Please upload a resume PDF file.")

# 3. Skill Improvement (Submit 3)
elif submit3:
    if uploaded_file is not None and input_text:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_prompt2, pdf_content, input_text)
            st.subheader("Skill Improvement Recommendations:")
            st.write(response)
    elif not input_text:
        st.warning("Please paste a Job Description before submitting.")
    else:
        st.warning("Please upload a resume PDF file.")