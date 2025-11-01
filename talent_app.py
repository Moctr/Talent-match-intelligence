import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

client = create_client(
    "https://ridvicextkltazrhmsql.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpZHZpY2V4dGtsdGF6cmhtc3FsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMwMTg0NywiZXhwIjoyMDc2ODc3ODQ3fQ.exOpdEPjTGcxjMlJ_1HZKUeFuzKTFsHulmGkl8WgkPo"
)

def main():
    st.title("🧠 AI Talent Matching Dashboard")
    
    # Input Section - Runtime User Inputs
    st.header("🎯 Job Requirements")
    col1, col2 = st.columns(2)
    
    with col1:
        role_name = st.text_input("Role Name", placeholder="e.g., Data Analyst")
        job_level = st.selectbox("Job Level", ["Junior", "Mid", "Senior", "Executive"])
    
    with col2:
        role_purpose = st.text_area("Role Purpose", placeholder="e.g., Analyze data and provide insights...")
    
    # Benchmark Selection
    st.header("⭐ Select Benchmark Employees")
    
    # Get available employees
    employees = client.table("emp_cognitive").select("employee_id").limit(200).execute()
    employee_ids = list(set([e['employee_id'] for e in employees.data]))
    
    selected_benchmarks = st.multiselect(
        "Choose high performers as benchmarks", 
        options=employee_ids,
        placeholder="Select employee IDs..."
    )
    
    # Show selected benchmarks
    if selected_benchmarks:
        st.write(f"**Selected Benchmarks:** {', '.join(selected_benchmarks)}")
    
    if st.button("🚀 Generate Talent Matches", type="primary"):
        if not all([role_name, job_level, role_purpose, selected_benchmarks]):
            st.error("Please fill all fields and select benchmark employees!")
            return
            
        try:
            # Step 1: Create new job vacancy in talent_benchmarks
            new_vacancy = {
                "role_name": role_name,
                "job_level": job_level, 
                "role_purpose": role_purpose,
                "selected_talent_ids": selected_benchmarks
            }
            
            result = client.table("talent_benchmarks").insert(new_vacancy).execute()
            vacancy_id = result.data[0]['job_vacancy_id']
            st.success(f"✅ Created Job Vacancy #{vacancy_id}")
            
            # Step 2: Recompute baselines and get matches using SQL function
            with st.spinner("🔄 Computing talent matches..."):
                matches = client.rpc("get_final_matches_for_vacancy", {"vacancy_id": vacancy_id}).execute()
                df = pd.DataFrame(matches.data)
            
            if df.empty:
                st.warning("No matches found. Try different benchmark employees.")
                return
            
            # Step 3: Regenerate profile, ranking, and visuals
            
            # Top 10 Ranking
            st.header("🏆 Top Talent Matches")
            top_matches = df.groupby('employee_id').agg({
                'final_match_rate': 'mean',
                'directorate': 'first',
                'role': 'first',
                'grade': 'first'
            }).nlargest(10, 'final_match_rate').reset_index()
            
            # Display ranking table
            st.dataframe(top_matches.style.format({'final_match_rate': '{:.1f}%'}))
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Match Rate Distribution")
                fig1 = px.bar(top_matches, x='employee_id', y='final_match_rate',
                             title="Top 10 Candidates by Match Rate")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.subheader("🎯 Match Rate Spread")
                fig2 = px.box(df, y='final_match_rate', 
                             title="Overall Match Rate Distribution")
                st.plotly_chart(fig2, use_container_width=True)
            
            # AI Insights
            st.header("🤖 AI Insights")
            avg_match = top_matches['final_match_rate'].mean()
            best_match = top_matches.iloc[0]
            
            insights = f"""
            **📈 Performance Analysis:**
            - **Average match rate for top candidates:** {avg_match:.1f}%
            - **Best fit candidate:** {best_match['employee_id']} ({best_match['final_match_rate']:.1f}% match)
            - **Role:** {best_match['role']} | **Grade:** {best_match['grade']}
            - **Directorate:** {best_match['directorate']}
            
            **💡 Recommendation:**
            Candidate {best_match['employee_id']} shows the strongest alignment with your benchmark profile.
            Consider this candidate for the {role_name} position.
            """
            
            st.info(insights)
            
            # Detailed breakdown
            st.header("🔍 Detailed Match Breakdown")
            st.dataframe(df.style.format({
                'tv_match_rate': '{:.1f}%',
                'tgv_match_rate': '{:.1f}%', 
                'final_match_rate': '{:.1f}%'
            }))
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
