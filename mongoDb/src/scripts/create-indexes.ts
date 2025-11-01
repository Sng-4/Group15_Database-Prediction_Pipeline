import { connectDB } from '../config/database';

async function createIndexes(): Promise<void> {
  try {
    const db = await connectDB();
    
    // Patients indexes
    await db.collection('patients').createIndex({ "patient_id": 1 }, { unique: true });
    await db.collection('patients').createIndex({ "last_name": 1, "first_name": 1 });
    await db.collection('patients').createIndex({ "dob": 1 });
    await db.collection('patients').createIndex({ "gender": 1 });
    
    // Encounters indexes
    await db.collection('encounters').createIndex({ "encounter_id": 1 }, { unique: true });
    await db.collection('encounters').createIndex({ "patient_id": 1 });
    await db.collection('encounters').createIndex({ "visit_date": 1 });
    await db.collection('encounters').createIndex({ "doctor": 1 });
    await db.collection('encounters').createIndex({ "patient_id": 1, "visit_date": -1 });
    
    // ECG Tests indexes
    await db.collection('ecg_tests').createIndex({ "test_id": 1 }, { unique: true });
    await db.collection('ecg_tests').createIndex({ "encounter_id": 1 });
    await db.collection('ecg_tests').createIndex({ "patient_id": 1 });
    await db.collection('ecg_tests').createIndex({ "test_date": 1 });
    await db.collection('ecg_tests').createIndex({ "target": 1 });
    await db.collection('ecg_tests').createIndex({ "patient_id": 1, "test_date": -1 });
    
    // Audit Logs indexes
    await db.collection('audit_logs').createIndex({ "log_id": 1 }, { unique: true });
    await db.collection('audit_logs').createIndex({ "action": 1 });
    await db.collection('audit_logs').createIndex({ "object_type": 1, "object_id": 1 });
    await db.collection('audit_logs').createIndex({ "logged_at": -1 });
    await db.collection('audit_logs').createIndex({ "user_id": 1 });
    
    console.log('Indexes created successfully');
  } catch (error) {
    console.error('Error creating indexes:', error);
  }
}

createIndexes();