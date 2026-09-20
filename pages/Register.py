import os
import requests
import streamlit as st

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")

# 1. Page Configuration (Must be the very first Streamlit command)
st.set_page_config(page_title="Register", layout="wide")

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

st.markdown("<h2 style='text-align: center;'>Account Registration</h2>", unsafe_allow_html=True)

# 2. Structural Layout Configuration (Fixed positional argument layout error)
_, col, _ = st.columns(3)

with col:
    # --- THE REGISTRATION FORM ---
    with st.form("register_form", clear_on_submit=True):
        st.subheader("Profile Configuration")
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        district = st.text_input("District / City")
        land_in_hectors = st.number_input("Land in Hectares", min_value=0.0, step=0.01, format="%.2f")
        password = st.text_input("Password", type="password")
        re_password = st.text_input("Confirm Password", type="password")
        
        submit = st.form_submit_button("Submit Registration", use_container_width=True)
        
        if submit:
            if not (name and email and district and password and re_password):
                st.warning("All data fields must be populated.")
            elif password != re_password:
                st.error("Configuration Error: Passwords are not identical.")
            else:
                try:
                    pydantic_payload = {
                        "name": name,
                        "email": email,
                        "district": district,
                        "land_in_hectors": float(land_in_hectors),
                        "password": password,
                        "re_password": re_password
                    }
                    response = requests.post(f"{FASTAPI_URL}/register", json=pydantic_payload)
                    
                    if response.status_code == 201:
                        st.success("Account created successfully.")
                        
                        # REDIRECT TARGET LOCK-IN FOR SUCCESSFUL HANDSHAKES
                        st.switch_page("pages/Login.py")
                        
                    elif response.status_code == 422:
                        # Parse structured data validation error arrays thrown by Pydantic models
                        errors = response.json().get("detail", [])
                        for err in errors:
                            st.error(f"Field Validation Error ({err.get('loc')[-1]}): {err.get('msg')}")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Registration failed.')}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Connection Failure: Target backend is unreachable.")

    # --- NAVIGATION ACTIONS CONTAINER (OUTSIDE THE FORM BLOCK) ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Cancel and Return Home", use_container_width=True):
        st.switch_page("app.py")
