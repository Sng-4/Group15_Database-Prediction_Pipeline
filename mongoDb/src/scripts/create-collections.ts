import { connectDB } from '../config/database';

async function createCollections(): Promise<void> {
  try {
    const db = await connectDB();
    
    // Create collections (MongoDB creates them automatically on first insert)
    await db.createCollection('patients');
    await db.createCollection('encounters');
    await db.createCollection('ecg_tests');
    await db.createCollection('audit_logs');
    
    console.log('Collections created successfully');
  } catch (error) {
    console.error('Error creating collections:', error);
  }
}

createCollections();