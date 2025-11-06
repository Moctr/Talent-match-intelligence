import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
from supabase import create_client

# Inject custom CSS for UI enhancements
st.markdown("""
    <style>
    /* Global app background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }

    /* Sidebar style */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
    }

    /* Headings */
    h1, h2, h3 {
        color: #60a5fa !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
    }

    /* Section headers */
    .stHeader, .stSubheader {
        color: #93c5fd !important;
    }

    /* Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        padding: 0.6em 1.2em;
        transition: all 0.3s ease;
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #1d4ed8, #2563eb);
        transform: scale(1.03);
    }

    /* Inputs and selectboxes */
    .stTextInput, .stSelectbox, .stMultiSelect {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #facc15 !important;
    }

    /* Info / Warning / Error boxes */
    .stAlert {
        border-radius: 10px;
        border: 1px solid #3b82f6;
        background-color: rgba(37, 99, 235, 0.1);
    }

    /* DataFrame styling */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        background-color: #0f172a !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background-color: #3b82f6;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize clients
client_supabase = create_client(
    "https://ridvicextkltazrhmsql.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpZHZpY2V4dGtsdGF6cmhtc3FsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMwMTg0NywiZXhwIjoyMDc2ODc3ODQ3fQ.exOpdEPjTGcxjMlJ_1HZKUeFuzKTFsHulmGkl8WgkPo"
)

# Initialize OpenAI with a placeholder - USER MUST REPLACE WITH THEIR OWN KEY
OPENAI_API_KEY = "ssk-proj-aVNhvlj9bUAgYf3vyNeVkNOfIt1vKiMt85BAAz0Up0bZFSkBJK6wX77a1gBwTEM7-mMkIjuJQ0T3BlbkFJA1Px1JKTb7vfcze1xDPB2csB2mTsoz2WMWzbK8QDxjLWUeFo1aOI3gHbTIEhzk7hDPYih6YnoA"  # ⚠️ REPLACE WITH ACTUAL KEY

def initialize_openai():
    """Initialize OpenAI client with the API key"""
    try:
        if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
            return OpenAI(api_key=OPENAI_API_KEY)
        else:
            return None
    except:
        return None

client_openai = initialize_openai()

def generate_ai_job_description(role_name, job_level, industry="Technology"):
    """Generate job description using OpenAI"""
    try:
        if not client_openai:
            return get_fallback_description(role_name, job_level)
        
        prompt = f"""
        Create a comprehensive, professional job description for a {job_level} {role_name} position in the {industry} industry.
        
        Please structure it with the following sections:
        
        **Job Summary**
        [Provide a compelling overview of the role and its impact]
        
        **Key Responsibilities**
        [List 5-7 main responsibilities with bullet points]
        
        **Required Qualifications** 
        [List essential qualifications and experience]
        
        **Preferred Skills**
        [List nice-to-have skills and experiences]
        
        **Key Competencies**
        [List 5-7 key competencies needed for success]
        
        **What We Offer**
        [Brief section about benefits and opportunities]
        
        Make it engaging, professional, and suitable for attracting top talent in the {industry} sector.
        """
        
        response = client_openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR professional and recruiter creating compelling job descriptions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return get_fallback_description(role_name, job_level)

def get_fallback_description(role_name, job_level):
    """Provide a professional fallback description when AI is unavailable"""
    return f"""
**{role_name} - {job_level} Position**

**Job Summary**
We are seeking a talented {job_level} {role_name} to join our dynamic team. This role offers an exciting opportunity to make significant impact and grow professionally in a collaborative environment.

**Key Responsibilities**
• Analyze and interpret complex data to drive business decisions
• Collaborate with cross-functional teams to understand requirements
• Develop and maintain reports, dashboards, and analytics solutions
• Identify trends, patterns, and insights from various data sources
• Present findings and recommendations to stakeholders

**Required Qualifications**
• Bachelor's degree in relevant field or equivalent experience
• {("1-3" if job_level == "Junior" else "3-5" if job_level == "Mid-Level" else "5+")} years of experience in {role_name} role
• Strong analytical and problem-solving skills
• Excellent communication and collaboration abilities

**Preferred Skills**
• Experience with data visualization tools
• Proficiency in SQL and data analysis
• Knowledge of statistical methods and analysis

**Key Competencies**
• Analytical Thinking
• Problem Solving
• Communication Skills
• Team Collaboration
• Attention to Detail

**What We Offer**
• Competitive compensation and benefits
• Professional development opportunities
• Collaborative and inclusive work environment
• Opportunities for career advancement
"""

def main():
    st.set_page_config(page_title="AI Talent Matcher", layout="wide")
    st.title("🚀 AI-Powered Talent Matching Dashboard")
    
    st.markdown("<hr style='border: 1px solid #3b82f6; margin: 1em 0;'>", unsafe_allow_html=True)
    
    # Input Section
    st.header("🎯 Job Requirements")
    col1, col2 = st.columns(2)
    
    with col1:
        role_name = st.text_input("Role Name", placeholder="e.g., Data Analyst, Software Engineer, Marketing Manager")
        job_level = st.selectbox("Job Level", ["Junior", "Mid-Level", "Senior", "Lead", "Executive"])
        industry = st.selectbox("Industry", ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Other"])
    
    with col2:
        use_ai = st.checkbox("✨ Generate Professional Job Description", value=True, 
                           help="Creates comprehensive job description using AI or professional templates")
        
        if st.button("🪄 Generate Job Description", type="secondary") and role_name and job_level:
            with st.spinner("💡 Creating professional job description..."):
                description = generate_ai_job_description(role_name, job_level, industry)
                role_purpose = st.text_area("Job Description", value=description, height=300)
        else:
            role_purpose = st.text_area("Job Description", 
                                      value=get_fallback_description(role_name, job_level) if role_name and job_level else "",
                                      height=300,
                                      placeholder="Enter job description or click 'Generate Job Description'")
    
    st.markdown("<hr style='border: 1px solid #3b82f6; margin: 1em 0;'>", unsafe_allow_html=True)

    # Benchmark Section
    st.header("🏆 Select Benchmark Employees")
    
    try:
        employees = client_supabase.table("emp_cognitive").select("employee_id").limit(200).execute()
        employee_ids = list(set([e['employee_id'] for e in employees.data]))
        
        selected_benchmarks = st.multiselect(
            "Choose high performers as benchmarks", 
            options=employee_ids,
            placeholder="Select employee IDs...",
            help="These employees will be used as the success benchmark for matching"
        )
        
        if selected_benchmarks:
            st.success(f"**Selected Benchmarks:** {', '.join(selected_benchmarks)}")
            
    except Exception as e:
        st.error(f"Error loading employees: {str(e)}")
        selected_benchmarks = []
    
    # Generate Matches Button
    if st.button("🚀 Generate Talent Matches", type="primary"):
        if not all([role_name, job_level, role_purpose, selected_benchmarks]):
            st.error("Please fill all required fields and select benchmark employees!")
            return
