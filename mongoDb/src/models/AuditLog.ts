import { ObjectId, InsertOneResult, WithId } from 'mongodb';
import { connectDB } from '../config/database';
import { AuditLog, CreateAuditLogData } from './types';

export class AuditLogModel {
  static async create(logData: CreateAuditLogData): Promise<InsertOneResult<AuditLog>> {
    const db = await connectDB();
    const result = await db.collection<AuditLog>('audit_logs').insertOne({
      log_id: `LOG_${Date.now()}`,
      ...logData,
      logged_at: new Date()
    });
    return result;
  }

  static async findByObject(objectType: string, objectId: string): Promise<WithId<AuditLog>[]> {
    const db = await connectDB();
    return await db.collection<AuditLog>('audit_logs')
      .find({ 
        object_type: objectType,
        object_id: objectId 
      })
      .sort({ logged_at: -1 })
      .toArray();
  }

  static async findByDateRange(startDate: Date, endDate: Date): Promise<WithId<AuditLog>[]> {
    const db = await connectDB();
    return await db.collection<AuditLog>('audit_logs')
      .find({
        logged_at: {
          $gte: startDate,
          $lte: endDate
        }
      })
      .sort({ logged_at: -1 })
      .toArray();
  }

  static async findByAction(action: string): Promise<WithId<AuditLog>[]> {
    const db = await connectDB();
    return await db.collection<AuditLog>('audit_logs')
      .find({ action })
      .sort({ logged_at: -1 })
      .toArray();
  }

  static async findRecent(limit: number = 100): Promise<WithId<AuditLog>[]> {
    const db = await connectDB();
    return await db.collection<AuditLog>('audit_logs')
      .find()
      .sort({ logged_at: -1 })
      .limit(limit)
      .toArray();
  }
}

export default AuditLogModel;