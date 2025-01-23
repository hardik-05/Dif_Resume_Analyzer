from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
from PyPDF2 import PdfReader
import google.generativeai as genai
import time

# Configure Gemini AI
#enai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key= r'AIzaSyC-T4haXA6ftapMGzvm3NbWFlhbjKWnngk')
class ATSAnalyzer:
    @staticmethod
    def get_gemini_response(input_prompt, pdf_text, job_description):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content([input_prompt, pdf_text, job_description])
            return response.text
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return None

    @staticmethod
    def extract_text_from_pdf(uploaded_file):
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error extracting PDF text: {str(e)}")
            return None

def main():
    # Page configuration
    st.set_page_config(
        page_title="Dif Resume Analyzer",
        page_icon="",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            background-color: #0066cc;
            color: white;
        }
        .stButton>button:hover {
            background-color: #0052a3;
        }
        .success-message {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #d4edda;
            color: #155724;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with professional description
    st.title("Dif Resume Analyzer")
    st.markdown("""
    """)

    # Create two columns for input
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            placeholder="Paste the complete job description here..."
        )

    with col2:
        st.subheader("Resume Upload")
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF format)",
            type=["pdf"],
            help="Please ensure your resume is in PDF format"
        )

        if uploaded_file:
            st.markdown('<p class="success-message">PDF uploaded successfully!</p>', unsafe_allow_html=True)

    # Analysis options
    if uploaded_file and job_description:
        st.subheader("🔍 Analysis Options")
        analysis_type = st.radio(
            "Choose analysis type:",
            ["JD Analysis","Resume Analysis", "Json Bin", "Json Report"]
            #["Detailed Resume Review", "Match Percentage Analysis", "JD Analysis","Resume Analysis"]
        )

        if st.button("Analyze Resume"):
            with st.spinner("Analyzing your resume... Please wait"):
                # Extract PDF text
                pdf_text = ATSAnalyzer.extract_text_from_pdf(uploaded_file)
                
                if pdf_text:
                    # Select prompt based on analysis type
                    if analysis_type == "Detailed Resume Review":
                        prompt = """
                        As an experienced Technical Human Resource Manager, provide a detailed professional evaluation 
                        of the candidate's resume against the job description. Please analyze:
                        1. Overall alignment with the role
                        2. Key strengths and qualifications that match
                        3. Notable gaps or areas for improvement
                        4. Specific recommendations for enhancing the resume
                        5. Final verdict on suitability for the role
                        
                        Format the response with clear headings and professional language.
                        """
                    elif analysis_type == "Resume Analysis":
                        prompt = """You are a highly intelligent and efficient resume analyzer. Your task is to process a provided resume and accurately extract key information into four distinct categories. Analyze the resume thoroughly and provide the extracted information in the following format:
                        Technical Skills: Extract specific technical skills, tools, programming languages, software, or methodologies mentioned in the resume. These should be skills that demonstrate technical expertise.
                        Domain Skills: Identify industry-specific knowledge or skills. These might include familiarity with particular business processes, sector expertise (e.g., finance, healthcare, manufacturing), or specialized certifications relevant to a domain.
                        Education: Extract all information related to the candidate's educational background, including degrees, certifications, institutions, years of study, and relevant coursework.
                        Achievements and Other Information: Identify professional accomplishments, awards, recognitions, volunteer work, hobbies, interests, and any other relevant information that does not fall into the above categories.
                        When extracting this information, maintain accuracy and organize the extracted data in a concise, structured manner. Ensure no important details are missed and avoid duplicating content across categories.
                        Output:
                        Technical Skills:
                        [List extracted skills]
                        Domain Skills:
                        [List extracted skills]
                        Education:
                        [List educational qualifications]
                        Achievements and Other Information:
                        [List achievements and additional information]
                        """
                    elif analysis_type == "JD Analysis":
                        prompt = """You are a highly efficient and intelligent job description analyzer. Your task is to process a provided job description (JD) and accurately extract key information into four distinct categories. Analyze the JD thoroughly and provide the extracted information in the following format:
                        Technical Skills: Extract specific technical skills, tools, programming languages, software, or methodologies mentioned in the job description. These should represent the technical expertise required for the role.
                        Domain Skills: Identify industry-specific knowledge or skills. These might include familiarity with particular business processes, sector expertise (e.g., finance, healthcare, manufacturing), or specialized certifications relevant to the role.
                        Education: Extract all information related to the educational qualifications required for the job, such as degrees, certifications, fields of study, or educational institutions.
                        Achievements and Other Information: Identify accomplishments, certifications, recognitions, or any additional information highlighted in the job description that does not fall into the above categories. Note: This category may remain empty if the job description does not include such details.
                        When extracting this information, maintain accuracy and organize the extracted data in a concise, structured manner. Ensure no important details are missed and avoid duplicating content across categories.
                        Output:
                        Technical Skills:
                        [List extracted skills]
                        Domain Skills:
                        [List extracted skills]
                        Education:
                        [List educational qualifications]
                        Achievements and Other Information:
                        [List achievements and additional information or state 'None' if empty] """
                    
                    elif analysis_type == "Json Bin":
                        prompt = """You are an advanced text processor. Your task is to analyze a given resume and job description (JD) and extract their content into four distinct bins for each. Organize the extracted data in a structured JSON format. Ensure the extraction is accurate and concise, avoiding duplicates.

                        Four Bins:

                        Technical Skills:

                        Extract all technical skills, tools, programming languages, software, or methodologies mentioned in the resume and JD.

                        Domain Skills:

                        Extract all industry-specific skills or knowledge relevant to the job (e.g., business processes, sector expertise, certifications).

                        Education:

                        Extract educational qualifications, degrees, certifications, fields of study, institutions, and years of study.

                        Achievements and Other Information:

                        Extract awards, recognitions, notable projects, volunteer work, hobbies, and any additional relevant information. This category may be empty if no such information exists.

                        Input Format:

                        Resume:
                        [Paste the resume text here]

                        Job Description (JD):
                        [Paste the job description text here]

                        Output Format:

                        Return the extracted bins in the following JSON structure:

                        {
                        "resume": {
                            "technical_skills": ["Skill 1", "Skill 2", ...],
                            "domain_skills": ["Skill 1", "Skill 2", ...],
                            "education": ["Qualification 1", "Qualification 2", ...],
                            "achievements_and_other_information": ["Achievement 1", "Achievement 2", ...]
                        },
                        "job_description": {
                            "technical_skills": ["Skill 1", "Skill 2", ...],
                            "domain_skills": ["Skill 1", "Skill 2", ...],
                            "education": ["Qualification 1", "Qualification 2", ...],
                            "achievements_and_other_information": ["Achievement 1", "Achievement 2", ...]
                        }
                        }

                        Guidelines:

                        Clearly identify and separate the content into the four bins.

                        Match similar elements between the resume and JD as closely as possible.

                        If any bin has no relevant information, return an empty array for that bin."""
                    elif analysis_type == "Json Report":
                        prompt = """You are an advanced text processor. Your task is to analyze a given resume and job description (JD) and extract their content into a detailed structured JSON format. The JSON should include four distinct bins for each (resume and JD), similarity scores, and further classification of technical skills within the JD. Ensure the extraction is accurate and concise, avoiding duplicates.

Four Bins:

Technical Skills:

Extract all technical skills, tools, programming languages, software, or methodologies mentioned in the resume and JD.

For the JD, split Technical Skills into two categories:

Primary Skills: Essential skills required for the job.

Split Primary Skills further into:

Non-negotiable Skills: Absolutely mandatory skills.

Negotiable Skills: Preferred but not mandatory skills.

Optional Skills: Skills that are nice to have but not critical.

Domain Skills:

Extract all industry-specific skills or knowledge relevant to the job (e.g., business processes, sector expertise, certifications).

Education:

Extract educational qualifications, degrees, certifications, fields of study, institutions, and years of study.

Achievements and Other Information:

Extract awards, recognitions, notable projects, volunteer work, hobbies, and any additional relevant information. This category may be empty if no such information exists.

Similarity Scores:

Calculate similarity scores for each of the following categories:

Technical Skills

Domain Skills

Education

Achievements and Other Information

Additionally, provide detailed similarity scores for the subcategories of technical skills in the JD:

Primary Skills

Non-negotiable Skills

Negotiable Skills

Optional Skills

Input Format:

Resume:
[Paste the resume text here]

Job Description (JD):
[Paste the job description text here]

Output Format:

Return the extracted bins and similarity scores in the following JSON structure:
{
  "resume": {
    "technical_skills": ["Skill 1", "Skill 2", ...],
    "domain_skills": ["Skill 1", "Skill 2", ...],
    "education": ["Qualification 1", "Qualification 2", ...],
    "achievements_and_other_information": ["Achievement 1", "Achievement 2", ...]
  },
  "job_description": {
    "technical_skills": {
      "primary_skills": {
        "non_negotiable_skills": ["Skill 1", "Skill 2", ...],
        "negotiable_skills": ["Skill 1", "Skill 2", ...]
      },
      "optional_skills": ["Skill 1", "Skill 2", ...]
    },
    "domain_skills": ["Skill 1", "Skill 2", ...],
    "education": ["Qualification 1", "Qualification 2", ...],
    "achievements_and_other_information": ["Achievement 1", "Achievement 2", ...]
  },
  "similarity_scores": {
    "technical_skills": ["Score"],
    "domain_skills": ["Score"],
    "education": ["Score"],
    "achievements_and_other_information": ["Score"],
    "detailed_technical_skills": {
      "primary_skills": ["Score"],
      "non_negotiable_skills": ["Score"],
      "negotiable_skills": ["Score"],
      "optional_skills": ["Score"]
    }
  }
}
Guidelines:

Clearly identify and separate the content into the four bins.

For the JD, ensure technical skills are further categorized as specified.

Match similar elements between the resume and JD as closely as possible.

If any bin has no relevant information, return an empty array for that bin.

Provide meaningful and well-justified similarity scores for each category and subcategory.

All the scores should be valid and double check all the scores
"""


                    else:
                        prompt = """
                        As an ATS (Applicant Tracking System) expert, provide:
                        1. Overall match percentage (%)
                        2. Key matching keywords found
                        3. Important missing keywords
                        4. Skills gap analysis
                        5. Specific recommendations for improvement
                        
                        Start with the percentage match prominently displayed.
                        """

                    # Get and display response
                    response = ATSAnalyzer.get_gemini_response(prompt, pdf_text, job_description)
                    
                    if response:
                        st.markdown("### Analysis Results")
                        st.markdown(response)
                        
                        # Add export option
                        st.download_button(
                            label="Export Analysis",
                            data=response,
                            file_name="resume_analysis.txt",
                            mime="text/plain"
                        )
    else:
        st.info("Please upload your resume and provide the job description to begin the analysis.")

    # Footer
    st.markdown("---")
    st.markdown(
        ""
        ""
    )

if __name__ == "__main__":
    main()