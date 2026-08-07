import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', textAlign: 'center', padding: '1rem' }}>
      <div>
        <h1 style={{ fontSize: '3rem' }}>404</h1>
        <p className="muted" style={{ marginBottom: '1rem' }}>Página não encontrada.</p>
        <Link to="/">← Voltar ao início</Link>
      </div>
    </div>
  )
}
