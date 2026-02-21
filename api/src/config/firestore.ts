import { Firestore } from '@google-cloud/firestore';

const projectId = process.env.GCP_PROJECT_ID || 'nexar-488119';

export const db = new Firestore({
  projectId,
  databaseId: '(default)',
});
