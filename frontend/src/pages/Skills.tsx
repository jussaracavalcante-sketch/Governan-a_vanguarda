import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { Card, Badge, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { Skill, SkillLevel } from '@/types'

const toneFor = (l: SkillLevel) =>
  l === 'Especialista' ? 'success' : l === 'Avançado' ? 'accent' : l === 'Intermediário' ? 'warning' : 'danger'

export default function Skills() {
  const { data, loading, error } = useAsync<Skill[]>(() => api.get('/skills'))

  return (
    <>
      <PageHead
        title="Pessoas & Skills"
        subtitle="Matriz de maturidade em IA por time e competência"
      />
      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}
      {data && !loading && (
        <Card>
          {data.length === 0 ? (
            <Empty>Nenhuma skill mapeada.</Empty>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr><th>Time</th><th>Skill</th><th>Categoria</th><th>Nível</th><th>Revisor</th></tr>
                </thead>
                <tbody>
                  {data.map((s) => (
                    <tr key={s.id}>
                      <td style={{ fontWeight: 600 }}>{s.team}</td>
                      <td>{s.skill}</td>
                      <td className="muted">{s.category}</td>
                      <td><Badge tone={toneFor(s.level)}>{s.level}</Badge></td>
                      <td className="muted">{s.reviewer || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}
    </>
  )
}
