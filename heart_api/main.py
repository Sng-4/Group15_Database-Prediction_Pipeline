from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date
import mysql.connector

app = FastAPI(title="Heart Disease SQL API")

# --- Connect to the hosted SQL database ---
sql_conn = mysql.connector.connect(
    host="your_host",
    user="your_user",
    password="your_password",
    database="heart_disease_db"
)
sql_cursor = sql_conn.cursor(dictionary=True)