import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { getGoogleOAuthUrl } from '@/services/auth-service';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Lock, Mail, ArrowRight } from 'lucide-react';
import AuthLayout from '@/components/layout/AuthLayout';
import GoogleIcon from '@/components/ui/GoogleIcon';

const SignIn: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [showResend, setShowResend] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [resendMessage, setResendMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login, resendVerification } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setShowResend(false);
    setResendMessage('');
    setIsLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { error?: string; code?: string } }; message?: string };
      const errorCode = axiosError.response?.data?.code;
      const errorMessage = axiosError.response?.data?.error || axiosError.message || 'Failed to sign in';

      setError(errorMessage);

      if (errorCode === 'EMAIL_NOT_VERIFIED') {
        setShowResend(true);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendVerification = async () => {
    setResendLoading(true);
    setResendMessage('');
    try {
      await resendVerification(email);
      setResendMessage('Verification email sent. Please check your inbox.');
    } catch {
      setResendMessage('Failed to resend. Please try again.');
    } finally {
      setResendLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = getGoogleOAuthUrl();
  };

  return (
    <AuthLayout
      title="Welcome back"
      description="Enter your credentials to access your account"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>
              {error}
              {showResend && (
                <div className="mt-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleResendVerification}
                    disabled={resendLoading}
                    className="text-xs"
                  >
                    {resendLoading ? 'Sending...' : 'Resend verification email'}
                  </Button>
                </div>
              )}
              {resendMessage && (
                <p className="mt-2 text-xs">{resendMessage}</p>
              )}
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email address</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10 h-11"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">Password</Label>
              <Link to="#" className="text-sm text-primary hover:underline">
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10 h-11"
                required
              />
            </div>
          </div>
        </div>

        <Button type="submit" className="w-full h-11" disabled={isLoading}>
          {isLoading ? (
            <span className="flex items-center gap-2">
              <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              Signing in...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              Sign in
              <ArrowRight className="h-4 w-4" />
            </span>
          )}
        </Button>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <Separator />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
          </div>
        </div>

        <Button
          type="button"
          variant="outline"
          className="w-full h-11"
          onClick={handleGoogleLogin}
        >
          <GoogleIcon className="mr-2 h-4 w-4" />
          Continue with Google
        </Button>

        <div className="text-center text-sm">
          <span className="text-muted-foreground">Don't have an account? </span>
          <Link to="/signup" className="text-primary hover:underline font-medium">
            Create account
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
};

export default SignIn;
