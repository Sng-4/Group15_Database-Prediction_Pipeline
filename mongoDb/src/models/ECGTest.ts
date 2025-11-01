import { ObjectId, InsertOneResult, WithId } from 'mongodb';
import { connectDB } from '../config/database';
import { ECGTest, CreateECGTestData } from './types';

export class ECGTestModel {
  static async create(ecgData: CreateECGTestData): Promise<InsertOneResult<ECGTest>> {
    const db = await connectDB();
    const result = await db.collection<ECGTest>('ecg_tests').insertOne({
      test_id: `ECG_${Date.now()}`,
      ...ecgData,
      created_at: new Date()
    });
    return result;
  }

  static async findByPatientId(patientId: string): Promise<WithId<ECGTest>[]> {
    const db = await connectDB();
    return await db.collection<ECGTest>('ecg_tests')
      .find({ patient_id: patientId })
      .sort({ test_date: -1 })
      .toArray();
  }

  static async findByEncounterId(encounterId: string): Promise<WithId<ECGTest>[]> {
    const db = await connectDB();
    return await db.collection<ECGTest>('ecg_tests').find({ encounter_id: encounterId }).toArray();
  }

  static async findById(testId: string): Promise<WithId<ECGTest> | null> {
    const db = await connectDB();
    return await db.collection<ECGTest>('ecg_tests').findOne({ test_id: testId });
  }

  static async findHeartDiseaseCases(): Promise<WithId<ECGTest>[]> {
    const db = await connectDB();
    return await db.collection<ECGTest>('ecg_tests').find({ target: 1 }).toArray();
  }

  static async findByTarget(target: number): Promise<WithId<ECGTest>[]> {
    const db = await connectDB();
    return await db.collection<ECGTest>('ecg_tests').find({ target }).toArray();
  }

  static async getStatistics(): Promise<{
    totalTests: number;
    heartDiseaseCases: number;
    averageAge: number;
    averageCholesterol: number;
  }> {
    const db = await connectDB();
    
    const totalTests = await db.collection<ECGTest>('ecg_tests').countDocuments();
    const heartDiseaseCases = await db.collection<ECGTest>('ecg_tests').countDocuments({ target: 1 });
    
    const ageStats = await db.collection<ECGTest>('ecg_tests').aggregate([
      { $group: { _id: null, avgAge: { $avg: '$age' } } }
    ]).toArray();
    
    const cholStats = await db.collection<ECGTest>('ecg_tests').aggregate([
      { $group: { _id: null, avgChol: { $avg: '$chol' } } }
    ]).toArray();

    return {
      totalTests,
      heartDiseaseCases,
      averageAge: ageStats[0]?.avgAge || 0,
      averageCholesterol: cholStats[0]?.avgChol || 0
    };
  }
}

export default ECGTestModel;