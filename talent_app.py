import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
from supabase import create_client

# ---- Professional Enterprise Dark Theme ----
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #141829 50%, #0a0e27 100%);
        color: #e8eaf6;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #0a0e27 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15);
    }

    h1 {
        color: #818cf8 !important;
        font-weight: 700 !important;
        font-size: 2.25em !important;
        letter-spacing: -0.03em;
        margin-bottom: 0.8em !important;
        font-weight: 700;
    }

    h2 {
        color: #a5b4fc !important;
        font-weight: 600 !important;
        font-size: 1.6em !important;
        margin-top: 1.2em !important;
        margin-bottom: 1.2em !important;
        border-bottom: 2px solid rgba(165, 180, 252, 0.15);
        padding-bottom: 0.6em !important;
    }

    h3 {
        color: #c7d2fe !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #6366f1, #818cf8);
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 600;
        padding: 0.9em 2em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.25);
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #818cf8, #a5b4fc);
        transform: translateY(-3px);
        box-shadow: 0 12px 24px rgba(99, 102, 241, 0.35);
    }

    div.stButton > button:first-child:active {
        transform: translateY(-1px);
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > div,
    .stNumberInput > div > div > input {
        background-color: #1a1f3a !important;
        color: #e8eaf6 !important;
        border: 1px solid rgba(165, 180, 252, 0.15) !important;
        border-radius: 6px !important;
        padding: 11px 14px !important;
        font-size: 14px !important;
        transition: all 0.2s ease;
    }

    .stTextInput > div > div > input::placeholder,
    .stSelectbox > div > div > select::placeholder {
        color: #64748b !important;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stMultiSelect > div > div > div:focus {
        border-color: #818cf8 !important;
        background-color: rgba(99, 102, 241, 0.08) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }

    .stTextArea textarea {
        background-color: #1a1f3a !important;
        color: #e8eaf6 !important;
        border: 1px solid rgba(165, 180, 252, 0.15) !important;
        border-radius: 6px !important;
        padding: 14px !important;
        font-size: 14px !important;
        transition: all 0.2s ease;
        font-family: 'Poppins', sans-serif !important;
    }

    .stTextArea textarea:focus {
        border-color: #818cf8 !important;
        background-color: rgba(99, 102, 241, 0.08) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }

    .stTextArea textarea::placeholder {
        color: #64748b !important;
    }

    [data-testid="stMetricValue"] {
        color: #818cf8 !important;
        font-weight: 700;
        font-size: 2.2em !important;
    }

    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-weight: 500;
        font-size: 0.95em !important;
    }

    [data-testid="stMetricDelta"] {
        color: #10b981 !important;
    }

    .stAlert {
        border-radius: 8px;
        border: 1px solid rgba(165, 180, 252, 0.2);
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(165, 180, 252, 0.05)) !important;
        color: #e8eaf6;
        padding: 18px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    div[data-testid="stMarkdownContainer"] {
        color: #e8eaf6;
    }

    [data-testid="stDataFrame"] {
        background-color: #0f1419 !important;
    }

    .stDataFrame {
        border: 1px solid rgba(165, 180, 252, 0.1) !important;
        border-radius: 8px !important;
        overflow: hidden;
    }

    .stCheckbox > label {
        color: #cbd5e1 !important;
        font-weight: 500;
    }

    .stCheckbox > label > span {
        color: #818cf8 !important;
    }

    .stInfo {
        background-color: rgba(99, 102, 241, 0.08) !important;
        border-left: 4px solid #6366f1 !important;
    }

    .stSuccess {
        background-color: rgba(16, 185, 129, 0.08) !important;
        border-left: 4px solid #10b981 !important;
    }

    .stError {
        background-color: rgba(239, 68, 68, 0.08) !important;
        border-left: 4px solid #ef4444 !important;
    }

    .stWarning {
        background-color: rgba(245, 158, 11, 0.08) !important;
        border-left: 4px solid #f59e0b !important;
    }

    .stColumn {
        padding: 0 8px;
    }

    label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        font-size: 0.95em !important;
        margin-bottom: 0.5em !important;
    }

    [data-testid="stVerticalBlock"] {
        gap: 1.5rem;
    }

    /* Table styling */
    .dataframe {
        background-color: #1a1f3a !important;
        color: #e8eaf6 !important;
    }

    .dataframe th {
        background-color: #0f1419 !important;
        color: #818cf8 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid rgba(165, 180, 252, 0.2) !important;
        padding: 12px !important;
    }

    .dataframe td {
        border-bottom: 1px solid rgba(165, 180, 252, 0.1) !important;
        padding: 10px 12px !important;
        color: #e8eaf6 !important;
    }

    .dataframe tr:hover {
        background-color: rgba(99, 102, 241, 0.05) !important;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #1a1f3a;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(165, 180, 252, 0.3);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(165, 180, 252, 0.5);
    }

    .metric-card {
        background: linear-gradient(135deg, #1a1f3a, #151a2f);
        border: 1px solid rgba(165, 180, 252, 0.1);
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    /* Section spacing */
    [data-testid="stForm"] {
        background-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Initialize Clients ----
client_supabase = create_client(
    "https://ridvicextkltazrhmsql.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpZHZpY2V4dGtsdGF6cmhtc3FsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMwMTg0NywiImV4cCI6MjA3Njg3Nzg0N30Oi5exOpdEPjTGcxjMlJ_1HZKUeFuzKTFsHulmGkl8WgkPo"
)

# Initialize OpenAI with placeholder key
OPENAI_API_KEY = "ssk-proj-aVNhvlj9bUAgYf3vyNeVkNOfIt1vKiMt85BAAz0Up0bZFSkBJK6wX77a1gBwTEM7-mMkIjuJQ0T3BlbkFJA1Px1JKTb7vfcze1xDPB2csB2mTsoz2WMWzbK8QDxjLWUeFo1aOI3gHbTIEhzk7hDPYih6YnoA"

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
    
    st.title("AI-Powered Talent Matching Dashboard")
    st.markdown("<p style='color: #94a3b8; margin-bottom: 2em; font-size: 1em; font-weight: 300;'>Discover and match the best talent for your organizational needs</p>", unsafe_allow_html=True)
    
    # Input Section
    st.header("Job Requirements")
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.subheader("Position Details", divider="gray")
        role_name = st.text_input("Role Name", placeholder="e.g., Data Analyst, Software Engineer, Marketing Manager")
        job_level = st.selectbox("Job Level", ["Junior", "Mid-Level", "Senior", "Lead", "Executive"])
        industry = st.selectbox("Industry", ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Other"])
    
    with col2:
        st.subheader("Job Description", divider="gray")
        use_ai = st.checkbox("Auto-Generate Professional Job Description", value=True, 
                           help="Creates comprehensive job description using AI or professional templates")
        
        if st.button("Generate Job Description", type="primary") and role_name and job_level:
            with st.spinner("Generating professional job description..."):
                description = generate_ai_job_description(role_name, job_level, industry)
                role_purpose = st.text_area("Job Description", value=description, height=280)
        else:
            role_purpose = st.text_area("Job Description", 
                                      value=get_fallback_description(role_name, job_level) if role_name and job_level else "",
                                      height=280,
                                      placeholder="Enter job description or click 'Generate Job Description'")
    
    # Benchmark Selection
    st.header("Benchmark Selection")
    st.markdown("<p style='color: #94a3b8; margin-bottom: 1.5em; font-size: 0.95em;'>Select high-performing employees to establish success criteria</p>", unsafe_allow_html=True)
    
    try:
        employees = client_supabase.table("emp_cognitive").select("employee_id").limit(200).execute()
        employee_ids = list(set([e['employee_id'] for e in employees.data]))
        
        selected_benchmarks = st.multiselect(
            "Select High Performers", 
            options=employee_ids,
            placeholder="Search and select employee IDs...",
            help="These employees will serve as the baseline for talent matching"
        )
        
        if selected_benchmarks:
            benchmark_text = ", ".join(selected_benchmarks)
            st.info(f"Benchmarks Selected: {benchmark_text}")
            
    except Exception as e:
        st.error(f"Error loading employees: {str(e)}")
        selected_benchmarks = []
    
    # Generate Matches
    st.markdown("---")
    col_submit = st.columns([1, 4, 1])
    
    with col_submit[1]:
        if st.button("Generate Talent Matches", type="primary", use_container_width=True):
            if not all([role_name, job_level, role_purpose, selected_benchmarks]):
                st.error("Please complete all required fields and select benchmark employees to proceed.")
                return
                
            try:
                # Create new vacancy
                new_vacancy = {
                    "role_name": role_name,
                    "job_level": job_level, 
                    "role_purpose": role_purpose,
                    "selected_talent_ids": selected_benchmarks
                }
                
                result = client_supabase.table("talent_benchmarks").insert(new_vacancy).execute()
                vacancy_id = result.data[0]['job_vacancy_id']
                st.success(f"Job Vacancy #{vacancy_id} created successfully")
                
                # Get talent matches
                with st.spinner("Computing talent matches..."):
                    matches = client_supabase.rpc("get_final_matches_for_vacancy", {"vacancy_id": vacancy_id}).execute()
                    df = pd.DataFrame(matches.data)
                
                if df.empty:
                    st.warning("No matching candidates found. Consider adjusting benchmark employees.")
                    return
                
                # AI-Generated Job Profile
                st.header("Job Profile Summary")
                col1, col2 = st.columns([2.5, 1.5], gap="large")
                
                with col1:
                    st.markdown(role_purpose)
                
                with col2:
                    st.subheader("Key Metrics")
                    st.markdown(f"""
                    <div class='metric-card'>
                        <p style='color: #94a3b8; font-size: 0.85em; margin-bottom: 0.5em;'>Position Level</p>
                        <p style='color: #818cf8; font-size: 1.4em; font-weight: 600; margin: 0;'>{job_level}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class='metric-card' style='margin-top: 1em;'>
                        <p style='color: #94a3b8; font-size: 0.85em; margin-bottom: 0.5em;'>Benchmark Pool</p>
                        <p style='color: #818cf8; font-size: 1.4em; font-weight: 600; margin: 0;'>{len(selected_benchmarks)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class='metric-card' style='margin-top: 1em;'>
                        <p style='color: #94a3b8; font-size: 0.85em; margin-bottom: 0.5em;'>Total Analyzed</p>
                        <p style='color: #818cf8; font-size: 1.4em; font-weight: 600; margin: 0;'>{df['employee_id'].nunique()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.header("Ranked Talent List")
                ranked_talent = df.groupby('employee_id').agg({
                    'final_match_rate': 'mean',
                    'directorate': 'first',
                    'role': 'first',
                    'grade': 'first',
                    'tv_match_rate': 'mean',
                    'tgv_match_rate': 'mean'
                }).nlargest(20, 'final_match_rate').reset_index()
                
                ranked_talent['rank'] = range(1, len(ranked_talent) + 1)
                ranked_talent['final_match_rate'] = ranked_talent['final_match_rate'].round(1)
                
                display_cols = ['rank', 'employee_id', 'directorate', 'role', 'grade', 'final_match_rate']
                
                st.dataframe(
                    ranked_talent[display_cols].style.format({'final_match_rate': '{:.1f}%'}),
                    use_container_width=True,
                    height=500
                )
                
                st.header("Analysis Summary")
                if len(ranked_talent) > 0:
                    top_candidate = ranked_talent.iloc[0]
                    summary_text = f"""
                    **Top Candidate:** {top_candidate['employee_id']} with {top_candidate['final_match_rate']}% match rate
                    
                    **Assessment:** The top-ranked candidates demonstrate strong alignment with benchmark performance profiles. The leading candidate exhibits comprehensive skill alignment across all key competency areas required for this {job_level} position.
                    
                    **Recommendation:** Prioritize {top_candidate['employee_id']} for consideration based on overall profile fit and demonstrated capabilities relative to benchmark standards.
                    """
                    st.info(summary_text)
                
            except Exception as e:
                st.error(f"Error generating matches: {str(e)}")

if __name__ == "__main__":
    main()
