import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { CheckCircle, XCircle, Clock, ArrowRight } from 'lucide-react'
import AuthLayout from '@/components/layout/AuthLayout'
import { resendVerification } from '@/services/auth-service'

type VerifyStatus = 'loading' | 'success' | 'already-verified' | 'expired' | 'error'

const VALID_STATUSES = ['success', 'already-verified', 'expired', 'error'] as const
type ValidQueryStatus = (typeof VALID_STATUSES)[number]

function isValidStatus(value: string | null): value is ValidQueryStatus {
  return VALID_STATUSES.includes(value as ValidQueryStatus)
}

const MAX_MESSAGE_LENGTH = 200

function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState<VerifyStatus>('loading')
  const [message, setMessage] = useState('')
  const [expiredEmail, setExpiredEmail] = useState('')
  const [resendLoading, setResendLoading] = useState(false)
  const [resendMessage, setResendMessage] = useState('')

  useEffect(() => {
    const statusParam = searchParams.get('status')
    const messageParam = searchParams.get('message')
    const emailParam = searchParams.get('email')

    if (!isValidStatus(statusParam)) {
      setStatus('error')
      setMessage('Invalid verification link')
      return
    }

    if (statusParam === 'success') {
      setStatus('success')
    } else if (statusParam === 'already-verified') {
      setStatus('already-verified')
    } else if (statusParam === 'expired') {
      setStatus('expired')
      if (emailParam) setExpiredEmail(emailParam)
    } else if (statusParam === 'error') {
      setStatus('error')
      const safeMessage = messageParam ? messageParam.slice(0, MAX_MESSAGE_LENGTH) : 'Verification failed'
      setMessage(safeMessage)
    }
  }, [searchParams])

  const handleResend = async () => {
    if (!expiredEmail) return
    setResendLoading(true)
    setResendMessage('')
    try {
      await resendVerification(expiredEmail)
      setResendMessage('A new verification email has been sent. Please check your inbox.')
    } catch {
      setResendMessage('Failed to resend verification email. Please try again.')
    } finally {
      setResendLoading(false)
    }
  }

  const renderContent = () => {
    switch (status) {
      case 'loading':
        return (
          <div className="text-center space-y-4">
            <div className="h-12 w-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-ink-muted">Verifying your email...</p>
          </div>
        )

      case 'success':
        return (
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              <div className="bg-success/10 p-4">
                <CheckCircle className="h-12 w-12 text-success" />
              </div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-normal text-ink">Email verified</h2>
              <p className="text-ink-muted">
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
        )

      case 'already-verified':
        return (
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              <div className="bg-surface-1 p-4">
                <CheckCircle className="h-12 w-12 text-primary" />
              </div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-normal text-ink">Already verified</h2>
              <p className="text-ink-muted">Your email has already been verified. You can sign in to your account.</p>
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
        )

      case 'expired':
        return (
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              <div className="bg-warning/15 p-4">
                <Clock className="h-12 w-12 text-ink" />
              </div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-normal text-ink">Link expired</h2>
              <p className="text-ink-muted">
                This verification link has expired. Verification links are valid for 24 hours.
              </p>
            </div>
            {expiredEmail && (
              <div className="space-y-3">
                <Button className="w-full h-11" onClick={handleResend} disabled={resendLoading}>
                  {resendLoading ? 'Sending...' : 'Resend verification email'}
                </Button>
                {resendMessage && <p className="text-sm text-ink-muted">{resendMessage}</p>}
              </div>
            )}
            <Link to="/signup" className="block">
              <Button variant="outline" className="w-full h-11">
                Register again
              </Button>
            </Link>
          </div>
        )

      case 'error':
        return (
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              <div className="bg-error/10 p-4">
                <XCircle className="h-12 w-12 text-error" />
              </div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-normal text-ink">Verification failed</h2>
              <p className="text-ink-muted">{message}</p>
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
        )
    }
  }

  return (
    <AuthLayout title="Email Verification" description="Confirming your email address">
      {renderContent()}
    </AuthLayout>
  )
}

export default VerifyEmail
