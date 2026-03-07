import { db } from "@config/firestore.js";
import { Timestamp } from "@google-cloud/firestore";
import { logger } from "@config/logger.js";

const DECISION_LOGS_COLLECTION = "decision_logs";

// ─────────────────────────────────────────────
//  Interfaces
// ─────────────────────────────────────────────

export interface DecisionLogDocument {
  id: string;

  // Who made the request
  userId: string;

  // Input features (from CodeAnalysisInput)
  input: {
    problem_type: string;
    problem_size: number;
    qubits_required: number;
    circuit_depth: number;
    gate_count: number;
    cx_gate_ratio: number;
    superposition_score: number;
    entanglement_score: number;
    time_complexity: string;
    memory_requirement_mb: number;
  };

  // Prediction results
  prediction: {
    recommended_hardware: string;
    confidence: number;
    quantum_probability: number;
    classical_probability: number;
    rationale: string;
  };

  // Cost & time estimates
  estimated_execution_time_ms: number | null;
  estimated_cost_usd: number | null;

  // Alternatives
  alternatives: Array<{
    hardware: string;
    confidence: number;
    trade_off: string;
  }> | null;

  // Budget
  budget_limit_usd: number | null;

  // Status tracking
  status: "predicted" | "executed" | "failed";

  // Feedback (populated after actual execution)
  feedback: {
    actual_hardware_used: string | null;
    actual_execution_time_ms: number | null;
    actual_cost_usd: number | null;
    prediction_correct: boolean | null;
    notes: string | null;
  } | null;

