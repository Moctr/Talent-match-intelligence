import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
from supabase import create_client

# Initialize Supabase
client_supabase = create_client(
    "https://ridvicextkltazrhmsql.supabase.co",
    "YOUR_SUPABASE_SERVICE_ROLE_KEY"
)

# Initialize OpenAI
OPENAI_API_KEY = "YOUR_OPENAI_KEY"
client_openai = OpenAI(api_key=OPENAI_API_KEY)

# --- 🎨 PAGE CONFIG ---
st.set_page_config(page_title="AI Talent Match Intelligence", layout="wide")
st.markdown(
    """
    <style>
    body { background-color: #f8f9fb; }
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    .stButton>button { border-radius: 10px; padding: 0.7em 1.5em; font-weight: 600; }
    h1, h2, h3, h4 { color: #283747; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- HEADER ---
st.title("🧠 AI Talent Match Intelligence System")
st.caption("Discover what makes your top performers succeed — and find the next generation of leaders.")

st.divider()

# --- JOB CREATION SECTION ---
st.header("🎯 Define Job Role & Requirements")

col1, col2 = st.columns([1.2, 1])
with col1:
    role_name = st.text_input("Role Name", placeholder="e.g., Data Analyst, HR Manager")
    job_level = st.selectbox("Job Level", ["Junior", "Mid-Level", "Senior", "Lead", "Executive"])
    industry = st.selectbox("Industry", ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Other"])

with col2:
    st.markdown("#### ✨ Job Description Generator")
    use_ai = st.checkbox("Use AI to auto-generate job description", True)
    if st.button("⚡ Generate Description"):
        with st.spinner("Creating professional description..."):
            prompt = f"Write a full job description for a {job_level} {role_name} in {industry}."
            response = client_openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            job_desc = response.choices[0].message.content
    else:
        job_desc = ""

role_purpose = st.text_area("📋 Job Description", value=job_desc, height=250, placeholder="Enter or generate job description...")

st.divider()

# --- BENCHMARK SELECTION ---
st.header("🏅 Select Benchmark Employees")
try:
    employees = client_supabase.table("emp_cognitive").select("employee_id").limit(200).execute()
    employee_ids = list(set([e['employee_id'] for e in employees.data]))
    selected_benchmarks = st.multiselect(
        "Choose high-performing employees as benchmarks:",
        options=employee_ids,
        placeholder="Select employee IDs..."
    )
    if selected_benchmarks:
        st.success(f"✅ Selected Benchmarks: {', '.join(selected_benchmarks)}")
except Exception as e:
    st.error(f"Error loading employees: {str(e)}")
    selected_benchmarks = []

st.divider()

# --- MATCH GENERATION ---
st.header("🔍 Talent Match Analysis")
if st.button("🚀 Generate Talent Matches", type="primary"):
    if not all([role_name, job_level, role_purpose, selected_benchmarks]):
        st.error("Please complete all required fields before generating matches.")
    else:
        with st.spinner("🧮 Computing Talent Matches..."):
            # Mock data for demonstration (replace with actual Supabase RPC call)
            df = pd.DataFrame({
                "employee_id": ["EMP001", "EMP002", "EMP003"],
                "final_match_rate": [95.4, 91.2, 89.7],
                "directorate": ["HR", "Operations", "Finance"],
                "role": ["Analyst", "Lead", "Manager"]
            })

        # --- RESULTS DASHBOARD ---
        st.success("✅ Talent matches generated successfully!")

        st.subheader("🏆 Top Matching Candidates")
        st.dataframe(df, use_container_width=True)

        # --- VISUALIZATION ---
        fig = px.bar(
            df,
            x="employee_id",
            y="final_match_rate",
            text_auto=".1f",
            color="final_match_rate",
            color_continuous_scale="Tealgrn",
            title="Final Match Rate per Candidate"
        )
        fig.update_layout(title_x=0.3, plot_bgcolor="white", xaxis_title=None, yaxis_title="Match Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

        # --- AI INSIGHTS ---
        top_candidate = df.iloc[0]["employee_id"]
        st.subheader("💡 AI Insights Summary")
        st.info(f"""
        • **{top_candidate}** leads with **{df.iloc[0]['final_match_rate']}%** match — strongest benchmark fit.  
        • Top candidates show balanced competencies across all key variables.  
        • Consider {top_candidate} for immediate succession or mentorship roles.
        """)

# --- FOOTER ---
st.divider()
st.markdown(
    """
    <center>
    <small>🔍 Talent Match Intelligence | Developed for HR Analytics Case Study 2025</small>
    </center>
    """,
    unsafe_allow_html=True
)
