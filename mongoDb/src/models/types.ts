import { ObjectId } from 'mongodb';

export interface Patient {
  _id?: ObjectId;
  patient_id: string;
  first_name: string;
  last_name: string;
  dob: Date;
  gender: string;
  created_at: Date;
  updated_at: Date;
}

export interface Encounter {
  _id?: ObjectId;
  encounter_id: string;
  patient_id: string;
  visit_date: Date;
  doctor: string;
  notes?: string;
  created_at: Date;
}

export interface ECGTest {
  _id?: ObjectId;
  test_id: string;
  encounter_id: string;
  patient_id: string;
  test_date: Date;
  age: number;
  sex: number; // 1 = male, 0 = female
  cp: number; // chest pain type
  trestbps: number; // resting blood pressure
  chol: number; // cholesterol
  fbs: number; // fasting blood sugar
  restecg: number; // resting electrocardiographic results
  thalach: number; // maximum heart rate achieved
  exang: number; // exercise induced angina
  oldpeak: number; // ST depression induced by exercise
  slope: number; // slope of the peak exercise ST segment
  ca: number; // number of major vessels
  thal: number; // thalassemia
  target: number; // diagnosis of heart disease
  created_at: Date;
}

export interface AuditLog {
  _id?: ObjectId;
  log_id: string;
  action: string;
  object_type: string;
  object_id: string;
  user_id?: string;
  details?: any;
  ip_address?: string;
  user_agent?: string;
  logged_at: Date;
}

export interface CreatePatientData {
  first_name: string;
  last_name: string;
  dob: Date;
  gender: string;
}

export interface CreateEncounterData {
  patient_id: string;
  visit_date: Date;
  doctor: string;
  notes?: string;
}

export interface CreateECGTestData {
  encounter_id: string;
  patient_id: string;
  test_date: Date;
  age: number;
  sex: number;
  cp: number;
  trestbps: number;
  chol: number;
  fbs: number;
  restecg: number;
  thalach: number;
  exang: number;
  oldpeak: number;
  slope: number;
  ca: number;
  thal: number;
  target: number;
}

export interface CreateAuditLogData {
  action: string;
  object_type: string;
  object_id: string;
  user_id?: string;
  details?: any;
  ip_address?: string;
  user_agent?: string;
}