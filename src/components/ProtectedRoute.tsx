import { Navigate } from 'react-router-dom'

type ProtectedRouteProps = {
  user: { user_id: string; username: string } | null
  children: React.ReactNode
}

export function ProtectedRoute({ user, children }: ProtectedRouteProps) {
  if (!user) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}