  // Timestamps
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface CreateDecisionLogInput {
  userId: string;
  requestBody: any; // The original CodeAnalysisInput sent to decision-engine
  responseBody: any; // The DecisionEngineResponse from decision-engine
  budgetLimitUsd?: number;
}

export interface FeedbackInput {
  actual_hardware_used: string;
  actual_execution_time_ms: number;
  actual_cost_usd: number;
  notes?: string;
}

// ─────────────────────────────────────────────
//  CREATE — Log a prediction
// ─────────────────────────────────────────────

export async function logDecision(
  input: CreateDecisionLogInput,
): Promise<string> {
  logger.debug("Logging decision to Firestore", {
    collection: DECISION_LOGS_COLLECTION,
    userId: input.userId,
  });

  const now = Timestamp.now();

  const recommendation = input.responseBody?.recommendation;
  const logData: Omit<DecisionLogDocument, "id"> = {
    userId: input.userId,
    input: {
      problem_type: input.requestBody.problem_type,
      problem_size: input.requestBody.problem_size,
      qubits_required: input.requestBody.qubits_required,
      circuit_depth: input.requestBody.circuit_depth,
      gate_count: input.requestBody.gate_count,
      cx_gate_ratio: input.requestBody.cx_gate_ratio,
      superposition_score: input.requestBody.superposition_score,
      entanglement_score: input.requestBody.entanglement_score,
      time_complexity: input.requestBody.time_complexity,
      memory_requirement_mb: input.requestBody.memory_requirement_mb,
    },
    prediction: {
      recommended_hardware: recommendation?.recommended_hardware ?? "Unknown",
      confidence: recommendation?.confidence ?? 0,
      quantum_probability: recommendation?.quantum_probability ?? 0,
      classical_probability: recommendation?.classical_probability ?? 0,
      rationale: recommendation?.rationale ?? "",
    },
    estimated_execution_time_ms:
      input.responseBody?.estimated_execution_time_ms ?? null,
    estimated_cost_usd: input.responseBody?.estimated_cost_usd ?? null,
    alternatives: input.responseBody?.alternatives ?? null,
    budget_limit_usd: input.budgetLimitUsd ?? null,
    status: "predicted",
    feedback: null,
    createdAt: now,
    updatedAt: now,
  };

  const startTime = Date.now();
  const docRef = await db.collection(DECISION_LOGS_COLLECTION).add(logData);
  const durationMs = Date.now() - startTime;

  logger.info("Decision logged to Firestore", {
    decisionId: docRef.id,
    userId: input.userId,
    hardware: logData.prediction.recommended_hardware,
    confidence: logData.prediction.confidence,
    writeDurationMs: durationMs,
  });

  return docRef.id;
}

// ─────────────────────────────────────────────
//  READ — Get decision history
// ─────────────────────────────────────────────

export async function getDecisionHistory(
  userId: string,
  limit: number = 20,
  offset: number = 0,
  filters?: {
    hardware?: string;
    status?: string;
  },
): Promise<{ decisions: DecisionLogDocument[]; total: number }> {
  logger.debug("Fetching decision history from Firestore", {
    collection: DECISION_LOGS_COLLECTION,
    userId,
    limit,
    offset,
    filters,
  });

  const startTime = Date.now();

  // Query by userId only (avoids composite index requirement)
  const snapshot = await db
    .collection(DECISION_LOGS_COLLECTION)
    .where("userId", "==", userId)
    .get();

  // Convert to typed array
  let decisions = snapshot.docs.map((doc) => ({
    id: doc.id,
    ...doc.data(),
  })) as DecisionLogDocument[];

  // Apply filters client-side
  if (filters?.hardware) {
    decisions = decisions.filter(
      (d) => d.prediction.recommended_hardware === filters.hardware,
    );
  }
  if (filters?.status) {
    decisions = decisions.filter((d) => d.status === filters.status);
  }

  const total = decisions.length;

  // Sort by createdAt descending (client-side)
  decisions.sort((a, b) => {
    const aTime = a.createdAt?.toDate?.() ? a.createdAt.toDate().getTime() : 0;
    const bTime = b.createdAt?.toDate?.() ? b.createdAt.toDate().getTime() : 0;
    return bTime - aTime;
  });

  // Apply pagination
  decisions = decisions.slice(offset, offset + limit);

  const durationMs = Date.now() - startTime;

  logger.debug("Decision history fetched", {
    userId,
    count: decisions.length,
    total,
    queryDurationMs: durationMs,
  });

  return { decisions, total };
}

// ─────────────────────────────────────────────
//  READ — Get single decision
// ─────────────────────────────────────────────

export async function getDecisionById(
  decisionId: string,
): Promise<DecisionLogDocument | null> {
  logger.debug("Fetching decision by ID", {
    collection: DECISION_LOGS_COLLECTION,
    decisionId,
  });

  const doc = await db
    .collection(DECISION_LOGS_COLLECTION)
    .doc(decisionId)
    .get();

  if (!doc.exists) {
    logger.debug("Decision not found", { decisionId });
    return null;
  }

  return { id: doc.id, ...doc.data() } as DecisionLogDocument;
}

// ─────────────────────────────────────────────
//  UPDATE — Submit execution feedback
// ─────────────────────────────────────────────

export async function submitFeedback(
  decisionId: string,
  userId: string,
  feedback: FeedbackInput,
): Promise<boolean> {
  logger.debug("Submitting feedback to Firestore", {
    collection: DECISION_LOGS_COLLECTION,
    decisionId,
    userId,
  });

  // First verify the decision exists and belongs to user
  const decision = await getDecisionById(decisionId);
  if (!decision) {
    logger.warn("Feedback submission failed: decision not found", {
      decisionId,
    });
    return false;
  }
  if (decision.userId !== userId) {
    logger.warn("Feedback submission failed: user mismatch", {
      decisionId,
      userId,
    });
    return false;
  }

  // Determine if prediction was correct
  const predictionCorrect =
    decision.prediction.recommended_hardware.toLowerCase() ===
    feedback.actual_hardware_used.toLowerCase();

  const startTime = Date.now();
  await db
    .collection(DECISION_LOGS_COLLECTION)
    .doc(decisionId)
    .update({
      status: "executed",
      feedback: {
        actual_hardware_used: feedback.actual_hardware_used,
        actual_execution_time_ms: feedback.actual_execution_time_ms,
        actual_cost_usd: feedback.actual_cost_usd,
        prediction_correct: predictionCorrect,
        notes: feedback.notes ?? null,
      },
      updatedAt: Timestamp.now(),
    });
  const durationMs = Date.now() - startTime;

  logger.info("Feedback submitted successfully", {
    decisionId,
    predictionCorrect,
    writeDurationMs: durationMs,
  });

  return true;
}

// ─────────────────────────────────────────────
//  ANALYTICS — Accuracy & stats
// ─────────────────────────────────────────────

export async function getAccuracyStats(userId: string): Promise<{
  totalPredictions: number;
  totalWithFeedback: number;
  correctPredictions: number;
  accuracy: number;
  hardwareBreakdown: Record<
    string,
    { total: number; correct: number; accuracy: number }
  >;
  averageCostSavings: number;
  averageTimeDelta: number;
}> {
  logger.debug("Calculating accuracy stats", {
    collection: DECISION_LOGS_COLLECTION,
    userId,
  });

  const startTime = Date.now();
  const snapshot = await db
    .collection(DECISION_LOGS_COLLECTION)
    .where("userId", "==", userId)
    .get();

  const decisions = snapshot.docs.map(
    (doc) => doc.data() as Omit<DecisionLogDocument, "id">,
  );

  const totalPredictions = decisions.length;
  const withFeedback = decisions.filter(
    (d) => d.feedback !== null && d.feedback !== undefined,
  );
  const totalWithFeedback = withFeedback.length;
  const correctPredictions = withFeedback.filter(
    (d) => d.feedback?.prediction_correct === true,
  ).length;
  const accuracy =
    totalWithFeedback > 0 ? (correctPredictions / totalWithFeedback) * 100 : 0;

  // Hardware breakdown
  const hardwareBreakdown: Record<
    string,
    { total: number; correct: number; accuracy: number }
  > = {};
  for (const d of withFeedback) {
    const hw = d.prediction.recommended_hardware;
    if (!hardwareBreakdown[hw]) {
      hardwareBreakdown[hw] = { total: 0, correct: 0, accuracy: 0 };
    }
    hardwareBreakdown[hw]!.total += 1;
    if (d.feedback?.prediction_correct) {
      hardwareBreakdown[hw]!.correct += 1;
    }
  }
  for (const hw of Object.keys(hardwareBreakdown)) {
    const entry = hardwareBreakdown[hw]!;
    entry.accuracy = entry.total > 0 ? (entry.correct / entry.total) * 100 : 0;
  }

  // Average cost savings (predicted - actual)
  let totalCostDelta = 0;
  let totalTimeDelta = 0;
  let costCount = 0;
  let timeCount = 0;
  for (const d of withFeedback) {
    if (
      d.estimated_cost_usd !== null &&
      d.feedback &&
      d.feedback.actual_cost_usd !== null
    ) {
      totalCostDelta += d.estimated_cost_usd - d.feedback.actual_cost_usd;
      costCount++;
    }
    if (
      d.estimated_execution_time_ms !== null &&
      d.feedback &&
      d.feedback.actual_execution_time_ms !== null
    ) {
      totalTimeDelta +=
        d.estimated_execution_time_ms - d.feedback.actual_execution_time_ms;
      timeCount++;
    }
  }

  const durationMs = Date.now() - startTime;
  logger.debug("Accuracy stats calculated", {
    userId,
    totalPredictions,
    totalWithFeedback,
    accuracy: accuracy.toFixed(1),
    queryDurationMs: durationMs,
  });

  return {
    totalPredictions,
    totalWithFeedback,
    correctPredictions,
    accuracy: Math.round(accuracy * 10) / 10,
    hardwareBreakdown,
    averageCostSavings:
      costCount > 0
        ? Math.round((totalCostDelta / costCount) * 10000) / 10000
        : 0,
    averageTimeDelta:
      timeCount > 0 ? Math.round(totalTimeDelta / timeCount) : 0,
  };
}
