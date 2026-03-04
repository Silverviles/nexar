import api from '@/lib/axios';

const AUTH_BASE = '/v1/auth';

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
  emailVerified: boolean;
}

export interface LoginResponse {
  token: string;
  user: AuthUser;
}

export interface RegisterResponse {
  message: string;
}

export async function registerUser(
  email: string,
  password: string,
  name: string
): Promise<RegisterResponse> {
  const { data } = await api.post<RegisterResponse>(`${AUTH_BASE}/register`, {
    email,
    password,
    name,
  });
  return data;
}

export async function loginUser(
  email: string,
  password: string
): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>(`${AUTH_BASE}/login`, {
    email,
    password,
  });
  return data;
}

export async function googleAuth(code: string): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>(`${AUTH_BASE}/google`, {
    code,
  });
  return data;
}

export async function resendVerification(email: string): Promise<{ message: string }> {
  const { data } = await api.post<{ message: string }>(
    `${AUTH_BASE}/resend-verification`,
    { email }
  );
  return data;
}

export async function getMe(): Promise<AuthUser> {
  const { data } = await api.get<{ user: AuthUser }>(`${AUTH_BASE}/me`);
  return data.user;
}

export function getGoogleOAuthUrl(): string {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const redirectUri = `${window.location.origin}/auth/google/callback`;
  const scope = 'openid email profile';

  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope,
    access_type: 'offline',
    prompt: 'consent',
  });

  return `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
}
