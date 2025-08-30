import streamlit as st
import requests
import pandas as pd

st.title("💊 MediCheck - Prescription OCR")

# -----------------------------
# 📤 Upload Section
# -----------------------------
st.subheader("📤 Upload Prescription Image")
patient_name = st.text_input("👤 Enter Patient Name")
age = st.number_input("🎂 Enter Age", min_value=0, max_value=120, step=1)
dosage = st.text_input("💊 Enter Dosage Information")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    with open("temp.png", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image("temp.png", caption="Uploaded Prescription", use_column_width=True)

    if st.button("Extract Text"):
        if not patient_name:
            st.warning("⚠️ Please enter patient name before extracting!")
        else:
            with open("temp.png", "rb") as f:
                files = {"file": f}
                data = {"patient_name": patient_name, "age": age, "dosage": dosage}
                response = requests.post("http://127.0.0.1:8000/ocr/", files=files, data=data)

            if response.status_code == 200:
                data = response.json()
                st.success("✅ OCR Extracted Successfully!")
                st.write(f"👤 **Patient Name:** {data['patient_name']}")
                st.write(f"🎂 **Age:** {data['age']}")
                st.write(f"💊 **Dosage:** {data['dosage']}")
                st.write("📄 **Extracted Text:**")
                st.write(data["extracted_text"])

                # ✅ PDF download button
                pdf_url = f"http://127.0.0.1:8000/download/{data['id']}"
                pdf_response = requests.get(pdf_url)
                if pdf_response.status_code == 200:
                    st.download_button(
                        label="⬇️ Download Prescription as PDF",
                        data=pdf_response.content,
                        file_name=f"prescription_{data['id']}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error("❌ Failed to extract text")

# -----------------------------
# 📜 History Section
# -----------------------------
st.subheader("📜 Past Prescriptions")

if st.button("View History"):
    response = requests.get("http://127.0.0.1:8000/prescriptions/")
    if response.status_code == 200:
        data = response.json()
        if len(data) == 0:
            st.info("No prescriptions found yet.")
        else:
            # ✅ Display history in table format
            df = pd.DataFrame(data)
            st.dataframe(df[["id", "patient_name", "age", "dosage", "medicines"]])

            # ✅ Expanders + individual PDF download
            for item in data:
                with st.expander(f"🆔 {item['id']} - 👤 {item['patient_name']}"):
                    st.write(f"🎂 **Age:** {item.get('age', 'N/A')}")
                    st.write(f"💊 **Dosage:** {item.get('dosage', 'Not specified')}")
                    st.write(f"📄 **Medicines:** {item['medicines']}")

                    pdf_url = f"http://127.0.0.1:8000/download/{item['id']}"
                    pdf_response = requests.get(pdf_url)
                    if pdf_response.status_code == 200:
                        st.download_button(
                            label=f"⬇️ Download PDF (ID {item['id']})",
                            data=pdf_response.content,
                            file_name=f"prescription_{item['id']}.pdf",
                            mime="application/pdf"
                        )
    else:
        st.error("❌ Could not fetch history")
