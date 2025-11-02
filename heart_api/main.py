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