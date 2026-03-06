import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Mail, ArrowLeft } from 'lucide-react';
import AuthLayout from '@/components/layout/AuthLayout';
import { resendVerification } from '@/services/auth-service';

const VerifyEmailNotice: React.FC = () => {
  const location = useLocation();
  const email = (location.state as { email?: string })?.email || '';
  const [resendLoading, setResendLoading] = useState(false);
  const [resendMessage, setResendMessage] = useState('');

  const handleResend = async () => {
    if (!email) return;
    setResendLoading(true);
    setResendMessage('');
    try {
      await resendVerification(email);
      setResendMessage('A new verification email has been sent.');
    } catch {
      setResendMessage('Failed to resend. Please try again.');
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Check your email"
      description="We sent you a verification link"
    >
      <div className="text-center space-y-6">
        <div className="flex justify-center">
          <div className="rounded-full bg-primary/10 p-4">
            <Mail className="h-12 w-12 text-primary" />
          </div>
        </div>

        <div className="space-y-2">
          <h2 className="text-2xl font-bold">Verify your email</h2>
          <p className="text-muted-foreground">
            We've sent a verification link to{' '}
            {email ? (
              <span className="font-medium text-foreground">{email}</span>
            ) : (
              'your email address'
            )}
            . Click the link in the email to activate your account.
          </p>
        </div>

        <div className="bg-muted/50 rounded-lg p-4 space-y-2">
          <p className="text-sm text-muted-foreground">
            The verification link will expire in <span className="font-medium text-foreground">24 hours</span>.
          </p>
          <p className="text-sm text-muted-foreground">
            Don't see the email? Check your spam folder.
          </p>
        </div>

        {email && (
          <div className="space-y-3">
            <Button
              variant="outline"
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

        <Link to="/signin" className="inline-flex items-center gap-2 text-sm text-primary hover:underline">
          <ArrowLeft className="h-4 w-4" />
          Back to sign in
        </Link>
      </div>
    </AuthLayout>
  );
};

export default VerifyEmailNotice;
