from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Prescription(Base):
    __tablename__ = "prescriptions"   # Table name in DB

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True, default="Unknown")
    age = Column(Integer, default=0)   # 🆕 Patient age
    medicines = Column(String)
    dosage = Column(String, default="Not specified")  # 🆕 Dosage info
    created_at = Column(DateTime, default=datetime.utcnow)
