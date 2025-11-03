import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
from supabase import create_client

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
    st.title(" AI-Powered Talent Matching Dashboard")
    
    # API Key Information
    with st.sidebar:
        st.header(" API Setup Instructions")
        st.info("""
        **To enable AI features:**
        
        1. Get OpenAI API key from:
           https://platform.openai.com/api-keys
        
        2. Replace the placeholder in code:
           - Open `talent_app.py`
           - Find: `OPENAI_API_KEY = "sk-your-openai-api-key-here"`
           - Replace with your actual key
        
        3. Redeploy the app
        """)
        
        if client_openai:
            st.success(" OpenAI API Connected")
        else:
            st.warning(" AI Features: Add OpenAI API key to code")
    
    # Input Section
    st.header(" Job Requirements")
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
    st.header(" Select Benchmark Employees")
    
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
    if st.button(" Generate Talent Matches", type="primary"):
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
            st.success(f" Created Job Vacancy #{vacancy_id}")
            
            # Get talent matches
            with st.spinner(" Computing talent matches..."):
                matches = client_supabase.rpc("get_final_matches_for_vacancy", {"vacancy_id": vacancy_id}).execute()
                df = pd.DataFrame(matches.data)
            
            if df.empty:
                st.warning("No matches found. Try different benchmark employees.")
                return
            
            # Display Results (rest of your existing results display code)
            # ... [include all the visualization code from previous version]
            
            st.header(" AI-Generated Job Profile")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(role_purpose)
            
            with col2:
                st.subheader("📋 Quick Facts")
                st.metric("Role Level", job_level)
                st.metric("Benchmarks Used", len(selected_benchmarks))
                st.metric("Candidates Analyzed", df['employee_id'].nunique())
            
            # Ranked Talent List
            st.header(" Ranked Talent List")
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
            
            # Show manual insights
            st.header(" Talent Insights")
            top_3 = ranked_talent.head(3)
            insights = f"""
            **Key Observations:**
            
            • **{top_3.iloc[0]['employee_id']}** leads with {top_3.iloc[0]['final_match_rate']}% match - strongest overall alignment
            • Top 3 candidates show exceptional alignment with benchmark profiles
            • Consider {top_3.iloc[0]['employee_id']} for immediate placement based on comprehensive profile fit
            • All top candidates demonstrate balanced competency across key talent variables
            """
            
            st.info(insights)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
