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
    password="",
    database="heart_disease_db"
)
sql_cursor = sql_conn.cursor(dictionary=True)
class Patient(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    dob: date
    gender: str = Field(..., pattern="^(Male|Female|Other)$") 
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

@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):
    return read_patient(patient_id)

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

@app.post("/ecg_tests/")
def create_ecg_test(test: ECGTest):
    sql_cursor.execute("SELECT * FROM encounters WHERE encounter_id=%s", (test.encounter_id,))
    if not sql_cursor.fetchone():
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    sql_cursor.execute("""
        INSERT INTO ecg_tests (encounter_id, age, sex, cp, trestbps, chol, fbs, restecg, thalach,
                               exang, oldpeak, slope, ca, thal, target)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (test.encounter_id, test.age, test.sex, test.cp, test.trestbps, test.chol, test.fbs,
          test.restecg, test.thalach, test.exang, test.oldpeak, test.slope, test.ca, test.thal, test.target))
    sql_conn.commit()
    
    sql_cursor.execute("SELECT LAST_INSERT_ID() AS test_id")
    new_id = sql_cursor.fetchone()["test_id"]
    return {"test_id": new_id, "message": "ECG Test created successfully"}

@app.get("/ecg_tests/{test_id}")
def read_ecg_test(test_id: int):
    sql_cursor.execute("SELECT * FROM ecg_tests WHERE test_id=%s", (test_id,))
    test = sql_cursor.fetchone()
    if not test:
        raise HTTPException(status_code=404, detail="ECG Test not found")
    return test

@app.get("/ecg_tests/latest")
def read_latest_ecg_test():
    sql_cursor.execute("SELECT * FROM ecg_tests ORDER BY test_id DESC LIMIT 1")
    test = sql_cursor.fetchone()
    if not test:
        raise HTTPException(status_code=404, detail="No ECG Tests found")
    return test

@app.put("/ecg_tests/{test_id}")
def update_ecg_test(test_id: int, test: ECGTest):
    sql_cursor.execute("SELECT * FROM encounters WHERE encounter_id=%s", (test.encounter_id,))
    if not sql_cursor.fetchone():
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    sql_cursor.execute("""
        UPDATE ecg_tests
        SET encounter_id=%s, age=%s, sex=%s, cp=%s, trestbps=%s, chol=%s, fbs=%s,
            restecg=%s, thalach=%s, exang=%s, oldpeak=%s, slope=%s, ca=%s, thal=%s, target=%s
        WHERE test_id=%s
    """, (test.encounter_id, test.age, test.sex, test.cp, test.trestbps, test.chol, test.fbs,
          test.restecg, test.thalach, test.exang, test.oldpeak, test.slope, test.ca, test.thal, test.target, test_id))
    sql_conn.commit()
    
    if sql_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="ECG Test not found")
    return {"message": "ECG Test updated successfully"}

@app.delete("/ecg_tests/{test_id}")
def delete_ecg_test(test_id: int):
    sql_cursor.execute("DELETE FROM ecg_tests WHERE test_id=%s", (test_id,))
    sql_conn.commit()
    if sql_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="ECG Test not found")
    return {"message": "ECG Test deleted successfully"}