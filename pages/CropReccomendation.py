import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")

# 1. Page Configuration
st.set_page_config(page_title="Crop Recommendation", layout="wide")

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
st.subheader("Crop Recommendation Engine")
st.markdown("---")
st.write("Provide the specific environmental and soil parameters below to execute the model pipeline.")

# 2-Column Form Grid Layout
form_col1, form_col2 = st.columns(2)

with st.form("recommendation_form", clear_on_submit=False):
    with form_col1:
        st.markdown("##### Soil Metrics")
        n = st.number_input("Nitrogen (N) level in soil", min_value=0.0, step=1.0, format="%.2f", value=90.0)
        p = st.number_input("Phosphorus (P) level in soil", min_value=0.0, step=1.0, format="%.2f", value=42.0)
        k = st.number_input("Potassium (K) level in soil", min_value=0.0, step=1.0, format="%.2f", value=43.0)
        ph = st.number_input("pH level of soil", min_value=0.0, max_value=14.0, step=0.1, format="%.2f", value=6.5)

    with form_col2:
        st.markdown("##### Climate Metrics")
        temperature = st.number_input("Temperature in Celsius", min_value=0.0, step=0.1, format="%.2f", value=20.0)
        humidity = st.number_input("Humidity percentage", min_value=0.0, max_value=100.0, step=0.1, format="%.2f", value=82.0)
        rainfall = st.number_input("Rainfall in mm", min_value=0.0, step=1.0, format="%.2f", value=202.0)

    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.form_submit_button("Execute Prediction Pipeline", use_container_width=True)

    if submit:
        try:
            # Pydantic CropRecommendModel schema mapping
            pydantic_payload = {
                "N": float(n),
                "P": float(p),
                "K": float(k),
                "temperature": float(temperature),
                "humidity": float(humidity),
                "ph": float(ph),
                "rainfall": float(rainfall)
            }

            # Setup HTTP Bearer Token headers for current_user dependency
            headers = {
                "Authorization": f"Bearer {st.session_state.jwt_token}"
            }

            # Execute Request to backend endpoint path
            response = requests.post(
                f"{FASTAPI_URL}/predict/Crop_recommendation",
                json=pydantic_payload,
                headers=headers
            )

            if response.status_code == 200:
                result_data = response.json()
                
                # Matches your response model: CropPredicted -> predicted_output
                predicted_output = result_data.get("predicted_output", {})
                
                # Extract fields mapping to your PredictedOutput schema
                crop = predicted_output.get("prediction", "Unknown")
                confidence = predicted_output.get("confidence", 0.0)

                st.markdown("---")
                st.subheader("Pipeline Output Results")
                
                # Clean structural metric allocation matrix grid
                res_col1, res_col2 = st.columns(2)
                res_col1.metric(label="Recommended Crop Allocation", value=str(crop))
                res_col2.metric(label="Model Confidence Score", value=f"{float(confidence):.2f}%" if isinstance(confidence, (int, float)) else str(confidence))
                
                st.success(result_data.get("message", "Inference executed successfully."))

            elif response.status_code == 422:
                st.error("Validation Error: Input variables failed backend structural constraints.")
                errors = response.json().get("detail", [])
                for err in errors:
                    st.error(f"Field Error ({err.get('loc')[-1]}): {err.get('msg')}")
                    
            elif response.status_code == 500:
                error_detail = response.json().get("detail", "Internal Operational Error.")
                st.error(f"Server Operational Error (500): {error_detail}")
                
            else:
                st.error(f"Unexpected operational status error code: {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("Connection Failure: Target backend predictive service is unreachable.")
