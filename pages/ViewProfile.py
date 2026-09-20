import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")

# 1. Page Configuration
st.set_page_config(page_title="User Profile", layout="wide")

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
st.subheader("Account Profile Details")
st.markdown("---")

# Setup HTTP Bearer Token authentication header
headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}

try:
    # Fetch user data from your exact backend endpoint path
    response = requests.get(f"{FASTAPI_URL}/view_profile", headers=headers)
    
    if response.status_code == 200:
        result_data = response.json()
        
        # Matches your response mapping: user_data -> data
        user_metadata = result_data.get("user_data", {})
        
        # Extract variables returned from your database logic
        name = user_metadata.get("name", "N/A")
        email = user_metadata.get("email", "N/A")
        district = user_metadata.get("district", "N/A")
        land_in_hectares = user_metadata.get("land_in_hectares", 0.0)
        
        # Minimalist Presentation Grid for User Metadata
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Personal Information")
            st.text_input("Full Name", value=str(name), disabled=True)
            st.text_input("Email Address", value=str(email), disabled=True)
            
        with col2:
            st.markdown("##### Regional and Land Metrics")
            st.text_input("Assigned District", value=str(district), disabled=True)
            
            # Formatted number metric presentation bounds
            st.number_input(
                "Total Registered Land (Hectares)", 
                value=float(land_in_hectares), 
                format="%.2f", 
                disabled=True
            )
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Actions Row Layout for Profile Modification Controls
        action_col1, action_col2, _ = st.columns([1, 1, 2])
        
        with action_col1:
            # Action button directing to your Edit Profile workspace page file script
            if st.button("Edit Profile", use_container_width=True, type="primary"):
                st.switch_page("pages/EditProfile.py")
                
        with action_col2:
            if st.button("Back to Dashboard", use_container_width=True):
                st.switch_page("pages/Dashboard.py")
                
    elif response.status_code == 500:
        st.error("Server Error (500): Internal server logs profile extraction failed.")
    else:
        st.error(f"Unexpected operational status error code: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    st.error("Connection Failure: Target backend identity database gateway is unreachable.")
