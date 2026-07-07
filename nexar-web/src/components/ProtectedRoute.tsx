import type { ReactNode, FC } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'

interface ProtectedRouteProps {
  children: ReactNode
}

const ProtectedRoute: FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-b-2 border-primary" />
          <p className="mt-4 text-sm text-ink-muted">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/signin" replace />
  }

  return <>{children}</>
}

export default ProtectedRoute
