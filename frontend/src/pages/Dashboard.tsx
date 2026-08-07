import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { Card, StatCard, Spinner, Empty, Badge } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { DashboardStats } from '@/types'

export default function Dashboard() {
  const { data, loading, error } = useAsync<DashboardStats>(() => api.get('/dashboard/stats'))

  return (
    <>
      <PageHead
        title="Dashboard Executivo"
        subtitle="Visão consolidada de adoção, ativos de IA e conformidade"
      />

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && (
        <div className="stack">
          <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <StatCard label="Prompts" value={data.total_prompts} hint={`${data.favorite_prompts} favoritos`} />
            <StatCard label="Ferramentas ativas" value={data.active_tools} hint={`${data.total_tools} no total`} />
            <StatCard label="Usuários ativos" value={data.active_users} hint={`${data.total_users} no total`} />
            <StatCard label="Skills mapeadas" value={data.total_skills} hint={`${data.total_teams} times`} />
          </div>

          <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
            <StatCard label="Nível médio de skill" value={data.avg_skill_level.toFixed(1)} hint="escala 1–4" />
            <StatCard label="Skills críticas" value={data.critical_skills} hint="requerem atenção" />
            <StatCard label="Prompts favoritos" value={data.favorite_prompts} hint="mais reutilizados" />
          </div>

          <Card title="Atividades recentes" subtitle="Últimas ações registradas na plataforma">
            {data.recent_activities.length === 0 ? (
              <Empty>Nenhuma atividade registrada.</Empty>
            ) : (
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Ação</th>
                      <th>Usuário</th>
                      <th>Data</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.recent_activities.map((a) => (
                      <tr key={a.id}>
                        <td>{a.action}</td>
                        <td><Badge tone="accent">{a.user}</Badge></td>
                        <td className="muted">{a.date}</td>
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
