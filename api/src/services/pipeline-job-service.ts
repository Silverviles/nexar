/**
 * Pipeline Job Service
 *
 * Firestore CRUD for async pipeline jobs.
 * Each pipeline run is stored as a document in the `pipeline_jobs` collection,
 * updated progressively as each stage (analysis → decision) completes.
 */

import { db } from "@config/firestore.js";
import { Timestamp } from "@google-cloud/firestore";
import { logger } from "@config/logger.js";

const COLLECTION = "pipeline_jobs";

// ── Document shape ──

export interface PipelineJobDocument {
  pipeline_id: string;
  user_id: string;
  code: string;
  status: "processing" | "analyzing" | "deciding" | "completed" | "failed";
  analysis: Record<string, any> | null;
  decision: Record<string, any> | null;
  mapped_input: Record<string, any> | null;
  error: string | null;
  timing: {
    analysis_ms: number | null;
    decision_ms: number | null;
    total_ms: number | null;
  };
  created_at: any;
  updated_at: any;
}

// ── Create ──

export async function createPipelineJob(
  pipelineId: string,
  userId: string,
  code: string
): Promise<void> {
  const doc: PipelineJobDocument = {
    pipeline_id: pipelineId,
    user_id: userId,
    code,
    status: "processing",
    analysis: null,
    decision: null,
    mapped_input: null,
    error: null,
    timing: { analysis_ms: null, decision_ms: null, total_ms: null },
    created_at: Timestamp.now(),
    updated_at: Timestamp.now(),
  };

  await db.collection(COLLECTION).doc(pipelineId).set(doc);
  logger.debug("[PipelineJob] Created job %s", pipelineId);
}

// ── Update ──

export async function updatePipelineJob(
  pipelineId: string,
  updates: Partial<Omit<PipelineJobDocument, "pipeline_id" | "user_id" | "code" | "created_at">>
): Promise<void> {
  await db.collection(COLLECTION).doc(pipelineId).update({
    ...updates,
    updated_at: Timestamp.now(),
  });
  logger.debug("[PipelineJob] Updated job %s → status=%s", pipelineId, updates.status ?? "(unchanged)");
}

// ── Read ──

export async function getPipelineJob(
  pipelineId: string
): Promise<PipelineJobDocument | null> {
  const doc = await db.collection(COLLECTION).doc(pipelineId).get();
  if (!doc.exists) return null;

  const data = doc.data() as PipelineJobDocument;

  // Serialize Firestore Timestamps to ISO strings for JSON response
  return {
    ...data,
    created_at: data.created_at?.toDate?.()
      ? data.created_at.toDate().toISOString()
      : data.created_at,
    updated_at: data.updated_at?.toDate?.()
      ? data.updated_at.toDate().toISOString()
      : data.updated_at,
  };
}
