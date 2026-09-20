import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")

# 1. Page Configuration
st.set_page_config(page_title="Crop Production", layout="wide")

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
st.subheader("Crop Production Forecasting Engine")
st.markdown("---")
st.write("Provide the geographical, temporal, and seasonal constraints below to forecast target production yield capacity metrics.")

# 2-Column Form Grid Layout
form_col1, form_col2 = st.columns(2)

with st.form("production_form", clear_on_submit=False):
    with form_col1:
        st.markdown("##### Regional and Temporal Controls")
        # Direct string value names will be transformed to title case via backend validation hooks
        district_name = st.text_input("District Name", placeholder="e.g. Khargone")
        crop_year = st.number_input("Crop Year", min_value=1900, max_value=2100, step=1, value=2026)
        
        # Season selection strictly locked to your backend Literal values
        season = st.selectbox(
            "Season of Crop", 
            ["Whole Year", "Kharif", "Rabi"]
        )

    with form_col2:
        st.markdown("##### Crop and Area Metrics")
        crop = st.text_input("Crop Type", placeholder="e.g. Rice")
        area = st.number_input("Area in Hectares", min_value=0.0, step=0.01, format="%.2f", value=2.0)

    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.form_submit_button("Execute Yield Forecasting Pipeline", use_container_width=True)

    if submit:
        if not (district_name and crop):
            st.warning("All string and numerical data fields must be populated.")
        else:
            try:
                # Pydantic CropProductionModel structural schema mapping payload
                pydantic_payload = {
                    "District_Name": str(district_name),
                    "Crop_Year": int(crop_year),
                    "Season": str(season),
                    "Crop": str(crop),
                    "Area": float(area)
                }

                # Setup HTTP Bearer Token authentication header criteria
                headers = {
                    "Authorization": f"Bearer {st.session_state.jwt_token}"
                }

                # Dispatch POST network call mapping payload arrays
                response = requests.post(
                    f"{FASTAPI_URL}/predict/Crop_Production",
                    json=pydantic_payload,
                    headers=headers
                )

                # Process backend operational context response matrices
                if response.status_code == 200:
                    result_data = response.json()
                    
                    # Matches your endpoint JSONResponse output mapping: "prediction_output"
                    prediction_output = result_data.get("prediction_output", {})
                    
                    total_prediction = prediction_output.get("prediction", 0.0)
                    per_hectare_yield = prediction_output.get("production_per_hectare", 0.0)

                    st.markdown("---")
                    st.subheader("Forecast Engine Output Results")
                    
                    # Structural metric presentation grids
                    res_col1, res_col2 = st.columns(2)
                    res_col1.metric(
                        label="Predicted Total Production (Metric Tonnes)", 
                        value=f"{float(total_prediction):.2f}"
                    )
                    res_col2.metric(
                        label="Yield Efficiency Per Hectare (Metric Tonnes / Ha)", 
                        value=f"{float(per_hectare_yield):.2f}"
                    )
                    
                    st.success(result_data.get("message", "Production forecast calculated successfully."))

                elif response.status_code == 422:
                    st.error("Validation Error: Input parameters failed backend structural parameters configuration.")
                    errors = response.json().get("detail", [])
                    for err in errors:
                        st.error(f"Field Constraints Error ({err.get('loc')[-1]}): {err.get('msg')}")
                        
                elif response.status_code == 500:
                    error_detail = response.json().get("detail", "Prediction tracking pipeline execution failure.")
                    st.error(f"Server Operational Error (500): {error_detail}")
                    
                else:
                    st.error(f"Unexpected operational status error code: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("Connection Failure: Target backend machine learning module is currently unreachable.")
