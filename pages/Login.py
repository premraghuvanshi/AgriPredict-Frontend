import os
import requests
import streamlit as st

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")

# 1. Page Configuration (Must be the very first Streamlit command)
st.set_page_config(page_title="Login", layout="wide")

# Hide raw pages from sidebar
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

st.markdown("<h2 style='text-align: center;'>Account Authentication</h2>", unsafe_allow_html=True)

# 2. Structural Layout Configuration (Fixed positional argument layout error)
_, col, _ = st.columns(3)

with col:
    # --- THE LOGIN FORM ---
    with st.form("login_form", clear_on_submit=True):
        st.subheader("Credentials")
        email = st.text_input("Email Address", placeholder="username@domain.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not (email and password):
                st.warning("All input fields are required.")
            else:
                try:
                    pydantic_payload = {"email": email, "password": password}
                    response = requests.post(f"{FASTAPI_URL}/login", json=pydantic_payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.jwt_token = data.get("access_token")
                        st.session_state.user_info = {"email": email}
                        st.success("Authenticated successfully.")
                        
                        # REDIRECT TARGET DEVIATED DIRECTLY TO DASHBOARD OVERVIEW
                        st.switch_page("pages/Dashboard.py")
                        
                    elif response.status_code == 401:
                        st.error("Authentication Failed: Invalid email or password.")
                    elif response.status_code == 422:
                        errors = response.json().get("detail", [])
                        for err in errors:
                            st.error(f"Validation Error ({err.get('loc')[-1]}): {err.get('msg')}")
                    else:
                        st.error(f"Execution Error: Server returned code {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Connection Failure: Unable to reach the backend service.")

    # --- NAVIGATION ACTIONS CONTAINER (OUTSIDE THE FORM BLOCK) ---
    st.markdown("<br>", unsafe_allow_html=True)
    nav_col1, nav_col2 = st.columns(2)
    
    with nav_col1:
        if st.button("Return Home", use_container_width=True):
            st.switch_page("app.py")
            
    with nav_col2:
        if st.button("Register Account", use_container_width=True):
            st.switch_page("pages/Register.py")
