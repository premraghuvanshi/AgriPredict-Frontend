import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")

# 1. Page Configuration
st.set_page_config(page_title="History Logs", layout="wide")

# Hide all default sidebar page links completely
st.markdown(
    """
    <style>
    div[data-testid="stSidebarNav"] ul {
        display: none !important;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# 2. Route Guard Validation: Ensure user is logged in
if "jwt_token" not in st.session_state or st.session_state.jwt_token is None:
    st.error("Authentication required. Access denied.")
    if st.button("Return to Login", type="primary"):
        st.switch_page("pages/Login.py")
    st.stop()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.subheader("Navigation")
    if st.button("Return to Dashboard", use_container_width=True):
        st.switch_page("pages/Dashboard.py")
    st.markdown("---")
    st.write(f"Identity: {st.session_state.user_info.get('email', 'User')}")

# --- MAIN WORKSPACE ---
st.subheader("Operational Execution History")
st.markdown("---")
st.write("Select the specific prediction log module from the dropdown below to fetch record summaries from the database.")

# 3. Dropdown Selection Framework
history_type = st.selectbox(
    "Select History Module",
    ["Crop Recommendation Logs", "Crop Production Logs"]
)

# Configuration for network operations
headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}

if history_type == "Crop Recommendation Logs":
    st.markdown("#### Stored Crop Recommendations")
    try:
        # Call the exact backend endpoint path
        response = requests.get(
            f"{FASTAPI_URL}/prediction__history/Crop_recommendation",
            headers=headers
        )
        
        if response.status_code == 200:
            result_data = response.json()
            # Extract list from the key: "Crop Prediction History"
            raw_logs = result_data.get("Crop Prediction History", [])
            
            if raw_logs:
                # Convert structured lists directly into pandas dataframes for clean human-centric table views
                df = pd.DataFrame(raw_logs)
                
                # Optional: drop internal db id keys if present to keep it minimalist
                if "user_id" in df.columns:
                    df = df.drop(columns=["user_id"])
                    
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.success(result_data.get("message", "History retrieved successfully."))
            else:
                st.info("No recommendation prediction records found inside the database.")
                
        elif response.status_code == 500:
            st.error("Server Error (500): Internal database pipeline execution failed.")
        else:
            st.error(f"Unexpected operational status error code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("Connection Failure: Target backend history tracking database is unreachable.")

elif history_type == "Crop Production Logs":
    st.markdown("#### Stored Production Yield Forecasts")
    try:
        # Call the exact backend endpoint path
        response = requests.get(
            f"{FASTAPI_URL}/prediction__history/Crop_Production",
            headers=headers
        )
        
        if response.status_code == 200:
            result_data = response.json()
            # Extract list from the key: "Crop Production History"
            raw_logs = result_data.get("Crop Production History", [])
            
            if raw_logs:
                df = pd.DataFrame(raw_logs)
                
                if "user_id" in df.columns:
                    df = df.drop(columns=["user_id"])
                    
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.success(result_data.get("message", "History retrieved successfully."))
            else:
                st.info("No production forecasting records found inside the database.")
                
        elif response.status_code == 500:
            st.error("Server Error (500): Internal server log retrieval failed.")
        else:
            st.error(f"Unexpected operational status error code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("Connection Failure: Target backend history tracking database is unreachable.")
