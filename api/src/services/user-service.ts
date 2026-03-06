import { db } from '@config/firestore.js';
import { Timestamp } from '@google-cloud/firestore';
import crypto from 'crypto';

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
  const token = crypto.randomUUID();
  const expiry = Timestamp.fromMillis(Date.now() + VERIFICATION_TOKEN_EXPIRY_MS);
  return { token, expiry };
}

export async function findUserByEmail(email: string): Promise<UserDocument | null> {
  const snapshot = await db
    .collection(USERS_COLLECTION)
    .where('email', '==', email.toLowerCase())
    .limit(1)
    .get();

  if (snapshot.empty) return null;

  const doc = snapshot.docs[0]!;
  return { id: doc.id, ...doc.data() } as UserDocument;
}

export async function findUserById(id: string): Promise<UserDocument | null> {
  const doc = await db.collection(USERS_COLLECTION).doc(id).get();
  if (!doc.exists) return null;
  return { id: doc.id, ...doc.data() } as UserDocument;
}

export async function findUserByGoogleId(googleId: string): Promise<UserDocument | null> {
  const snapshot = await db
    .collection(USERS_COLLECTION)
    .where('googleId', '==', googleId)
    .limit(1)
    .get();

  if (snapshot.empty) return null;

  const doc = snapshot.docs[0]!;
  return { id: doc.id, ...doc.data() } as UserDocument;
}

export async function findUserByVerificationToken(token: string): Promise<UserDocument | null> {
  const snapshot = await db
    .collection(USERS_COLLECTION)
    .where('verificationToken', '==', token)
    .limit(1)
    .get();

  if (snapshot.empty) return null;

  const doc = snapshot.docs[0]!;
  return { id: doc.id, ...doc.data() } as UserDocument;
}

export async function createUser(input: CreateUserInput): Promise<{ user: UserDocument; verificationToken: string }> {
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

  const docRef = await db.collection(USERS_COLLECTION).add(userData);
  const user: UserDocument = { id: docRef.id, ...userData };

  return { user, verificationToken: token };
}

export async function createGoogleUser(input: CreateGoogleUserInput): Promise<UserDocument> {
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

  const docRef = await db.collection(USERS_COLLECTION).add(userData);
  return { id: docRef.id, ...userData };
}

export async function updateUnverifiedUser(
  userId: string,
  updates: { name: string; hashedPassword: string }
): Promise<string> {
  const { token, expiry } = generateVerificationToken();

  await db.collection(USERS_COLLECTION).doc(userId).update({
    name: updates.name,
    hashedPassword: updates.hashedPassword,
    verificationToken: token,
    verificationTokenExpiry: expiry,
    updatedAt: Timestamp.now(),
  });

  return token;
}

export async function markEmailVerified(userId: string): Promise<void> {
  await db.collection(USERS_COLLECTION).doc(userId).update({
    emailVerified: true,
    verificationToken: null,
    verificationTokenExpiry: null,
    updatedAt: Timestamp.now(),
  });
}

export async function refreshVerificationToken(userId: string): Promise<string> {
  const { token, expiry } = generateVerificationToken();

  await db.collection(USERS_COLLECTION).doc(userId).update({
    verificationToken: token,
    verificationTokenExpiry: expiry,
    updatedAt: Timestamp.now(),
  });

  return token;
}

export async function linkGoogleAccount(userId: string, googleId: string): Promise<void> {
  await db.collection(USERS_COLLECTION).doc(userId).update({
    googleId,
    emailVerified: true,
    verificationToken: null,
    verificationTokenExpiry: null,
    updatedAt: Timestamp.now(),
  });
}

export function isVerificationTokenExpired(user: UserDocument): boolean {
  if (!user.verificationTokenExpiry) return true;
  return Timestamp.now().toMillis() > user.verificationTokenExpiry.toMillis();
}

export function sanitizeUser(user: UserDocument) {
  return {
    id: user.id,
    email: user.email,
    name: user.name,
    role: user.role,
    emailVerified: user.emailVerified,
  };
}
