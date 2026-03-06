import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Alert, AlertDescription } from '@/components/ui/alert';
import AuthLayout from '@/components/layout/AuthLayout';

const GoogleCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [error, setError] = useState('');
  const { loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get('code');
    const errorParam = searchParams.get('error');

    if (errorParam) {
      setError('Google sign-in was cancelled or failed. Please try again.');
      return;
    }

    if (!code) {
      setError('No authorization code received from Google.');
      return;
    }

    loginWithGoogle(code)
      .then(() => {
        navigate('/dashboard', { replace: true });
      })
      .catch((err: unknown) => {
        const axiosError = err as { response?: { data?: { error?: string } }; message?: string };
        setError(
          axiosError.response?.data?.error || axiosError.message || 'Google authentication failed'
        );
      });
  }, [searchParams, loginWithGoogle, navigate]);

  return (
    <AuthLayout
      title="Signing in with Google"
      description="Please wait while we authenticate your account"
    >
      <div className="text-center space-y-6">
        {error ? (
          <div className="space-y-4">
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
            <div className="space-y-2">
              <a
                href="/signin"
                className="block text-sm text-primary hover:underline"
              >
                Back to sign in
              </a>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="h-12 w-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-muted-foreground">Completing Google sign-in...</p>
          </div>
        )}
      </div>
    </AuthLayout>
  );
};

export default GoogleCallback;
