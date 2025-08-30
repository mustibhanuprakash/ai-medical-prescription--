import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.title("💊 SafeMeds - Prescription OCR System")

# Upload prescription
st.header("📤 Upload Prescription")
uploaded_file = st.file_uploader("Upload prescription image", type=["jpg", "png", "jpeg"])

patient_name = st.text_input("👤 Patient Name")
age = st.number_input("🎂 Age", min_value=0, max_value=120, step=1)
dosage = st.text_input("💊 Dosage")

if st.button("Upload & Process"):
    if uploaded_file:
        files = {"file": uploaded_file.getvalue()}
        data = {"patient_name": patient_name, "age": age, "dosage": dosage}
        response = requests.post(f"{BACKEND_URL}/ocr/", files={"file": uploaded_file}, data=data)
        st.json(response.json())
    else:
        st.warning("⚠️ Please upload a file first.")

# Show saved prescriptions
st.header("📋 Saved Prescriptions")
if st.button("Get All Prescriptions"):
    response = requests.get(f"{BACKEND_URL}/prescriptions/")
    st.json(response.json())

# Search prescriptions
st.header("🔍 Search Prescriptions")
query = st.text_input("Enter search query (name or medicine)")
if st.button("Search"):
    response = requests.get(f"{BACKEND_URL}/search/", params={"query": query})
    st.json(response.json())
