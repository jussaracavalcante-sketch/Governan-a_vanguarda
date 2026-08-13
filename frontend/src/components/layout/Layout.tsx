import { useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { useTheme } from '@/context/ThemeContext'
import './layout.css'

type NavItem = { to: string; label: string; icon: string; end?: boolean; roles?: string[] }

const NAV_GROUPS: { title: string; items: NavItem[] }[] = [
  {
    title: 'Gestão HEAD de IA',
    items: [
      { to: '/', label: 'Visão Geral', icon: '🧠', end: true },
      { to: '/ativos', label: 'Controle de Ativos', icon: '🗂️' },
      { to: '/tarefas', label: 'Tarefas do Dia a Dia', icon: '✅' },
      { to: '/indicadores', label: 'Indicadores & KPIs', icon: '📈' },
      { to: '/relatorios', label: 'Relatórios Mensais', icon: '🗓️' },
      { to: '/licencas', label: 'Controle de Licenças', icon: '🔑' },
      { to: '/processos', label: 'Otimização de Processos', icon: '⚙️' },
      { to: '/conhecimento', label: 'Base de Conhecimento', icon: '📖' },
    ],
  },
]

const TITLES: Record<string, string> = {
  '/': 'Visão Geral',
  '/ativos': 'Controle de Ativos',
  '/tarefas': 'Tarefas do Dia a Dia',
  '/indicadores': 'Indicadores & KPIs',
  '/relatorios': 'Relatórios Mensais',
  '/licencas': 'Controle de Licenças',
  '/processos': 'Otimização de Processos',
  '/conhecimento': 'Base de Conhecimento',
}

export default function Layout() {
  const { user, logout } = useAuth()
  const { theme, toggle } = useTheme()
  const [open, setOpen] = useState(false)
  const loc = useLocation()
  const title = TITLES[loc.pathname] || 'HEAD de IA'
  const initials = (user?.name || '?')
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  const groups = NAV_GROUPS.map((g) => ({
    ...g,
    items: g.items.filter((n) => !n.roles || (user && n.roles.includes(user.role))),
  })).filter((g) => g.items.length > 0)

  return (
    <div className="app-shell">
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="brand">
          <div className="brand-mark">H</div>
          <div>
            <div className="brand-name">HEAD de IA</div>
            <div className="brand-sub">Painel de Gestão</div>
          </div>
        </div>
        {groups.map((g) => (
          <div key={g.title}>
            <div className="nav-sep">{g.title}</div>
            {g.items.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.end}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setOpen(false)}
              >
                <span className="nav-icon">{n.icon}</span>
                {n.label}
              </NavLink>
            ))}
          </div>
        ))}
      </aside>
      <div
        className={`sidebar-backdrop ${open ? 'show' : ''}`}
        onClick={() => setOpen(false)}
        aria-hidden="true"
      />

      <div className="main">
        <header className="topbar">
          <div className="row" style={{ gap: '0.75rem' }}>
            <button className="icon-btn menu-toggle" onClick={() => setOpen((o) => !o)} aria-label="Menu">
              ☰
            </button>
            <h1>{title}</h1>
          </div>
          <div className="topbar-actions">
            <button className="icon-btn" onClick={toggle} aria-label="Alternar tema" title="Alternar tema">
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            <div className="row" style={{ gap: '0.5rem' }}>
              <div className="avatar" title={user?.email}>{initials}</div>
              <div className="user-meta" style={{ lineHeight: 1.1 }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{user?.name}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--muted)' }}>{user?.role}</div>
              </div>
            </div>
            <button className="icon-btn" onClick={logout} aria-label="Sair" title="Sair">
              ⏻
            </button>
          </div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
