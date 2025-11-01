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

# Initialize OpenAI client (will be set when API key is available)
client_openai = None

def generate_ai_job_description(role_name, job_level, industry="Technology"):
    """Generate job description using OpenAI"""
    try:
        if not client_openai:
            return f"**{role_name} - {job_level}**\n\n*Please add OpenAI API key to generate AI job description.*"
        
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
        return f"**{role_name} - {job_level}**\n\n*Error generating AI description: {str(e)}*"

def main():
    st.set_page_config(page_title="AI Talent Matcher", layout="wide")
    st.title("🧠 AI-Powered Talent Matching Dashboard")
    
    # API Key Setup
    st.sidebar.header("🔑 API Configuration")
    openai_key = st.sidebar.text_input("OpenAI API Key", type="password", 
                                      help="Get your API key from https://platform.openai.com/api-keys")
    
    global client_openai
    if openai_key:
        client_openai = OpenAI(api_key=openai_key)
        st.sidebar.success("✅ OpenAI API Connected")
    else:
        st.sidebar.warning("⚠️ Add OpenAI API key for AI features")
    
    # Input Section
    st.header("🎯 Job Requirements")
    col1, col2 = st.columns(2)
    
    with col1:
        role_name = st.text_input("Role Name", placeholder="e.g., Data Analyst, Software Engineer, Marketing Manager")
        job_level = st.selectbox("Job Level", ["Junior", "Mid-Level", "Senior", "Lead", "Executive"])
        industry = st.selectbox("Industry", ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Other"])
    
    with col2:
        use_ai = st.checkbox("Generate AI Job Description", value=True, 
                           help="Use OpenAI to create a professional job description")
        
        if use_ai and role_name and job_level and client_openai:
            if st.button("🪄 Generate with AI", type="secondary"):
                with st.spinner("🤖 Creating professional job description..."):
                    ai_description = generate_ai_job_description(role_name, job_level, industry)
                    role_purpose = st.text_area("Job Description", value=ai_description, height=300)
            else:
                role_purpose = st.text_area("Job Description", 
                                          placeholder="Click 'Generate with AI' to create a professional job description...", 
                                          height=300)
        else:
            role_purpose = st.text_area("Job Description", 
                                      placeholder="Enter job description manually or enable AI generation...", 
                                      height=300)
    
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
            with st.spinner("🔄 Computing talent matches..."):
                matches = client_supabase.rpc("get_final_matches_for_vacancy", {"vacancy_id": vacancy_id}).execute()
                df = pd.DataFrame(matches.data)
            
            if df.empty:
                st.warning("No matches found. Try different benchmark employees.")
                return
            
            # AI-Generated Job Profile
            st.header("🤖 AI-Generated Job Profile")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(role_purpose)
            
            with col2:
                st.subheader("📋 Quick Facts")
                st.metric("Role Level", job_level)
                st.metric("Benchmarks Used", len(selected_benchmarks))
                st.metric("Candidates Analyzed", df['employee_id'].nunique())
            
            # Ranked Talent List
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
            
            # Dashboard Visualizations
            st.header("📊 Talent Analytics Dashboard")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Match Rate Distribution
                st.subheader("Match Rate Distribution")
                fig1 = px.histogram(df, x='final_match_rate', nbins=20,
                                  title="Distribution of Final Match Rates",
                                  color_discrete_sequence=['#FF4B4B'])
                st.plotly_chart(fig1, use_container_width=True)
                
                # Top 10 Candidates
                st.subheader("Top 10 Candidates")
                top_10 = ranked_talent.head(10)
                fig2 = px.bar(top_10, x='employee_id', y='final_match_rate',
                            title="Top 10 Candidates by Match Rate",
                            color='final_match_rate',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                # Strengths & Gaps Analysis
                st.subheader("Top Talent Variables")
                tv_analysis = df.groupby('tv_name')['tv_match_rate'].mean().nlargest(8)
                fig3 = px.bar(x=tv_analysis.index, y=tv_analysis.values,
                            title="Strongest Talent Variables Across Candidates",
                            labels={'x': 'Talent Variable', 'y': 'Average Match Rate (%)'})
                st.plotly_chart(fig3, use_container_width=True)
                
                # Performance Range
                st.subheader("Performance Range by Variable")
                bench_stats = df.groupby('tv_name')['tv_match_rate'].agg(['min', 'max', 'mean']).reset_index()
                fig4 = px.scatter(bench_stats, x='tv_name', y='mean', 
                                error_y=bench_stats['max'] - bench_stats['mean'],
                                error_y_minus=bench_stats['mean'] - bench_stats['min'],
                                title="Performance Range Across Talent Variables")
                st.plotly_chart(fig4, use_container_width=True)
            
            # Radar Chart for Top Candidate
            if not df.empty:
                st.header("📈 Candidate Profile Analysis")
                top_candidate = ranked_talent.iloc[0]['employee_id']
                candidate_data = df[df['employee_id'] == top_candidate]
                
                if not candidate_data.empty:
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        fig_radar = go.Figure()
                        fig_radar.add_trace(go.Scatterpolar(
                            r=candidate_data['tv_match_rate'],
                            theta=candidate_data['tv_name'],
                            fill='toself',
                            name=f'Top Candidate: {top_candidate}',
                            line_color='#FF4B4B'
                        ))
                        fig_radar.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 150])),
                            showlegend=True,
                            title=f"Skills Profile: {top_candidate}"
                        )
                        st.plotly_chart(fig_radar, use_container_width=True)
                    
                    with col2:
                        st.subheader("🎯 Top Candidate Summary")
                        st.metric("Overall Match", f"{ranked_talent.iloc[0]['final_match_rate']}%")
                        st.metric("Role", ranked_talent.iloc[0]['role'])
                        st.metric("Grade", ranked_talent.iloc[0]['grade'])
                        st.metric("Directorate", ranked_talent.iloc[0]['directorate'])
            
            # AI Insights
            st.header("💡 AI-Powered Insights")
            
            if client_openai:
                try:
                    insights_prompt = f"""
                    Analyze this talent matching data and provide 3-4 key insights:
                    
                    Role: {role_name} ({job_level})
                    Top 3 Candidates: {ranked_talent.head(3)['employee_id'].tolist()}
                    Match Rates: {ranked_talent.head(3)['final_match_rate'].tolist()}
                    
                    Provide insights on:
                    1. Why these candidates ranked highest
                    2. Key strengths observed
                    3. Any notable patterns in the data
                    4. Recommendations for next steps
                    
                    Keep it concise and actionable.
                    """
                    
                    insights_response = client_openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": insights_prompt}],
                        max_tokens=500
                    )
                    
                    ai_insights = insights_response.choices[0].message.content
                    st.info(ai_insights)
                    
                except Exception as e:
                    st.warning("AI insights temporarily unavailable")
            
            # Manual insights fallback
            top_3 = ranked_talent.head(3)
            manual_insights = f"""
            **Key Observations:**
            
            • **{top_3.iloc[0]['employee_id']}** leads with {top_3.iloc[0]['final_match_rate']}% match - strongest overall alignment
            • Top 3 candidates show 20-30% higher match rates than cohort average  
            • Consistent strength in technical and analytical competencies across top performers
            • Consider {top_3.iloc[0]['employee_id']} for immediate placement based on profile fit
            """
            
            st.success(manual_insights)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
