import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { CheckCircle, XCircle, Clock, ArrowRight } from 'lucide-react';
import AuthLayout from '@/components/layout/AuthLayout';
import { resendVerification } from '@/services/auth-service';

type VerifyStatus = 'loading' | 'success' | 'already-verified' | 'expired' | 'error';

const VerifyEmail: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<VerifyStatus>('loading');
  const [message, setMessage] = useState('');
  const [expiredEmail, setExpiredEmail] = useState('');
  const [resendLoading, setResendLoading] = useState(false);
  const [resendMessage, setResendMessage] = useState('');

  useEffect(() => {
    const statusParam = searchParams.get('status');
    const messageParam = searchParams.get('message');
    const emailParam = searchParams.get('email');

    if (statusParam === 'success') {
      setStatus('success');
    } else if (statusParam === 'already-verified') {
      setStatus('already-verified');
    } else if (statusParam === 'expired') {
      setStatus('expired');
      if (emailParam) setExpiredEmail(emailParam);
    } else if (statusParam === 'error') {
      setStatus('error');
      setMessage(messageParam || 'Verification failed');
    } else {
      // No status param means direct page load without verification
      setStatus('error');
      setMessage('Invalid verification link');
    }
  }, [searchParams]);

  const handleResend = async () => {
    if (!expiredEmail) return;
    setResendLoading(true);
    setResendMessage('');
    try {
      await resendVerification(expiredEmail);
      setResendMessage('A new verification email has been sent. Please check your inbox.');
    } catch {
      setResendMessage('Failed to resend verification email. Please try again.');
    } finally {
      setResendLoading(false);
    }
  };

  const renderContent = () => {
    switch (status) {
      case 'loading':
        return (
          <div className="text-center space-y-4">
            <div className="h-12 w-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-muted-foreground">Verifying your email...</p>
          </div>
        );

      case 'success':
        return (
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              <div className="rounded-full bg-green-500/10 p-4">
                <CheckCircle className="h-12 w-12 text-green-500" />
              </div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold">Email verified</h2>
              <p className="text-muted-foreground">
                Your email has been successfully verified. You can now sign in to your account.
              </p>
            </div>
            <Link to="/signin">
              <Button className="w-full h-11">
                <span className="flex items-center gap-2">
                  Continue to sign in
                  <ArrowRight className="h-4 w-4" />
                </span>
              </Button>
            </Link>
          </div>
        );

      case 'already-verified':
        return (
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              <div className="rounded-full bg-primary/10 p-4">
                <CheckCircle className="h-12 w-12 text-primary" />
              </div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold">Already verified</h2>
              <p className="text-muted-foreground">
                Your email has already been verified. You can sign in to your account.
              </p>
            </div>
            <Link to="/signin">
              <Button className="w-full h-11">
                <span className="flex items-center gap-2">
                  Go to sign in
                  <ArrowRight className="h-4 w-4" />
                </span>
              </Button>
            </Link>
          </div>
        );

      case 'expired':
        return (
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              <div className="rounded-full bg-yellow-500/10 p-4">
                <Clock className="h-12 w-12 text-yellow-500" />
              </div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold">Link expired</h2>
              <p className="text-muted-foreground">
                This verification link has expired. Verification links are valid for 24 hours.
              </p>
            </div>
            {expiredEmail && (
              <div className="space-y-3">
                <Button
                  className="w-full h-11"
                  onClick={handleResend}
                  disabled={resendLoading}
                >
                  {resendLoading ? 'Sending...' : 'Resend verification email'}
                </Button>
                {resendMessage && (
                  <p className="text-sm text-muted-foreground">{resendMessage}</p>
                )}
              </div>
            )}
            <Link to="/signup" className="block">
              <Button variant="outline" className="w-full h-11">
                Register again
              </Button>
            </Link>
          </div>
        );

      case 'error':
        return (
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              <div className="rounded-full bg-destructive/10 p-4">
                <XCircle className="h-12 w-12 text-destructive" />
              </div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold">Verification failed</h2>
              <p className="text-muted-foreground">{message}</p>
            </div>
            <div className="space-y-3">
              <Link to="/signup">
                <Button className="w-full h-11">Create a new account</Button>
              </Link>
              <Link to="/signin">
                <Button variant="outline" className="w-full h-11">
                  Back to sign in
                </Button>
              </Link>
            </div>
          </div>
        );
    }
  };

  return (
    <AuthLayout
      title="Email Verification"
      description="Confirming your email address"
    >
      {renderContent()}
    </AuthLayout>
  );
};

export default VerifyEmail;
