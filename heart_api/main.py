from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, conint, confloat
from typing import Optional
from datetime import date, datetime
import mysql.connector

app = FastAPI(title="Heart Disease SQL API")

# --- Connect to the hosted SQL database ---
sql_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Naturi^06",
    database="heart_disease_db"
)
sql_cursor = sql_conn.cursor(dictionary=True)
class Patient(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    dob: date
    gender: str = Field(..., regex="^(Male|Female|Other)$") 
class Encounter(BaseModel):
    patient_id: int
    visit_date: datetime
    doctor: str
    notes: Optional[str] = None

class ECGTest(BaseModel):
    encounter_id: int
    age: int = Field(..., ge=0)
    sex: int = Field(..., ge=0, le=1)
    cp: int = Field(..., ge=0)
    trestbps: int = Field(..., ge=0)
    chol: int = Field(..., ge=0)
    fbs: int = Field(..., ge=0, le=1)
    restecg: int = Field(..., ge=0)
    thalach: int = Field(..., ge=0)
    exang: int = Field(..., ge=0, le=1)
    oldpeak: float = Field(..., ge=0)
    slope: int = Field(..., ge=0)
    ca: int = Field(..., ge=0)
    thal: int = Field(..., ge=0)
    target: int = Field(..., ge=0, le=1)

@app.post("/patients/")
def create_patient(patient: Patient):
    try:
        sql_cursor.callproc("insert_new_patient", [
            patient.first_name,
            patient.last_name,
            patient.dob,
            patient.gender
        ])
        sql_conn.commit()

        sql_cursor.execute("SELECT LAST_INSERT_ID() AS patient_id;")
        new_id = sql_cursor.fetchone()["patient_id"]

        return {"patient_id": new_id, "message": "Patient created successfully"}
    
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

def read_patient(patient_id: int):
    sql_cursor.execute("SELECT * FROM patients WHERE patient_id = %s;", (patient_id,))
    patient = sql_cursor.fetchone()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/patients/{patient_id}")
def update_patient(patient_id: int, patient: Patient):
    sql_cursor.execute("""
        UPDATE patients
        SET first_name=%s, last_name=%s, dob=%s, gender=%s
        WHERE patient_id=%s
    """, (patient.first_name, patient.last_name, patient.dob, patient.gender, patient_id))
    sql_conn.commit()

    if sql_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient updated successfully"}

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    sql_cursor.execute("DELETE FROM patients WHERE patient_id = %s;", (patient_id,))
    sql_conn.commit()

    if sql_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

@app.post("/encounters/")
def create_encounter(encounter: Encounter):
    sql_cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (encounter.patient_id,))
    if not sql_cursor.fetchone():
        raise HTTPException(status_code=404, detail="Patient not found")
    
    sql_cursor.execute("""
        INSERT INTO encounters (patient_id, visit_date, doctor, notes)
        VALUES (%s, %s, %s, %s)
    """, (encounter.patient_id, encounter.visit_date, encounter.doctor, encounter.notes))
    sql_conn.commit()
    
    sql_cursor.execute("SELECT LAST_INSERT_ID() AS encounter_id")
    new_id = sql_cursor.fetchone()["encounter_id"]
    return {"encounter_id": new_id, "message": "Encounter created successfully"}

@app.get("/encounters/{encounter_id}")
def read_encounter(encounter_id: int):
    sql_cursor.execute("SELECT * FROM encounters WHERE encounter_id=%s", (encounter_id,))
    encounter = sql_cursor.fetchone()
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter

@app.put("/encounters/{encounter_id}")
def update_encounter(encounter_id: int, encounter: Encounter):
    sql_cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (encounter.patient_id,))
    if not sql_cursor.fetchone():
        raise HTTPException(status_code=404, detail="Patient not found")
    
    sql_cursor.execute("""
        UPDATE encounters
        SET patient_id=%s, visit_date=%s, doctor=%s, notes=%s
        WHERE encounter_id=%s
    """, (encounter.patient_id, encounter.visit_date, encounter.doctor, encounter.notes, encounter_id))
    sql_conn.commit()
    if sql_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return {"message": "Encounter updated successfully"}

@app.delete("/encounters/{encounter_id}")
def delete_encounter(encounter_id: int):
    sql_cursor.execute("DELETE FROM encounters WHERE encounter_id=%s", (encounter_id,))
    sql_conn.commit()
    if sql_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return {"message": "Encounter deleted successfully"}