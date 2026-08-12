import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { brl } from '@/lib/format'
import { Card, StatCard, Spinner, Empty, Badge } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { HeadDashboard as Stats, TaskStatus } from '@/types'

const taskTone = (s: TaskStatus) =>
  s === 'Concluída' ? 'success' : s === 'Bloqueada' ? 'danger' : s === 'Em andamento' ? 'accent' : 'warning'

export default function HeadDashboard() {
  const { data, loading, error } = useAsync<Stats>(() => api.get('/head/dashboard'))

  return (
    <>
      <PageHead
        title="Gestão HEAD de IA"
        subtitle="Visão executiva de ativos, operação, licenças, KPIs e conhecimento"
      />

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && (
        <div className="stack">
          <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <StatCard label="Ativos de IA" value={data.total_assets} hint={`${data.active_assets} ativos · ${data.critical_assets} críticos`} />
            <StatCard label="Custo mensal (ativos)" value={brl(data.assets_monthly_cost)} hint="modelos, agentes e automações" />
            <StatCard label="Licenças" value={data.total_licenses} hint={`${brl(data.licenses_monthly_cost)}/mês`} />
            <StatCard label="Uso de assentos" value={`${data.seats_utilization}%`} hint={`${data.seats_used}/${data.seats_total} em uso`} />
          </div>

          <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <StatCard label="Tarefas (total)" value={data.total_tasks} hint={`${data.tasks_pending} pendentes`} />
            <StatCard label="Concluídas" value={data.tasks_done} hint={`${data.tasks_in_progress} em andamento`} />
            <StatCard label="Horas no mês" value={data.hours_this_month} hint="esforço registrado" />
            <StatCard label="KPIs na meta" value={`${data.kpis_on_target}/${data.total_indicators}`} hint={`${data.kpis_off_target} fora da meta`} />
          </div>

          <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
            <StatCard label="Base de conhecimento" value={data.total_articles} hint={`${data.published_articles} publicados`} />
            <StatCard label="Licenças em renovação" value={data.licenses_renewing} hint="requerem atenção" />
            <StatCard label="Ativos críticos" value={data.critical_assets} hint="prioridade máxima" />
          </div>

          <Card title="Tarefas recentes" subtitle="Últimas atividades registradas pela equipe de IA">
            {data.recent_tasks.length === 0 ? (
              <Empty>Nenhuma tarefa registrada.</Empty>
            ) : (
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr><th>Tarefa</th><th>Responsável</th><th>Status</th><th>Data</th></tr>
                  </thead>
                  <tbody>
                    {data.recent_tasks.map((t) => (
                      <tr key={t.id}>
                        <td style={{ fontWeight: 600 }}>{t.title}</td>
                        <td>{t.responsible || '—'}</td>
                        <td><Badge tone={taskTone(t.status)}>{t.status}</Badge></td>
                        <td className="muted">{t.task_date || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>
      )}
    </>
  )
}
