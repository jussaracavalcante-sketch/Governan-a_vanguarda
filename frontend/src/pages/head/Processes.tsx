import { useMemo, useState } from 'react'
import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { brl } from '@/lib/format'
import { Card, StatCard, Button, Badge, Modal, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { ProcessImprovement, ProcessStage, ProcessStatus, Level3, AiAutomation } from '@/types'

const STAGES: ProcessStage[] = ['Mapeamento', 'Diagnóstico', 'Priorização', 'Redesenho', 'Implementação', 'Medição', 'Padronizado']
const STATUSES: ProcessStatus[] = ['Em andamento', 'Concluído', 'Pausado']
const LEVELS: Level3[] = ['Baixo', 'Médio', 'Alto']
const AI_LEVELS: AiAutomation[] = ['Não', 'Parcial', 'Total']

const statusTone = (s: ProcessStatus) => (s === 'Concluído' ? 'success' : s === 'Pausado' ? 'default' : 'accent')

/** Prioridade derivada da matriz Impacto × Esforço. */
function priority(p: ProcessImprovement): { label: string; tone: 'success' | 'warning' | 'accent' | 'default' } {
  const imp = { Baixo: 1, Médio: 2, Alto: 3 }[p.impact]
  const eff = { Baixo: 1, Médio: 2, Alto: 3 }[p.effort]
  if (imp === 3 && eff === 1) return { label: 'Quick Win', tone: 'success' }
  if (imp >= 2 && eff <= 2) return { label: 'Prioritário', tone: 'warning' }
  if (imp === 3) return { label: 'Estratégico', tone: 'accent' }
  return { label: 'Planejar', tone: 'default' }
}

const emptyForm = {
  name: '', area: '', owner: '', stage: 'Mapeamento' as ProcessStage, status: 'Em andamento' as ProcessStatus,
  impact: 'Médio' as Level3, effort: 'Médio' as Level3, ai_automation: 'Não' as AiAutomation,
  problem: '', proposal: '', time_before: 0, time_after: 0, cost_before: 0, cost_after: 0,
  responsible: '', due_date: '', notes: '',
}

export default function Processes() {
  const { data, loading, error, setData } = useAsync<ProcessImprovement[]>(() => api.get('/head/processes'))
  const [modal, setModal] = useState<null | { mode: 'create' | 'edit' | 'view'; item?: ProcessImprovement }>(null)
  const [form, setForm] = useState(emptyForm)
  const [busy, setBusy] = useState(false)
  const [stageFilter, setStageFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const filtered = useMemo(
    () => (data || []).filter((p) => (!stageFilter || p.stage === stageFilter) && (!statusFilter || p.status === statusFilter)),
    [data, stageFilter, statusFilter],
  )
  const summary = useMemo(() => {
    const list = data || []
    return {
      total: list.length,
      done: list.filter((p) => p.status === 'Concluído').length,
      quickWins: list.filter((p) => priority(p).label === 'Quick Win').length,
      hoursSaved: list.reduce((s, p) => s + Math.max(0, (p.time_before || 0) - (p.time_after || 0)), 0),
      costSaved: list.reduce((s, p) => s + Math.max(0, (p.cost_before || 0) - (p.cost_after || 0)), 0),
    }
  }, [data])

  function openCreate() { setForm(emptyForm); setModal({ mode: 'create' }) }
  function openEdit(p: ProcessImprovement) {
    setForm({
      name: p.name, area: p.area, owner: p.owner, stage: p.stage, status: p.status, impact: p.impact,
      effort: p.effort, ai_automation: p.ai_automation, problem: p.problem, proposal: p.proposal,
      time_before: p.time_before, time_after: p.time_after, cost_before: p.cost_before, cost_after: p.cost_after,
      responsible: p.responsible, due_date: p.due_date, notes: p.notes,
    })
    setModal({ mode: 'edit', item: p })
  }
  async function save(e: React.FormEvent) {
    e.preventDefault(); setBusy(true)
    try {
      if (modal?.mode === 'edit' && modal.item) {
        const u = await api.put<ProcessImprovement>(`/head/processes/${modal.item.id}`, form)
        setData((prev) => (prev || []).map((x) => (x.id === u.id ? u : x)))
      } else {
        const c = await api.post<ProcessImprovement>('/head/processes', form)
        setData((prev) => [c, ...(prev || [])])
      }
      setModal(null)
    } catch (err) { alert(err instanceof Error ? err.message : 'Erro ao salvar') } finally { setBusy(false) }
  }
  async function remove(p: ProcessImprovement) {
    if (!confirm(`Excluir a iniciativa "${p.name}"?`)) return
    try { await api.del(`/head/processes/${p.id}`); setData((prev) => (prev || []).filter((x) => x.id !== p.id)) }
    catch (err) { alert(err instanceof Error ? err.message : 'Erro ao excluir') }
  }

  const timeSaved = (p: ProcessImprovement) => Math.max(0, (p.time_before || 0) - (p.time_after || 0))
  const savedPct = (p: ProcessImprovement) => (p.time_before ? Math.round((timeSaved(p) / p.time_before) * 100) : 0)

  return (
    <>
      <PageHead
        title="Otimização de Processos"
        subtitle="Fluxo PDCA/Kaizen: mapear, diagnosticar, priorizar, redesenhar, implementar, medir e padronizar"
        actions={<Button variant="primary" onClick={openCreate}>+ Nova iniciativa</Button>}
      />

      {data && !loading && (
        <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '1.25rem' }}>
          <StatCard label="Iniciativas" value={summary.total} hint={`${summary.done} concluídas`} />
          <StatCard label="Quick Wins" value={summary.quickWins} hint="alto impacto · baixo esforço" />
          <StatCard label="Horas economizadas" value={`${Math.round(summary.hoursSaved)}h`} hint="por ciclo (antes → depois)" />
          <StatCard label="Economia mensal" value={brl(summary.costSaved)} hint="custo evitado/mês" />
        </div>
      )}

      <Card style={{ marginBottom: '1.25rem' }}>
        <div className="row" style={{ gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <select value={stageFilter} onChange={(e) => setStageFilter(e.target.value)} style={{ maxWidth: 200 }}>
            <option value="">Todas as etapas</option>
            {STAGES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ maxWidth: 180 }}>
            <option value="">Todos os status</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <span className="muted" style={{ marginLeft: 'auto', fontSize: '0.85rem' }}>{filtered.length} iniciativas</span>
        </div>
      </Card>

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && !loading && (
        <Card>
          {filtered.length === 0 ? (
            <Empty>Nenhuma iniciativa de otimização encontrada.</Empty>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Processo</th><th>Área</th><th>Etapa</th><th>Prioridade</th>
                    <th>IA</th><th>Ganho</th><th>Status</th><th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((p) => {
                    const prio = priority(p)
                    const stageIdx = STAGES.indexOf(p.stage) + 1
                    return (
                      <tr key={p.id}>
                        <td style={{ fontWeight: 600, cursor: 'pointer' }} onClick={() => setModal({ mode: 'view', item: p })}>
                          {p.name}
                          {p.owner && <div className="muted" style={{ fontSize: '0.75rem' }}>{p.owner}</div>}
                        </td>
                        <td>{p.area || '—'}</td>
                        <td><Badge tone="accent">{p.stage}</Badge><div className="muted" style={{ fontSize: '0.7rem' }}>etapa {stageIdx}/7</div></td>
                        <td><Badge tone={prio.tone}>{prio.label}</Badge></td>
                        <td>{p.ai_automation}</td>
                        <td>{timeSaved(p) > 0 ? <span>−{timeSaved(p)}h <span className="muted">({savedPct(p)}%)</span></span> : '—'}</td>
                        <td><Badge tone={statusTone(p.status)}>{p.status}</Badge></td>
                        <td>
                          <div className="row" style={{ gap: '0.4rem', justifyContent: 'flex-end' }}>
                            <Button size="sm" variant="ghost" onClick={() => openEdit(p)}>Editar</Button>
                            <Button size="sm" variant="danger" onClick={() => remove(p)}>Excluir</Button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {modal?.mode === 'view' && modal.item && (
        <Modal title={modal.item.name} onClose={() => setModal(null)}>
          <div className="row" style={{ gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
            <Badge tone="accent">{modal.item.stage}</Badge>
            <Badge tone={statusTone(modal.item.status)}>{modal.item.status}</Badge>
            <Badge tone={priority(modal.item).tone}>{priority(modal.item).label}</Badge>
            <Badge>IA: {modal.item.ai_automation}</Badge>
          </div>
          <div className="stack" style={{ gap: '0.75rem' }}>
            <div><strong>Área:</strong> {modal.item.area || '—'} · <strong>Dono:</strong> {modal.item.owner || '—'} · <strong>Responsável:</strong> {modal.item.responsible || '—'}</div>
            <div><strong>Situação atual (as-is):</strong><p className="muted" style={{ marginTop: 4 }}>{modal.item.problem || '—'}</p></div>
            <div><strong>Proposta otimizada (to-be):</strong><p className="muted" style={{ marginTop: 4 }}>{modal.item.proposal || '—'}</p></div>
            <div className="grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
              <StatCard label="Tempo (antes → depois)" value={`${modal.item.time_before}h → ${modal.item.time_after}h`} hint={`economia de ${timeSaved(modal.item)}h/ciclo`} />
              <StatCard label="Custo (antes → depois)" value={`${brl(modal.item.cost_before)} → ${brl(modal.item.cost_after)}`} hint={`economia de ${brl(Math.max(0, modal.item.cost_before - modal.item.cost_after))}/mês`} />
            </div>
            {modal.item.notes && <div><strong>Notas:</strong> <span className="muted">{modal.item.notes}</span></div>}
            {modal.item.due_date && <div className="muted" style={{ fontSize: '0.8rem' }}>Prazo: {modal.item.due_date}</div>}
          </div>
        </Modal>
      )}

      {(modal?.mode === 'create' || modal?.mode === 'edit') && (
        <Modal title={modal.mode === 'edit' ? 'Editar iniciativa' : 'Nova iniciativa de otimização'} onClose={() => setModal(null)}>
          <form onSubmit={save}>
            <div className="field"><label>Nome do processo</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="field"><label>Área</label>
                <input value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value })} /></div>
              <div className="field"><label>Dono do processo</label>
                <input value={form.owner} onChange={(e) => setForm({ ...form, owner: e.target.value })} /></div>
              <div className="field"><label>Etapa (PDCA)</label>
                <select value={form.stage} onChange={(e) => setForm({ ...form, stage: e.target.value as ProcessStage })}>
                  {STAGES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Status</label>
                <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as ProcessStatus })}>
                  {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Impacto</label>
                <select value={form.impact} onChange={(e) => setForm({ ...form, impact: e.target.value as Level3 })}>
                  {LEVELS.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Esforço</label>
                <select value={form.effort} onChange={(e) => setForm({ ...form, effort: e.target.value as Level3 })}>
                  {LEVELS.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Automação com IA</label>
                <select value={form.ai_automation} onChange={(e) => setForm({ ...form, ai_automation: e.target.value as AiAutomation })}>
                  {AI_LEVELS.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Responsável</label>
                <input value={form.responsible} onChange={(e) => setForm({ ...form, responsible: e.target.value })} /></div>
            </div>
            <div className="field"><label>Situação atual / gargalo (as-is)</label>
              <textarea rows={2} value={form.problem} onChange={(e) => setForm({ ...form, problem: e.target.value })} /></div>
            <div className="field"><label>Proposta otimizada (to-be)</label>
              <textarea rows={2} value={form.proposal} onChange={(e) => setForm({ ...form, proposal: e.target.value })} /></div>
            <div className="grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem' }}>
              <div className="field"><label>Tempo antes (h/ciclo)</label>
                <input type="number" min={0} step="0.5" value={form.time_before} onChange={(e) => setForm({ ...form, time_before: Number(e.target.value) })} /></div>
              <div className="field"><label>Tempo depois (h/ciclo)</label>
                <input type="number" min={0} step="0.5" value={form.time_after} onChange={(e) => setForm({ ...form, time_after: Number(e.target.value) })} /></div>
              <div className="field"><label>Custo antes (R$/mês)</label>
                <input type="number" min={0} step="0.01" value={form.cost_before} onChange={(e) => setForm({ ...form, cost_before: Number(e.target.value) })} /></div>
              <div className="field"><label>Custo depois (R$/mês)</label>
                <input type="number" min={0} step="0.01" value={form.cost_after} onChange={(e) => setForm({ ...form, cost_after: Number(e.target.value) })} /></div>
              <div className="field"><label>Prazo</label>
                <input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} /></div>
            </div>
            <div className="field"><label>Notas</label>
              <textarea rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
            <div className="row" style={{ justifyContent: 'flex-end', gap: '0.5rem' }}>
              <Button type="button" variant="ghost" onClick={() => setModal(null)}>Cancelar</Button>
              <Button type="submit" variant="primary" disabled={busy}>{busy ? 'Salvando…' : 'Salvar'}</Button>
            </div>
          </form>
        </Modal>
      )}
    </>
  )
}
