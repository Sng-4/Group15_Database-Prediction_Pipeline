import { ObjectId, InsertOneResult, WithId } from 'mongodb';
import { connectDB } from '../config/database';
import { Encounter, CreateEncounterData } from './types';

export class EncounterModel {
  static async create(encounterData: CreateEncounterData): Promise<InsertOneResult<Encounter>> {
    const db = await connectDB();
    const result = await db.collection<Encounter>('encounters').insertOne({
      encounter_id: `ENC_${Date.now()}`,
      ...encounterData,
      created_at: new Date()
    });
    return result;
  }

  static async findByPatientId(patientId: string): Promise<WithId<Encounter>[]> {
    const db = await connectDB();
    return await db.collection<Encounter>('encounters')
      .find({ patient_id: patientId })
      .sort({ visit_date: -1 })
      .toArray();
  }

  static async findById(encounterId: string): Promise<WithId<Encounter> | null> {
    const db = await connectDB();
    return await db.collection<Encounter>('encounters').findOne({ encounter_id: encounterId });
  }

  static async findByObjectId(objectId: string): Promise<WithId<Encounter> | null> {
    const db = await connectDB();
    return await db.collection<Encounter>('encounters').findOne({ _id: new ObjectId(objectId) });
  }

  static async updateNotes(encounterId: string, notes: string): Promise<boolean> {
    const db = await connectDB();
    const result = await db.collection<Encounter>('encounters').updateOne(
      { encounter_id: encounterId },
      { $set: { notes } }
    );
    return result.modifiedCount === 1;
  }

  static async delete(encounterId: string): Promise<boolean> {
    const db = await connectDB();
    const result = await db.collection<Encounter>('encounters').deleteOne({ encounter_id: encounterId });
    return result.deletedCount === 1;
  }
}

export default EncounterModel;