import { Firestore } from '@google-cloud/firestore';

const projectId = process.env.GCP_PROJECT_ID || 'nexar-488119';
const databaseId = process.env.FIRESTORE_DATABASE_ID || '(default)';

export const db = new Firestore({
  projectId,
  databaseId,
});
