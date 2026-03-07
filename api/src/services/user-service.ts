import { db } from '@config/firestore.js';
import { Timestamp } from '@google-cloud/firestore';
import crypto from 'crypto';
import { logger } from '@config/logger.js';

const USERS_COLLECTION = 'users';
const VERIFICATION_TOKEN_EXPIRY_MS = 24 * 60 * 60 * 1000; // 24 hours

export interface UserDocument {
  id: string;
  email: string;
  name: string;
  role: string;
  hashedPassword: string | null;
  emailVerified: boolean;
  verificationToken: string | null;
  verificationTokenExpiry: Timestamp | null;
  googleId: string | null;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface CreateUserInput {
  email: string;
  name: string;
  hashedPassword: string;
}

export interface CreateGoogleUserInput {
  email: string;
  name: string;
  googleId: string;
}

function generateVerificationToken(): { token: string; expiry: Timestamp } {
  logger.debug("Generating verification token");
  const token = crypto.randomUUID();
  const expiry = Timestamp.fromMillis(Date.now() + VERIFICATION_TOKEN_EXPIRY_MS);
  logger.debug("Verification token generated", {
    tokenLength: token.length,
    expiresInMs: VERIFICATION_TOKEN_EXPIRY_MS,
  });
  return { token, expiry };
}

export async function findUserByEmail(email: string): Promise<UserDocument | null> {
  logger.debug("Querying Firestore: findUserByEmail", {
    collection: USERS_COLLECTION,
    filterField: 'email',
    email: email.toLowerCase(),
  });

  const startTime = Date.now();
  const snapshot = await db
    .collection(USERS_COLLECTION)
    .where('email', '==', email.toLowerCase())
    .limit(1)
    .get();

  const durationMs = Date.now() - startTime;

  if (snapshot.empty) {
    logger.debug("findUserByEmail: no user found", {
      email: email.toLowerCase(),
      queryDurationMs: durationMs,
    });
    return null;
  }

  const doc = snapshot.docs[0]!;
  logger.debug("findUserByEmail: user found", {
    userId: doc.id,
    email: email.toLowerCase(),
    queryDurationMs: durationMs,
  });
  return { id: doc.id, ...doc.data() } as UserDocument;
}

export async function findUserById(id: string): Promise<UserDocument | null> {
  logger.debug("Querying Firestore: findUserById", {
    collection: USERS_COLLECTION,
    userId: id,
  });

  const startTime = Date.now();
  const doc = await db.collection(USERS_COLLECTION).doc(id).get();
  const durationMs = Date.now() - startTime;

  if (!doc.exists) {
    logger.debug("findUserById: user not found", {
      userId: id,
      queryDurationMs: durationMs,
    });
    return null;
  }

  logger.debug("findUserById: user found", {
    userId: doc.id,
    queryDurationMs: durationMs,
  });
  return { id: doc.id, ...doc.data() } as UserDocument;
}

export async function findUserByGoogleId(googleId: string): Promise<UserDocument | null> {
  logger.debug("Querying Firestore: findUserByGoogleId", {
    collection: USERS_COLLECTION,
    filterField: 'googleId',
  });

  const startTime = Date.now();
  const snapshot = await db
    .collection(USERS_COLLECTION)
    .where('googleId', '==', googleId)
    .limit(1)
    .get();

  const durationMs = Date.now() - startTime;

  if (snapshot.empty) {
    logger.debug("findUserByGoogleId: no user found", {
      queryDurationMs: durationMs,
    });
    return null;
  }

  const doc = snapshot.docs[0]!;
  logger.debug("findUserByGoogleId: user found", {
    userId: doc.id,
    queryDurationMs: durationMs,
  });
  return { id: doc.id, ...doc.data() } as UserDocument;
}

export async function findUserByVerificationToken(token: string): Promise<UserDocument | null> {
  logger.debug("Querying Firestore: findUserByVerificationToken", {
    collection: USERS_COLLECTION,
    filterField: 'verificationToken',
    tokenLength: token.length,
  });

  const startTime = Date.now();
  const snapshot = await db
    .collection(USERS_COLLECTION)
    .where('verificationToken', '==', token)
    .limit(1)
    .get();

  const durationMs = Date.now() - startTime;

  if (snapshot.empty) {
    logger.debug("findUserByVerificationToken: no user found", {
      queryDurationMs: durationMs,
    });
    return null;
  }

  const doc = snapshot.docs[0]!;
  logger.debug("findUserByVerificationToken: user found", {
    userId: doc.id,
    queryDurationMs: durationMs,
  });
  return { id: doc.id, ...doc.data() } as UserDocument;
}

export async function createUser(input: CreateUserInput): Promise<{ user: UserDocument; verificationToken: string }> {
  logger.debug("Creating new user in Firestore", {
    collection: USERS_COLLECTION,
    email: input.email.toLowerCase(),
    name: input.name,
  });

  const { token, expiry } = generateVerificationToken();
  const now = Timestamp.now();

  const userData = {
    email: input.email.toLowerCase(),
    name: input.name,
    role: 'user',
    hashedPassword: input.hashedPassword,
    emailVerified: false,
    verificationToken: token,
    verificationTokenExpiry: expiry,
    googleId: null,
    createdAt: now,
    updatedAt: now,
  };

  const startTime = Date.now();
  const docRef = await db.collection(USERS_COLLECTION).add(userData);
  const durationMs = Date.now() - startTime;

  const user: UserDocument = { id: docRef.id, ...userData };

  logger.debug("User created successfully in Firestore", {
    userId: docRef.id,
    email: input.email.toLowerCase(),
    writeDurationMs: durationMs,
  });

  return { user, verificationToken: token };
}

export async function createGoogleUser(input: CreateGoogleUserInput): Promise<UserDocument> {
  logger.debug("Creating new Google user in Firestore", {
    collection: USERS_COLLECTION,
    email: input.email.toLowerCase(),
    name: input.name,
  });

  const now = Timestamp.now();

  const userData = {
    email: input.email.toLowerCase(),
    name: input.name,
    role: 'user',
    hashedPassword: null,
    emailVerified: true,
    verificationToken: null,
    verificationTokenExpiry: null,
    googleId: input.googleId,
    createdAt: now,
    updatedAt: now,
  };

  const startTime = Date.now();
  const docRef = await db.collection(USERS_COLLECTION).add(userData);
  const durationMs = Date.now() - startTime;

  logger.debug("Google user created successfully in Firestore", {
    userId: docRef.id,
    email: input.email.toLowerCase(),
    writeDurationMs: durationMs,
  });

  return { id: docRef.id, ...userData };
}

export async function updateUnverifiedUser(
  userId: string,
  updates: { name: string; hashedPassword: string }
): Promise<string> {
  logger.debug("Updating unverified user in Firestore", {
    collection: USERS_COLLECTION,
    userId,
    updatingFields: ['name', 'hashedPassword', 'verificationToken', 'verificationTokenExpiry', 'updatedAt'],
  });

  const { token, expiry } = generateVerificationToken();

  const startTime = Date.now();
  await db.collection(USERS_COLLECTION).doc(userId).update({
    name: updates.name,
    hashedPassword: updates.hashedPassword,
    verificationToken: token,
    verificationTokenExpiry: expiry,
    updatedAt: Timestamp.now(),
  });
  const durationMs = Date.now() - startTime;

  logger.debug("Unverified user updated successfully", {
    userId,
    writeDurationMs: durationMs,
  });

  return token;
}

export async function markEmailVerified(userId: string): Promise<void> {
  logger.debug("Marking email as verified in Firestore", {
    collection: USERS_COLLECTION,
    userId,
  });

  const startTime = Date.now();
  await db.collection(USERS_COLLECTION).doc(userId).update({
    emailVerified: true,
    verificationToken: null,
    verificationTokenExpiry: null,
    updatedAt: Timestamp.now(),
  });
  const durationMs = Date.now() - startTime;

  logger.debug("Email marked as verified successfully", {
    userId,
    writeDurationMs: durationMs,
  });
}

export async function refreshVerificationToken(userId: string): Promise<string> {
  logger.debug("Refreshing verification token in Firestore", {
    collection: USERS_COLLECTION,
    userId,
  });

  const { token, expiry } = generateVerificationToken();

  const startTime = Date.now();
  await db.collection(USERS_COLLECTION).doc(userId).update({
    verificationToken: token,
    verificationTokenExpiry: expiry,
    updatedAt: Timestamp.now(),
  });
  const durationMs = Date.now() - startTime;

  logger.debug("Verification token refreshed successfully", {
    userId,
    writeDurationMs: durationMs,
  });

  return token;
}

export async function linkGoogleAccount(userId: string, googleId: string): Promise<void> {
  logger.debug("Linking Google account in Firestore", {
    collection: USERS_COLLECTION,
    userId,
  });

  const startTime = Date.now();
  await db.collection(USERS_COLLECTION).doc(userId).update({
    googleId,
    emailVerified: true,
    verificationToken: null,
    verificationTokenExpiry: null,
    updatedAt: Timestamp.now(),
  });
  const durationMs = Date.now() - startTime;

  logger.debug("Google account linked successfully", {
    userId,
    writeDurationMs: durationMs,
  });
}

export function isVerificationTokenExpired(user: UserDocument): boolean {
  if (!user.verificationTokenExpiry) {
    logger.debug("Verification token expiry check: no expiry set (treating as expired)", {
      userId: user.id,
    });
    return true;
  }

  const isExpired = Timestamp.now().toMillis() > user.verificationTokenExpiry.toMillis();
  logger.debug("Verification token expiry check", {
    userId: user.id,
    isExpired,
    expiryTime: user.verificationTokenExpiry.toDate().toISOString(),
  });
  return isExpired;
}

export function sanitizeUser(user: UserDocument) {
  logger.debug("Sanitizing user document for response", { userId: user.id });
  return {
    id: user.id,
    email: user.email,
    name: user.name,
    role: user.role,
    emailVerified: user.emailVerified,
  };
}
