
import streamlit as st
import pandas as pd

def main():
    st.title("Talent Benchmarks Manager")
    st.write("Simple talent management app")
    
    # Add your form here
    with st.form("benchmark_form"):
        name = st.text_input("Role Name")
        submitted = st.form_submit_button("Create")
        if submitted:
            st.success(f"Created: {name}")

if __name__ == "__main__":
    main()
