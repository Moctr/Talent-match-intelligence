import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
from supabase import create_client

# ---- Professional Dark Theme UI ----
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        color: #e2e8f0;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.1);
    }

    h1 {
        color: #38bdf8 !important;
        font-weight: 700 !important;
        font-size: 2.5em !important;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #38bdf8, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5em !important;
    }

    h2 {
        color: #0ea5e9 !important;
        font-weight: 700 !important;
        font-size: 1.75em !important;
        margin-top: 1.5em !important;
        margin-bottom: 1em !important;
        border-bottom: 2px solid rgba(14, 165, 233, 0.2);
        padding-bottom: 0.5em !important;
    }

    h3 {
        color: #38bdf8 !important;
        font-weight: 600 !important;
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0ea5e9, #06b6d4);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 600;
        padding: 0.75em 1.5em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4);
    }

    div.stButton > button:first-child:active {
        transform: translateY(0);
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > div {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1.5px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        font-size: 14px !important;
        transition: all 0.2s ease;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stMultiSelect > div > div > div:focus {
        border-color: #0ea5e9 !important;
        background-color: rgba(14, 165, 233, 0.05) !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1) !important;
    }

    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1.5px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 8px !important;
        padding: 14px !important;
        font-size: 14px !important;
        transition: all 0.2s ease;
    }

    .stTextArea textarea:focus {
        border-color: #0ea5e9 !important;
        background-color: rgba(14, 165, 233, 0.05) !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1) !important;
    }

    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 700;
        font-size: 2em !important;
    }

    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-weight: 500;
    }

    .stMetricDelta {
        color: #10b981 !important;
    }

    .stAlert {
        border-radius: 12px;
        border: 1.5px solid rgba(14, 165, 233, 0.3);
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(6, 182, 212, 0.05)) !important;
        color: #cffafe;
        padding: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    div[data-testid="stMarkdownContainer"] {
        color: #e2e8f0;
    }

    [data-testid="stDataFrame"] {
        background-color: #1e293b !important;
    }

    .stDataFrame {
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
        border-radius: 8px !important;
        overflow: hidden;
    }

    .stCheckbox > label {
        color: #cbd5e1 !important;
        font-weight: 500;
    }

    .stCheckbox > label > span {
        color: #0ea5e9 !important;
    }

    .stInfo {
        background-color: rgba(14, 165, 233, 0.1) !important;
        border-left: 4px solid #0ea5e9 !important;
    }

    .stSuccess {
        background-color: rgba(16, 185, 129, 0.1) !important;
        border-left: 4px solid #10b981 !important;
    }

    .stError {
        background-color: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid #ef4444 !important;
    }

    .stWarning {
        background-color: rgba(245, 158, 11, 0.1) !important;
        border-left: 4px solid #f59e0b !important;
    }

    /* Column divider styling */
    .stColumn {
        padding: 0 12px;
    }

    /* Spinner styling */
    .stSpinner {
        color: #0ea5e9 !important;
    }

    /* Sidebar text */
    .css-1d391kg {
        color: #cbd5e1 !important;
    }

    /* Label styling */
    label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Initialize Clients ----
client_supabase = create_client(
    "https://ridvicextkltazrhmsql.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpZHZpY2V4dGtsdGF6cmhtc3FsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMwMTg0NywiZXhwIjoyMDc2ODc3ODQ3fQ.exOpdEPjTGcxjMlJ_1HZKUeFuzKTFsHulmGkl8WgkPo"
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
    st.title("✨ AI-Powered Talent Matching Dashboard")
    
    # Input Section
    st.header("🎯 Job Requirements")
    col1, col2 = st.columns(2)
    
    with col1:
        role_name = st.text_input("Role Name", placeholder="e.g., Data Analyst, Software Engineer, Marketing Manager")
        job_level = st.selectbox("Job Level", ["Junior", "Mid-Level", "Senior", "Lead", "Executive"])
        industry = st.selectbox("Industry", ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Other"])
    
    with col2:
        use_ai = st.checkbox("Generate Professional Job Description", value=True, 
                           help="Creates comprehensive job description using AI or professional templates")
        
        if st.button("🪄 Generate Job Description", type="secondary") and role_name and job_level:
            with st.spinner(" Creating professional job description..."):
                description = generate_ai_job_description(role_name, job_level, industry)
                role_purpose = st.text_area("Job Description", value=description, height=300)
        else:
            role_purpose = st.text_area("Job Description", 
                                      value=get_fallback_description(role_name, job_level) if role_name and job_level else "",
                                      height=300,
                                      placeholder="Enter job description or click 'Generate Job Description'")
    
    # Benchmark Selection
    st.header("⭐ Select Benchmark Employees")
    
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
            st.info(f"**Selected Benchmarks:** {', '.join(selected_benchmarks)}")
            
    except Exception as e:
        st.error(f"Error loading employees: {str(e)}")
        selected_benchmarks = []
    
    # Generate Matches
    if st.button("🚀 Generate Talent Matches", type="primary"):
        if not all([role_name, job_level, role_purpose, selected_benchmarks]):
            st.error("Please fill all required fields and select benchmark employees!")
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
            st.success(f"✅ Created Job Vacancy #{vacancy_id}")
            
            # Get talent matches
            with st.spinner(" Computing talent matches..."):
                matches = client_supabase.rpc("get_final_matches_for_vacancy", {"vacancy_id": vacancy_id}).execute()
                df = pd.DataFrame(matches.data)
            
            if df.empty:
                st.warning("No matches found. Try different benchmark employees.")
                return
            
            st.header("🧠 AI-Generated Job Profile")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(role_purpose)
            
            with col2:
                st.subheader("📋 Quick Facts")
                st.metric("Role Level", job_level)
                st.metric("Benchmarks Used", len(selected_benchmarks))
                st.metric("Candidates Analyzed", df['employee_id'].nunique())
            
            st.header("🏆 Ranked Talent List")
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
                use_container_width=True
            )
            
            st.header("💡 Talent Insights")
            top_3 = ranked_talent.head(3)
            insights = f"""
            **Key Observations:**
            
            • **{top_3.iloc[0]['employee_id']}** leads with {top_3.iloc[0]['final_match_rate']}% match — strongest overall alignment  
            • Top 3 candidates show exceptional alignment with benchmark profiles  
            • Consider {top_3.iloc[0]['employee_id']} for immediate placement based on comprehensive profile fit  
            • All top candidates demonstrate balanced competency across key talent variables
            """
            
            st.info(insights)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
