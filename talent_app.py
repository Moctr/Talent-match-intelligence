pip install supabase

import streamlit as st
import pandas as pd
from supabase import create_client
 #Initialize Supabase client with YOUR credentials
client = create_client(
    "https://ridvicextkltazrhmsql.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpZHZpY2V4dGtsdGF6cmhtc3FsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMwMTg0NywiZXhwIjoyMDc2ODc3ODQ3fQ.exOpdEPjTGcxjMlJ_1HZKUeFuzKTFsHulmGkl8WgkPo"
)

def main():
    st.title("AI Talent Matching Dashboard")
    
    # Input Section
    st.header("Job Requirements")
    role_name = st.text_input("Role Name")
    job_level = st.selectbox("Job Level", ["Junior", "Mid", "Senior", "Executive"])
    role_purpose = st.text_area("Role Purpose")
    
    # Benchmark Selection
    st.header("Select Benchmark Employees")
    employees = client.table("employees").select("employee_id, fullname, rating").execute()
    benchmark_options = {f"{e['employee_id']} - {e['fullname']} (Rating: {e['rating']})": e['employee_id'] 
                        for e in employees.data}
    selected_benchmarks = st.multiselect("Choose high performers as benchmarks", options=list(benchmark_options.keys()))
    
    if st.button("Generate Talent Matches"):
        if selected_benchmarks:
            # Create new benchmark entry
            benchmark_ids = [benchmark_options[b] for b in selected_benchmarks]
            new_vacancy = {
                "role_name": role_name,
                "job_level": job_level, 
                "role_purpose": role_purpose,
                "selected_talent_ids": benchmark_ids
            }
            
            # Insert into talent_benchmarks
            result = client.table("talent_benchmarks").insert(new_vacancy).execute()
            vacancy_id = result.data[0]['job_vacancy_id']
            
            # Get matches using our SQL function
            matches = client.rpc("get_final_matches_for_vacancy", {"vacancy_id": vacancy_id}).execute()
            
            # Display Results
            st.header("Top Talent Matches")
            df = pd.DataFrame(matches.data)
            
            # Show top 10 by final match rate
            top_matches = df.groupby('employee_id').agg({
                'final_match_rate': 'mean',
                'directorate': 'first',
                'role': 'first',
                'grade': 'first'
            }).nlargest(10, 'final_match_rate')
            
            st.dataframe(top_matches)
            
            # Visualizations
            st.subheader("Match Distribution")
            st.bar_chart(top_matches['final_match_rate'])
            
            # AI Insights
            st.subheader("AI Insights")
            avg_match = top_matches['final_match_rate'].mean()
            st.write(f"**Average match rate for top candidates: {avg_match:.1f}%**")
            st.write(f"**Best fit:** {top_matches.index[0]} with {top_matches['final_match_rate'].iloc[0]:.1f}% match")
            
if __name__ == "__main__":
    main()
