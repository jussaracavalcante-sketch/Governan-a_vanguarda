import { useMemo, useState } from 'react'
import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { useAuth } from '@/context/AuthContext'
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

type SyncState = {
  id: number
  source: string
  status: string
  last_count: number
  message: string
  last_run: string | null
}

const syncTone = (s: string) =>
  s === 'ok' ? 'success' : s === 'erro' ? 'danger' : 'warning'

function fmtWhen(iso: string | null) {
  if (!iso) return 'nunca'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const sourceTone = (s: string) =>
  s === 'Jira' ? 'accent' : s === 'GitHub' ? 'warning' : s === 'Gmail' ? 'danger' : 'success'

const statusTone = (s: string) => {
  const v = (s || '').toLowerCase()
  if (v.includes('conclu') || v.includes('done') || v.includes('fech')) return 'success'
  if (v.includes('pend') || v.includes('block') || v.includes('bloque')) return 'warning'
  if (v.includes('andamento') || v.includes('progress')) return 'accent'
  return 'default'
}

export default function Activities() {
  const { user } = useAuth()
  const canSync = user?.role === 'Admin' || user?.role === 'Manager'
  const { data, loading, error, reload } = useAsync<Activity[]>(() => api.get('/head/activities'))
  const sync = useAsync<SyncState[]>(() => api.get('/head/sync-status'))
  const [filter, setFilter] = useState('')
  const [syncing, setSyncing] = useState(false)
  const [syncMsg, setSyncMsg] = useState('')

  async function runSync() {
    setSyncing(true); setSyncMsg('')
    try {
      const res = await api.post<{ created: number }>('/head/sync', {})
      setSyncMsg(`Sincronizado — ${res.created} nova(s) atividade(s).`)
      reload(); sync.reload()
    } catch (err) {
      setSyncMsg(err instanceof Error ? err.message : 'Falha ao sincronizar')
    } finally { setSyncing(false) }
  }

  const counts = useMemo(() => {
    const c: Record<string, number> = { Jira: 0, Drive: 0, Gmail: 0, GitHub: 0 }
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
        subtitle="Sincronização automática das suas ferramentas — Jira, Google Drive e Gmail"
        actions={
          <div className="row" style={{ gap: '0.4rem', flexWrap: 'wrap' }}>
            {['', 'Jira', 'Drive', 'Gmail', 'GitHub'].map((s) => (
              <Button key={s || 'all'} size="sm" variant={filter === s ? 'primary' : 'ghost'} onClick={() => setFilter(s)}>
                {s || 'Todas'}
              </Button>
            ))}
            {canSync && (
              <Button size="sm" variant="primary" onClick={runSync} disabled={syncing}>
                {syncing ? 'Sincronizando…' : '↻ Sincronizar agora'}
              </Button>
            )}
          </div>
        }
      />

      {(sync.data || syncMsg) && (
        <Card style={{ marginBottom: '1rem' }}>
          <div className="row" style={{ gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <strong style={{ fontSize: '0.85rem' }}>Sincronização automática · 3× ao dia (08h, 14h, 20h)</strong>
            <div className="row" style={{ gap: '0.5rem', flexWrap: 'wrap', marginLeft: 'auto' }}>
              {['Jira', 'Drive', 'Gmail'].map((src) => {
                const st = (sync.data || []).find((x) => x.source === src)
                return (
                  <Badge key={src} tone={st ? syncTone(st.status) : 'default'}>
                    {src}: {st ? `${st.status}` : 'aguardando'}
                    {st?.last_run ? ` · ${fmtWhen(st.last_run)}` : ''}
                  </Badge>
                )
              })}
            </div>
          </div>
          {syncMsg && <div className="muted" style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>{syncMsg}</div>}
          {(sync.data || []).some((x) => x.status === 'não configurado') && (
            <div className="muted" style={{ fontSize: '0.78rem', marginTop: '0.4rem' }}>
              Algumas fontes ainda não têm credenciais configuradas no servidor — assim que forem
              adicionadas, a atualização passa a ser automática.
            </div>
          )}
        </Card>
      )}

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && (
        <div className="stack">
          <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <StatCard label="Total de atividades" value={data.length} hint="ferramentas integradas" />
            <StatCard label="Jira" value={counts.Jira || 0} hint="tarefas e bugs" />
            <StatCard label="Google Drive" value={counts.Drive || 0} hint="documentos" />
            <StatCard label="Gmail" value={counts.Gmail || 0} hint="e-mails relevantes" />
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
