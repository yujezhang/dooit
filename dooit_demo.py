import streamlit as st
import pandas as pd
import os
import sys
import importlib
import subprocess


# @st.cache_resource
# def install_from_whl(package_name, whl_path):
#     try:
#         # Check if the package is already installed
#         importlib.import_module(package_name)
#         print(f"'{package_name}' is already installed.")
#     except ImportError:
#         # Install from the specified .whl file
#         if os.path.exists(whl_path):
#             print(f"Installing '{package_name}' from '{whl_path}'...")
#             subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", whl_path])
#             print(f"'{package_name}' installed successfully!")
#         else:
#             print(f"Error: The .whl file '{whl_path}' does not exist.")

# install_from_whl("langchain-community", "langchain_community-0.3.17-py3-none-any.whl")
# install_from_whl("langchain-core", "langchain_core-0.3.35-py3-none-any.whl")

import llm_api as api
# Sample employee data
emps = pd.read_csv("data/data3.csv")
skillset = ["Java", "JavaScript", "React", "Node.js", 'AWS', 'Embedded C', 
            'Game Development', 'Python','Cybersecurity', "Creativity", "Adaptability", 
            "Conflict Resolution" ]

# Initialize session state for navigation
# navigation session state
if 'emps' not in st.session_state:
    st.session_state.emps = emps
    st.session_state.emps_json = emps.to_dict(orient="records")

if 'current_page' not in st.session_state:
    st.session_state.current_page = "employee"

if 'selected_emp' not in st.session_state:
    st.session_state.selected_emp = st.session_state.emps.iloc[0,0]

# Data session state
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None  # Store prediction result
    
if 'talent_req' not in st.session_state:
    st.session_state.talent_req = "" # Store talent requirement result

if 'talent_result' not in st.session_state:
    st.session_state.talent_result = None # Store talent search result

# Function to navigate to a page
def navigate(page, emp_id=None):
    st.session_state.current_page = page
    st.session_state.selected_emp = emp_id
    st.session_state.prediction_result = None  # Reset prediction when switching employees

# Fucntion to get career path by employees data
def job_predict(emp_data):
    st.session_state.prediction_result = api.job_predict(emp_data)

# Function to get talent seach by tech requirement and data in json
def search_talent(talent_req):
    if talent_req != []:
        st.session_state.talent_result = api.talent_search(talent_req, st.session_state.emps_json)

# Add more description to requirement in chat input
def describe_more():
    print(st.session_state.talent_desc)
    st.session_state.talent_req = st.session_state.talent_desc
    search_talent(st.session_state.talent_req)
    
# Sidebar Navigation
with st.sidebar:
    if st.button("Talent Search", use_container_width=True, type='primary'):
        navigate("talent_search")

    st.sidebar.caption("Employees")

    for _, row in st.session_state.emps.iterrows():
        if st.button(row["Name"], key=f"emp_{row['ID']}", use_container_width=True):
            navigate("employee", row["ID"])

# Page Rendering Logic
# Talent Search
if st.session_state.current_page == "talent_search":
    st.title("Talent Search")
    
    st.session_state.talent_req = st.multiselect(
        "Select your requirement",
        skillset,
        [],
    )
    col1, col2, col3 = st.columns(3)
    
    if st.session_state.talent_req != []:
        col1.button("Search", use_container_width=True, on_click=search_talent, args=[st.session_state.talent_req])
    
    if col3.button("Clear", use_container_width=True, type='primary'):
        st.session_state.talent_req = ""
        st.session_state.talent_result = None
        
    st.chat_input("Describe more here", on_submit=describe_more, key='talent_desc')
        
    if st.session_state.talent_result is not None:
        print(st.session_state.talent_result)
        st.write("### Talents Searched:")
        for talent in st.session_state.talent_result['talent_search']:
            if 'talent' in talent:
                st.write(talent['talent'])
            with st.expander("See explanation"):
                if 'reason' in talent:
                    st.write(talent['reason'])

# Employee job prediction
elif st.session_state.current_page == "employee" and st.session_state.selected_emp is not None:
    # Get employee details
    emp_data = st.session_state.emps[st.session_state.emps["ID"] == st.session_state.selected_emp].iloc[0]
    st.title(f"{emp_data['Name']}")
    st.divider()
    st.subheader(f"{emp_data['Role']}")
    col1, col2 = st.columns(2)
    con1 = col1.container(border=True)
    con2 = col2.container(border=True)
    con1.write("**Hardskill**")
    con1.write(emp_data["HardSkill"])
    con2.write("**Softskill**")
    con2.write(emp_data['SoftSkill'])
    st.button('See Career Path Planing', use_container_width=True, on_click=job_predict, args=[emp_data])
    if st.session_state.prediction_result is not None:
        st.write("### Career Path Planing:")
        for prediction in st.session_state.prediction_result['job_prediction']:
            st.write(prediction['job'])
            with st.expander("See explanation"):
                st.write(prediction['reason'])       