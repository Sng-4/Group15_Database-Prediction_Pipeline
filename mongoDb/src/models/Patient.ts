import { ObjectId, InsertOneResult, UpdateResult, WithId } from 'mongodb';
import { connectDB } from '../config/database';
import { Patient, CreatePatientData } from './types';

export class PatientModel {
  static async create(patientData: CreatePatientData): Promise<InsertOneResult<Patient>> {
    const db = await connectDB();
    const result = await db.collection<Patient>('patients').insertOne({
      patient_id: `PAT_${Date.now()}`,
      ...patientData,
      created_at: new Date(),
      updated_at: new Date()
    });
    return result;
  }

  static async findById(patientId: string): Promise<WithId<Patient> | null> {
    const db = await connectDB();
    return await db.collection<Patient>('patients').findOne({ patient_id: patientId });
  }

  static async findByObjectId(objectId: string): Promise<WithId<Patient> | null> {
    const db = await connectDB();
    return await db.collection<Patient>('patients').findOne({ _id: new ObjectId(objectId) });
  }

  static async findByName(firstName: string, lastName: string): Promise<WithId<Patient>[]> {
    const db = await connectDB();
    return await db.collection<Patient>('patients').find({
      first_name: firstName,
      last_name: lastName
    }).toArray();
  }

  static async update(patientId: string, updateData: Partial<Omit<Patient, '_id' | 'patient_id' | 'created_at'>>): Promise<UpdateResult> {
    const db = await connectDB();
    const result = await db.collection<Patient>('patients').updateOne(
      { patient_id: patientId },
      { 
        $set: {
          ...updateData,
          updated_at: new Date()
        }
      }
    );
    return result;
  }

  static async delete(patientId: string): Promise<boolean> {
    const db = await connectDB();
    const result = await db.collection<Patient>('patients').deleteOne({ patient_id: patientId });
    return result.deletedCount === 1;
  }

  static async findAll(skip: number = 0, limit: number = 50): Promise<WithId<Patient>[]> {
    const db = await connectDB();
    return await db.collection<Patient>('patients')
      .find()
      .skip(skip)
      .limit(limit)
      .toArray();
  }
}

export default PatientModel;