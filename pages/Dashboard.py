import os
import streamlit as st
from dotenv import load_dotenv

# Load configuration layer variables
load_dotenv()

# Page configuration - Set wide layout and keep sidebar tidy
st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global style injection to strictly hide all raw file names from the sidebar
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

# Route Guard Validation: Ensure user has a valid JWT token session before loading parameters
if "jwt_token" not in st.session_state or st.session_state.jwt_token is None:
    st.error("Authentication required. Access denied.")
    if st.button("Return to Login", type="primary"):
        st.switch_page("pages/Login.py")
    st.stop()

# --- AUTHENTICATED CONTROL PANEL INTERFACE ---

# Custom Workspace Sidebar Navigation
with st.sidebar:
    st.subheader("Navigation")
    # Active state tracker for user session awareness
    if st.button("Dashboard Overview", use_container_width=True, type="primary"):
        st.switch_page("pages/Dashboard.py")
        
    st.markdown("---")
    st.write(f"Identity: {st.session_state.user_info.get('email', 'User')}")
    
    if st.button("Sign Out", use_container_width=True):
        st.session_state.jwt_token = None
        st.session_state.user_info = None
        st.switch_page("app.py")

# Main Page Workspace
st.subheader("Operational User Dashboard")
st.markdown("---")

# Clean Minimalist Matrix Grid for System KPIs
m1, m2, m3 = st.columns(3)
m1.metric(label="Authentication Matrix", value="Verified")
m2.metric(label="API Core Gateway", value="Stable Connection")
m3.metric(label="Session State", value="Active")

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### System Submodules")

# 2x2 Clean Balanced Layout Grid Using Standard Columns
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# Row 1 Gateways
with row1_col1:
    st.markdown("#### Crop Optimization Analysis")
    st.write("Determine the best crop alternatives suited for specific regional soil parameters.")
    if st.button("Open Crop Recommendation", use_container_width=True, type="primary"):
        st.switch_page("pages/CropReccomendation.py")
        
with row1_col2:
    st.markdown("#### Production Yield Forecasting")
    st.write("Evaluate total agricultural crop production capacity maps across temporal cycles.")
    if st.button("Open Crop Production", use_container_width=True):
        st.switch_page("pages/CropProduction.py")

st.markdown("<br><hr>", unsafe_allow_html=True) # Minimal line separation block

# Row 2 Gateways
with row2_col1:
    st.markdown("#### Profile Configuration Details")
    st.write("Review core account credentials, localized regional district variables, and land metadata mappings.")
    if st.button("View Profile", use_container_width=True):
        st.switch_page("pages/ViewProfile.py")
        
with row2_col2:
    st.markdown("#### Operational Query History")
    st.write("Access logs of previously recorded system execution pipelines and stored predictions.")
    if st.button("View History", use_container_width=True):
        st.switch_page("pages/History.py")
