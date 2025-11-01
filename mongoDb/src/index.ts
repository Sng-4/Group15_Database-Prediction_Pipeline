import { connectDB, closeDB } from './config/database';
import PatientModel from './models/Patient';
import EncounterModel from './models/Encounter';
import ECGTestModel from './models/ECGTest';
import AuditLogModel from './models/AuditLog';

async function main(): Promise<void> {
  try {
    await connectDB();
    console.log('Heart Disease Database Application Started');
    
    // Example usage
    const patientResult = await PatientModel.create({
      first_name: 'John',
      last_name: 'Doe',
      dob: new Date('1980-05-15'),
      gender: 'Male'
    });
    
    console.log('Created patient:', patientResult.insertedId);
    
  } catch (error) {
    console.error('Application error:', error);
  } finally {
    await closeDB();
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nShutting down gracefully...');
  await closeDB();
  process.exit(0);
});

main();