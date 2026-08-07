import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { Card, StatCard, Badge, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'

interface AdminDashboard {
  total_users: number
  active_users: number
  total_tools: number
  active_tools: number
  total_skills: number
  total_prompts: number
  total_audit_logs: number
  integrations_enabled: number
}
interface AuditLog {
  id: number
  timestamp: string
  user_email?: string | null
  action: string
  resource_type: string
  success: boolean
}
interface AuditLogList {
  logs: AuditLog[]
  total: number
}

export default function Admin() {
  const stats = useAsync<AdminDashboard>(() => api.get('/admin/dashboard'))
  const logs = useAsync<AuditLogList>(() => api.get('/admin/audit-logs?page=1&page_size=15'))

  return (
    <>
      <PageHead title="Administração" subtitle="Painel administrativo, auditoria e integrações" />

      {stats.loading && <Spinner />}
      {stats.error && <Card><Empty>{stats.error}</Empty></Card>}
      {stats.data && (
        <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '1.25rem' }}>
          <StatCard label="Usuários" value={stats.data.total_users} hint={`${stats.data.active_users} ativos`} />
          <StatCard label="Prompts" value={stats.data.total_prompts} />
          <StatCard label="Logs de auditoria" value={stats.data.total_audit_logs} />
          <StatCard label="Integrações ativas" value={stats.data.integrations_enabled} />
        </div>
      )}

      <Card title="Logs de auditoria recentes" subtitle="Trilha de operações sensíveis (quem, quando, o quê)">
        {logs.loading && <Spinner />}
        {logs.error && <Empty>{logs.error}</Empty>}
        {logs.data && (
          logs.data.logs.length === 0 ? (
            <Empty>Nenhum log registrado.</Empty>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr><th>Quando</th><th>Usuário</th><th>Ação</th><th>Recurso</th><th>Resultado</th></tr>
                </thead>
                <tbody>
                  {logs.data.logs.map((l) => (
                    <tr key={l.id}>
                      <td className="muted">{new Date(l.timestamp).toLocaleString('pt-BR')}</td>
                      <td>{l.user_email || '—'}</td>
                      <td><Badge tone="accent">{l.action}</Badge></td>
                      <td className="muted">{l.resource_type}</td>
                      <td><Badge tone={l.success ? 'success' : 'danger'}>{l.success ? 'OK' : 'Falha'}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </Card>
    </>
  )
}
