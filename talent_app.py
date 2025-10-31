# talent_app.py
import streamlit as st
import pandas as pd
import json

# Page configuration
st.set_page_config(
    page_title="Talent Benchmarks Manager",
    page_icon="🏆",
    layout="wide"
)

# Main title
st.title("🏆 Talent Benchmarks Manager")
st.markdown("Define ideal talent profiles and match employees against benchmarks")

# Initialize session state for data
if 'benchmarks' not in st.session_state:
    st.session_state.benchmarks = []

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Dashboard", "Create Benchmark", "View Benchmarks", "Employee Matching"]
)

# Sample data (we'll replace with Supabase later)
sample_employees = [
    {"id": 111, "name": "John Smith", "role": "Sales", "rating": 5},
    {"id": 123, "name": "Sarah Johnson", "role": "Sales", "rating": 5},
    {"id": 113, "name": "Mike Chen", "role": "Development", "rating": 5},
    {"id": 4213, "name": "Emma Davis", "role": "Marketing", "rating": 5},
    {"id": 412, "name": "Alex Wong", "role": "Sales", "rating": 4}
]

if page == "Dashboard":
    st.header("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Benchmarks", len(st.session_state.benchmarks))
    with col2:
        st.metric("Top Performers", len(sample_employees))
    with col3:
        st.metric("Active Roles", len(set([b['role_name'] for b in st.session_state.benchmarks])))
    
    st.info("💡 Start by creating your first talent benchmark!")

elif page == "Create Benchmark":
    st.header("➕ Create New Talent Benchmark")
    
    with st.form("benchmark_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            job_vacancy_id = st.number_input("Job Vacancy ID", min_value=1, value=1)
            role_name = st.text_input("Role Name", placeholder="e.g., Senior Sales Executive")
            job_level = st.selectbox("Job Level", ["Junior", "Mid", "Senior", "Lead", "Principal"])
        
        with col2:
            role_purpose = st.text_area("Role Purpose", placeholder="Describe the main objectives of this role...")
            weights_config = st.selectbox("Weights Configuration", ["cog", "behavioral", "technical", "balanced"])
        
        # Talent selection
        st.subheader("🎯 Select Benchmark Employees (Rating = 5)")
        top_performers = [emp for emp in sample_employees if emp['rating'] == 5]
        
        selected_talents = []
        for emp in top_performers:
            if st.checkbox(f"{emp['name']} - {emp['role']} (ID: {emp['id']})", key=emp['id']):
                selected_talents.append(emp['id'])
        
        submitted = st.form_submit_button("Create Talent Benchmark")
        
        if submitted:
            if not selected_talents:
                st.error("Please select at least one benchmark employee!")
            else:
                new_benchmark = {
                    'job_vacancy_id': job_vacancy_id,
                    'role_name': role_name,
                    'job_level': job_level,
                    'role_purpose': role_purpose,
                    'selected_talent_ids': selected_talents,
                    'weights_config': weights_config
                }
                
                st.session_state.benchmarks.append(new_benchmark)
                st.success(f"✅ Successfully created benchmark for {role_name}!")
                
                # Show created benchmark
                with st.expander("View Created Benchmark"):
                    st.json(new_benchmark)

elif page == "View Benchmarks":
    st.header("📋 Current Talent Benchmarks")
    
    if not st.session_state.benchmarks:
        st.info("No benchmarks created yet. Go to 'Create Benchmark' to get started!")
    else:
        for i, benchmark in enumerate(st.session_state.benchmarks):
            with st.expander(f"🏷️ {benchmark['role_name']} - {benchmark['job_level']} (ID: {benchmark['job_vacancy_id']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Role Purpose:** {benchmark['role_purpose']}")
                    st.write(f"**Weights Config:** {benchmark['weights_config']}")
                
                with col2:
                    st.write(f"**Benchmark Employees:** {len(benchmark['selected_talent_ids'])} selected")
                    st.write(f"**Employee IDs:** {benchmark['selected_talent_ids']}")
                
                # Delete button
                if st.button(f"Delete Benchmark", key=f"delete_{i}"):
                    st.session_state.benchmarks.pop(i)
                    st.rerun()

elif page == "Employee Matching":
    st.header("🔍 Employee Matching Simulation")
    
    if not st.session_state.benchmarks:
        st.warning("Create benchmarks first to see matching results!")
    else:
        st.subheader("Match Employees Against Benchmarks")
        
        selected_benchmark = st.selectbox(
            "Select Benchmark to Match Against:",
            [f"{b['role_name']} - {b['job_level']} (ID: {b['job_vacancy_id']})" for b in st.session_state.benchmarks]
        )
        
        # Simple matching simulation
        if st.button("Calculate Match Scores"):
            st.subheader("🎯 Match Results")
            
            # Mock matching algorithm
            for employee in sample_employees:
                match_score = min(95, 70 + (employee['rating'] * 5) + len(st.session_state.benchmarks))
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{employee['name']}** - {employee['role']}")
                with col2:
                    st.write(f"Rating: {employee['rating']}/5")
                with col3:
                    if match_score >= 85:
                        st.success(f"Match: {match_score}% 🎯")
                    elif match_score >= 70:
                        st.warning(f"Match: {match_score}% ⚠️")
                    else:
                        st.error(f"Match: {match_score}% ❌")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("**Next Step:** Connect to Supabase database for persistent storage")
