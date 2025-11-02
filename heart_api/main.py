from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date
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