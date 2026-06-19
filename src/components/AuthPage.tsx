import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { loginUser, registerUser } from '../api/api'

type AuthPageProps = {
  onLogin: (user: { user_id: string; username: string }) => void
}

export function AuthPage({ onLogin }: AuthPageProps) {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const user = mode === 'login'
        ? await loginUser(username, password)
        : await registerUser(username, password)

      onLogin({ user_id: user.user_id, username: user.username })
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to authenticate')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-panel">
        <div className="auth-tabs">
          <button type="button" className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>Sign in</button>
          <button type="button" className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')}>Create account</button>
        </div>
        <h1>{mode === 'login' ? 'Welcome back' : 'Create your travel profile'}</h1>
        <form onSubmit={handleSubmit}>
          <label htmlFor="username">Username</label>
          <input id="username" value={username} onChange={(event) => setUsername(event.target.value)} required />

          <label htmlFor="password">Password</label>
          <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />

          <button className="primary-button" type="submit" disabled={isLoading}>
            {isLoading ? 'Processing…' : mode === 'login' ? 'Sign in' : 'Register'}
          </button>
        </form>
        {error && <div className="api-error">{error}</div>}
      </div>
    </section>
  )
}