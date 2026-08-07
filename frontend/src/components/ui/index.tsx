import type { ButtonHTMLAttributes, ReactNode } from 'react'
import './ui.css'

export function Card({
  title,
  subtitle,
  actions,
  children,
  style,
}: {
  title?: string
  subtitle?: string
  actions?: ReactNode
  children?: ReactNode
  style?: React.CSSProperties
}) {
  return (
    <div className="card" style={style}>
      {(title || actions) && (
        <div className="row" style={{ justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            {title && <div className="card-title">{title}</div>}
            {subtitle && <div className="card-sub">{subtitle}</div>}
          </div>
          {actions}
        </div>
      )}
      {children}
    </div>
  )
}

type BtnVariant = 'primary' | 'ghost' | 'danger' | 'default'
export function Button({
  variant = 'default',
  size,
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: BtnVariant; size?: 'sm' }) {
  const cls = ['btn']
  if (variant === 'primary') cls.push('btn-primary')
  if (variant === 'ghost') cls.push('btn-ghost')
  if (variant === 'danger') cls.push('btn-danger')
  if (size === 'sm') cls.push('btn-sm')
  return (
    <button className={cls.join(' ')} {...rest}>
      {children}
    </button>
  )
}

type Tone = 'success' | 'danger' | 'warning' | 'accent' | 'default'
export function Badge({ tone = 'default', children }: { tone?: Tone; children: ReactNode }) {
  const cls = ['badge']
  if (tone !== 'default') cls.push(`badge-${tone}`)
  return <span className={cls.join(' ')}>{children}</span>
}

export function StatCard({
  label,
  value,
  hint,
}: {
  label: string
  value: ReactNode
  hint?: string
}) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {hint && <div className="stat-hint">{hint}</div>}
    </div>
  )
}

export function Modal({
  title,
  onClose,
  children,
}: {
  title: string
  onClose: () => void
  children: ReactNode
}) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 style={{ fontSize: '1.1rem' }}>{title}</h3>
          <button className="modal-close" onClick={onClose} aria-label="Fechar">
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}

export function Spinner() {
  return <div className="spinner" role="status" aria-label="Carregando" />
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="empty">{children}</div>
}
