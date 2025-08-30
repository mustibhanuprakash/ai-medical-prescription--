from fastapi import FastAPI, UploadFile, File, Depends, Form, Query
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import shutil
import os
from PIL import Image
import pytesseract
from fastapi.responses import FileResponse
from fpdf import FPDF

app = FastAPI()

# ✅ Create DB tables
Base.metadata.create_all(bind=engine)


# ✅ Upload + OCR + Save to DB
@app.post("/ocr/")
async def upload_prescription(
    file: UploadFile = File(...),
    patient_name: str = Form("Unknown"),
    age: int = Form(0),
    dosage: str = Form("Not specified"),
    db: Session = Depends(get_db)
):
    # Save uploaded file temporarily
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # OCR using pytesseract
    img = Image.open(file_location)
    text = pytesseract.image_to_string(img)

    # Save result in DB
    new_prescription = models.Prescription(
        patient_name=patient_name,
        age=age,
        dosage=dosage,
        medicines=text
    )
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)

    # Remove temp file
    os.remove(file_location)

    return {
        "id": new_prescription.id,
        "patient_name": new_prescription.patient_name,
        "age": new_prescription.age,
        "dosage": new_prescription.dosage,
        "extracted_text": text
    }


# ✅ Get all prescriptions
@app.get("/prescriptions/")
def get_prescriptions(db: Session = Depends(get_db)):
    prescriptions = db.query(models.Prescription).all()
    return prescriptions


# ✅ Download prescription as PDF
@app.get("/download/{prescription_id}")
def download_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()
    if not prescription:
        return {"error": "Prescription not found"}

    # Create folder if not exists
    os.makedirs("prescriptions", exist_ok=True)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="💊 Prescription Report", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"👤 Patient Name: {prescription.patient_name}", ln=True)
    pdf.cell(200, 10, txt=f"🎂 Age: {prescription.age}", ln=True)
    pdf.cell(200, 10, txt=f"💊 Dosage: {prescription.dosage}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"📄 Medicines:\n{prescription.medicines}")

    # Save PDF into folder
    file_path = f"prescriptions/prescription_{prescription.id}.pdf"
    pdf.output(file_path)

    return FileResponse(file_path, media_type="application/pdf", filename=f"prescription_{prescription.id}.pdf")


# ✅ 🔍 Search API
@app.get("/search/")
def search_prescriptions(
    query: str = Query(..., description="Search by patient name or medicine"),
    db: Session = Depends(get_db)
):
    results = db.query(models.Prescription).filter(
        (models.Prescription.patient_name.ilike(f"%{query}%")) |
        (models.Prescription.medicines.ilike(f"%{query}%"))
    ).all()

    return results
