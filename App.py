import os
import streamlit as st
from dotenv import load_dotenv

# 1. Load System Environment Variables from .env file
load_dotenv()

# 2. Main Page Configurations (Must be the very first Streamlit command)
st.set_page_config(
    page_title="Management Portal",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start collapsed to keep it perfectly clean
)

# 3. Initialize Persistent Application Session States
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# Fetch the FastAPI Backend URL safely from your config layer
FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")


# --- CORE ROUTE GUARD CONTROLLER LAYER ---
if st.session_state.jwt_token is None:
    # IF NOT LOGGED IN: Inject target CSS parameters to hide the file-system routing sidebar.
    # This completely hides all raw pages from the sidebar list for unauthenticated users.
    st.markdown(
        """
        <style>
        div[data-testid="stSidebarNav"] ul {
            display: none !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # --- MINIMALIST LANDING SCREEN COMPONENT (HUMAN DESIGN) ---
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>Agricultural Management Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Backend connection: FastAPI | Frontend execution: Streamlit</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Structural 3-Column Grid for Information Breakdown
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Data Validation")
        st.write("Strict type-checking and schema enforcement via Pydantic architecture bounds.")
    with col2:
        st.subheader("Operational Metrics")
        st.write("Granular tracking of regional land plots calculated strictly in hectares.")
    with col3:
        st.subheader("System Performance")
        st.write("Asynchronous engine optimizations ensuring reliable database request loops.")
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Welcome. Please authenticate your identity or configure a new account to unlock the portal metrics.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Symmetrical 2-Column Grid Layout for Main Actions
    _, action_col1, action_col2, _ = st.columns([1, 2, 2, 1])
    
    with action_col1:
        if st.button("Sign In to Portal", use_container_width=True, type="primary"):
            st.switch_page("pages/Login.py")
            
    with action_col2:
        if st.button("Register Account", use_container_width=True):
            st.switch_page("pages/Register.py")

else:
    # --- IF ALREADY AUTHENTICATED: AUTO REDIRECT TO DASHBOARD ---
    # If a logged-in user hits app.py by mistake, it safely pushes them back to their workspace dashboard.
    st.switch_page("pages/Dashboard.py")
