import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui'
import { ApiError } from '@/lib/api'

export default function Login() {
  const { user, login } = useAuth()
  const [email, setEmail] = useState('admin@vanguardian.local')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/" replace />

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await login(email, password, remember)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Falha no login')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: '1rem' }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div
            style={{
              width: 52,
              height: 52,
              borderRadius: 14,
              margin: '0 auto 0.75rem',
              display: 'grid',
              placeItems: 'center',
              fontWeight: 800,
              fontSize: '1.5rem',
              color: '#06263a',
              background: 'linear-gradient(135deg, var(--accent), var(--accent-2))',
            }}
          >
            V
          </div>
          <h1 style={{ fontSize: '1.4rem' }}>VANGUARDIAN</h1>
          <p className="muted" style={{ fontSize: '0.85rem' }}>
            Governança de IA · Prompts · Propriedade Intelectual
          </p>
        </div>

        <form className="card" onSubmit={submit}>
          <div className="field">
            <label htmlFor="email">E-mail</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="username"
            />
          </div>
          <div className="field">
            <label htmlFor="password">Senha</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          <label className="row" style={{ gap: '0.5rem', fontSize: '0.85rem', marginBottom: '0.9rem' }}>
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
              style={{ width: 'auto' }}
            />
            Manter conectado
          </label>

          {error && (
            <div
              style={{
                background: 'rgba(248,113,113,0.15)',
                color: 'var(--danger)',
                padding: '0.6rem 0.75rem',
                borderRadius: 8,
                fontSize: '0.85rem',
                marginBottom: '0.9rem',
              }}
            >
              {error}
            </div>
          )}

          <Button variant="primary" type="submit" disabled={busy} style={{ width: '100%', justifyContent: 'center' }}>
            {busy ? 'Entrando…' : 'Entrar'}
          </Button>

          <p className="muted" style={{ fontSize: '0.72rem', textAlign: 'center', marginTop: '1rem' }}>
            Demo: admin@vanguardian.local · admin123
          </p>
        </form>
      </div>
    </div>
  )
}
