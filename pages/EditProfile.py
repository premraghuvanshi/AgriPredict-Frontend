import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")

# 1. Page Configuration
st.set_page_config(page_title="Edit Profile", layout="wide")

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
st.subheader("Modify Account Profile")
st.markdown("---")
st.write("Update your profile attributes below and submit to execute the modification pipeline.")

# Setup HTTP Bearer Token authentication header
headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}

# First, fetch the current values from view_profile to pre-populate the inputs
@st.cache_data(show_spinner=False)
def get_current_profile_data(token_auth):
    try:
        response = requests.get(f"{FASTAPI_URL}/view_profile", headers={"Authorization": f"Bearer {token_auth}"})
        if response.status_code == 200:
            return response.json().get("user_data", {})
    except requests.exceptions.ConnectionError:
        pass
    return {}

current_data = get_current_profile_data(st.session_state.jwt_token)

# 2-Column Form Grid Layout
col1, col2 = st.columns(2)

with st.form("edit_profile_form", clear_on_submit=False):
    with col1:
        st.markdown("##### Personal Identification")
        # Editable name field matching EditProfileModel
        name = st.text_input("Full Name", value=str(current_data.get("name", "")))
        
        # Read-only Email Field (Not part of EditProfileModel updates)
        st.text_input("Email Address (Unchangeable)", value=str(current_data.get("email", st.session_state.user_info.get("email", ""))), disabled=True)
        
    with col2:
        st.markdown("##### Regional Parameters")
        # Editable district and land fields matching EditProfileModel
        district = st.text_input("District / City", value=str(current_data.get("district", "")))
        land_in_hectares = st.number_input(
            "Land in hectares", 
            min_value=0.0, 
            step=0.01, 
            format="%.2f", 
            value=float(current_data.get("land_in_hectares", 0.0))
        )

    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.form_submit_button("Save Modification Changes", use_container_width=True)

    if submit:
        if not (name and district):
            st.warning("All modification text parameters must be populated.")
        else:
            try:
                # Pydantic EditProfileModel structural schema mapping payload
                pydantic_payload = {
                    "name": str(name),
                    "district": str(district),
                    "land_in_hectares": float(land_in_hectares)
                }

                # Dispatch PUT network call mapping configuration parameters
                response = requests.put(
                    f"{FASTAPI_URL}/edit_profile",
                    json=pydantic_payload,
                    headers=headers
                )

                if response.status_code == 200:
                    st.success(response.json().get("message", "Profile updated successfully."))
                    # Clear profile cache so that the new values appear immediately on reload
                    st.cache_data.clear()
                    st.info("👉 Redirecting back to profile view...")
                    st.switch_page("pages/ViewProfile.py")
                    
                elif response.status_code == 422:
                    st.error("Validation Error: Configuration fields failed backend constraints mapping.")
                    errors = response.json().get("detail", [])
                    for err in errors:
                        st.error(f"Field Error ({err.get('loc')[-1]}): {err.get('msg')}")
                        
                elif response.status_code == 500:
                    error_detail = response.json().get("detail", "Internal profile storage pipeline failure.")
                    st.error(f"Server Operational Error (500): {error_detail}")
                    
                else:
                    st.error(f"Unexpected operational status error code: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("Connection Failure: Target backend profile gateway database is unreachable.")

# --- NAVIGATION ACTIONS CONTAINER (OUTSIDE THE FORM BLOCK) ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Cancel and Back to Profile", use_container_width=True):
    st.switch_page("pages/ViewProfile.py")
