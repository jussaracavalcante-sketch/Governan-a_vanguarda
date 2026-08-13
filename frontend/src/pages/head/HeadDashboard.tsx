import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { brl } from '@/lib/format'
import { Card, StatCard, Spinner, Empty, Badge } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { HeadDashboard as Stats, TaskStatus } from '@/types'

const taskTone = (s: TaskStatus) =>
  s === 'Concluída' ? 'success' : s === 'Bloqueada' ? 'danger' : s === 'Em andamento' ? 'accent' : 'warning'

const critTone = (c: string) =>
  c === 'Alta' ? 'danger' : c === 'Média' ? 'warning' : 'accent'

const stageTone = (s: string) =>
  s === 'active' ? 'success' : s === 'at-risk' ? 'danger' : 'accent'

const stageLabel = (s: string) =>
  s === 'active' ? 'Ativa' : s === 'at-risk' ? 'Em risco' : s === 'onboarding' ? 'Onboarding' : s

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Prmo = any

function PrmoView() {
  const { data: p, loading, error } = useAsync<Prmo>(() => api.get('/head/prmo'))

  if (loading) return <Spinner />
  if (error || !p) return null

  return (
    <div className="stack">
      <Card
        title="🛡️ Visão do PrMO · consultivo"
        subtitle={`${p.source} · snapshot de ${p.as_of} (somente leitura)`}
      >
        <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
          {p.registry.by_type.map((r: { label: string; count: number }) => (
            <StatCard key={r.label} label={r.label} value={r.count} />
          ))}
        </div>
      </Card>

      <div className="grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
        <Card title="Adoção por área" subtitle="% de uso de IA nas frentes da operação">
          <div className="stack" style={{ gap: '0.75rem' }}>
            {p.adoption.map((a: { area: string; percent: number }) => (
              <div key={a.area}>
                <div className="row" style={{ justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                  <span style={{ fontSize: '0.85rem' }}>{a.area}</span>
                  <strong style={{ fontSize: '0.85rem' }}>{a.percent}%</strong>
                </div>
                <div style={{ height: 8, borderRadius: 6, background: 'var(--surface-2)', overflow: 'hidden' }}>
                  <div style={{ width: `${a.percent}%`, height: '100%', background: 'linear-gradient(90deg, var(--accent), var(--accent-2))' }} />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Incidentes de governança" subtitle="Conformidade e ações necessárias">
          <div className="stack" style={{ gap: '0.6rem' }}>
            {p.incidents.map((i: { title: string; area: string; criticality: string; status: string }) => (
              <div key={i.title} className="row" style={{ justifyContent: 'space-between', gap: '0.75rem' }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{i.title}</div>
                  <div className="muted" style={{ fontSize: '0.75rem' }}>{i.area} · {i.status}</div>
                </div>
                <Badge tone={critTone(i.criticality)}>{i.criticality}</Badge>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
        <Card title="Iniciativas de IA" subtitle={`${p.hours_saved_total}h economizadas no total`}>
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Iniciativa</th><th>Status</th><th>Horas</th></tr></thead>
              <tbody>
                {p.initiatives.map((it: { name: string; status: string; hours_saved: number }) => (
                  <tr key={it.name}>
                    <td style={{ fontWeight: 600 }}>{it.name}</td>
                    <td className="muted">{it.status}</td>
                    <td>{it.hours_saved > 0 ? `${it.hours_saved}h` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card title="Carteira de contas" subtitle="Uso de IA por cliente">
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Cliente</th><th>Segmento</th><th>Situação</th></tr></thead>
              <tbody>
                {p.clients.map((c: { name: string; segment: string; stage: string; ai_usage: string }) => (
                  <tr key={c.name}>
                    <td style={{ fontWeight: 600 }}>{c.name}<div className="muted" style={{ fontSize: '0.72rem' }}>{c.ai_usage}</div></td>
                    <td className="muted">{c.segment}</td>
                    <td><Badge tone={stageTone(c.stage)}>{stageLabel(c.stage)}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  )
}

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

          <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <StatCard label="Otimização de processos" value={data.total_processes} hint={`${data.processes_done} concluídos · ${data.processes_in_progress} em andamento`} />
            <StatCard label="Horas economizadas" value={`${data.hours_saved}h`} hint="por ciclo (antes → depois)" />
            <StatCard label="Economia mensal" value={brl(data.cost_saved)} hint="custo evitado com otimização" />
            <StatCard label="Base de conhecimento" value={data.total_articles} hint={`${data.published_articles} publicados`} />
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

          <PrmoView />
        </div>
      )}
    </>
  )
}
