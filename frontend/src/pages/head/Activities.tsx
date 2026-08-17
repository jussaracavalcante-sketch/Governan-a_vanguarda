import { useMemo, useState } from 'react'
import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { Card, StatCard, Badge, Spinner, Empty, Button } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'

type Activity = {
  id: number
  source: string
  title: string
  reference: string
  category: string
  status: string
  priority: string
  url: string
  activity_date: string
}

const sourceTone = (s: string) =>
  s === 'Jira' ? 'accent' : s === 'GitHub' ? 'warning' : 'success'

const statusTone = (s: string) => {
  const v = (s || '').toLowerCase()
  if (v.includes('conclu') || v.includes('done') || v.includes('fech')) return 'success'
  if (v.includes('pend') || v.includes('block') || v.includes('bloque')) return 'warning'
  if (v.includes('andamento') || v.includes('progress')) return 'accent'
  return 'default'
}

export default function Activities() {
  const { data, loading, error } = useAsync<Activity[]>(() => api.get('/head/activities'))
  const [filter, setFilter] = useState('')

  const counts = useMemo(() => {
    const c: Record<string, number> = { Jira: 0, Drive: 0, GitHub: 0 }
    ;(data || []).forEach((a) => { c[a.source] = (c[a.source] || 0) + 1 })
    return c
  }, [data])

  const rows = useMemo(
    () => (data || []).filter((a) => !filter || a.source === filter),
    [data, filter],
  )

  return (
    <>
      <PageHead
        title="Minhas Atividades"
        subtitle="Agregado das suas ferramentas — Jira, Google Drive e GitHub"
        actions={
          <div className="row" style={{ gap: '0.4rem', flexWrap: 'wrap' }}>
            {['', 'Jira', 'Drive', 'GitHub'].map((s) => (
              <Button key={s || 'all'} size="sm" variant={filter === s ? 'primary' : 'ghost'} onClick={() => setFilter(s)}>
                {s || 'Todas'}
              </Button>
            ))}
          </div>
        }
      />

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && (
        <div className="stack">
          <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <StatCard label="Total de atividades" value={data.length} hint="das 3 ferramentas" />
            <StatCard label="Jira" value={counts.Jira || 0} hint="tarefas e bugs" />
            <StatCard label="Google Drive" value={counts.Drive || 0} hint="documentos" />
            <StatCard label="GitHub" value={counts.GitHub || 0} hint="PRs e commits" />
          </div>

          <Card title="Atividades" subtitle={`${rows.length} item(ns)${filter ? ` · ${filter}` : ''}`}>
            {rows.length === 0 ? (
              <Empty>Nenhuma atividade para este filtro.</Empty>
            ) : (
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr><th>Fonte</th><th>Atividade</th><th>Ref.</th><th>Status</th><th>Prioridade</th><th>Data</th></tr>
                  </thead>
                  <tbody>
                    {rows.map((a) => (
                      <tr key={a.id}>
                        <td><Badge tone={sourceTone(a.source)}>{a.source}</Badge></td>
                        <td style={{ fontWeight: 600, maxWidth: 420 }}>
                          {a.url ? (
                            <a href={a.url} target="_blank" rel="noreferrer">{a.title}</a>
                          ) : a.title}
                          {a.category ? <div className="muted" style={{ fontSize: '0.72rem', fontWeight: 400 }}>{a.category}</div> : null}
                        </td>
                        <td className="muted">{a.reference || '—'}</td>
                        <td>{a.status ? <Badge tone={statusTone(a.status)}>{a.status}</Badge> : '—'}</td>
                        <td className="muted">{a.priority || '—'}</td>
                        <td className="muted">{a.activity_date || '—'}</td>
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
