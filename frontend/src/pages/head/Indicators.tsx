import { useMemo, useState } from 'react'
import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { useAuth } from '@/context/AuthContext'
import { currentPeriod } from '@/lib/format'
import { Card, Button, Badge, Modal, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { Indicator, IndicatorCategory, Trend } from '@/types'

const CATEGORIES: IndicatorCategory[] = ['Operacional', 'Financeiro', 'Adoção', 'Qualidade', 'Risco']
const TRENDS: Trend[] = ['Subindo', 'Estável', 'Caindo']
const trendIcon = (t: Trend) => (t === 'Subindo' ? '▲' : t === 'Caindo' ? '▼' : '▬')

/** Para categoria de Risco, "menor é melhor"; nas demais, "maior é melhor". */
const onTarget = (i: Indicator) => {
  if (!i.target) return i.actual > 0 ? i.category !== 'Risco' : i.category === 'Risco'
  return i.category === 'Risco' ? i.actual <= i.target : i.actual >= i.target
}

const emptyForm = {
  name: '', category: 'Operacional' as IndicatorCategory, period: currentPeriod(),
  unit: '', target: 0, actual: 0, trend: 'Estável' as Trend, notes: '',
}

export default function Indicators() {
  const { user } = useAuth()
  const canEdit = user?.role === 'Admin' || user?.role === 'Manager'
  const { data, loading, error, setData } = useAsync<Indicator[]>(() => api.get('/head/indicators'))
  const [modal, setModal] = useState<null | { mode: 'create' | 'edit'; item?: Indicator }>(null)
  const [form, setForm] = useState(emptyForm)
  const [busy, setBusy] = useState(false)
  const [catFilter, setCatFilter] = useState('')
  const [periodFilter, setPeriodFilter] = useState('')

  const periods = useMemo(() => Array.from(new Set((data || []).map((i) => i.period).filter(Boolean))).sort().reverse(), [data])
  const filtered = useMemo(
    () => (data || []).filter((i) => (!catFilter || i.category === catFilter) && (!periodFilter || i.period === periodFilter)),
    [data, catFilter, periodFilter],
  )
  const onTargetCount = useMemo(() => filtered.filter(onTarget).length, [filtered])

  function openCreate() { setForm({ ...emptyForm, period: currentPeriod() }); setModal({ mode: 'create' }) }
  function openEdit(i: Indicator) {
    setForm({ name: i.name, category: i.category, period: i.period, unit: i.unit, target: i.target, actual: i.actual, trend: i.trend, notes: i.notes })
    setModal({ mode: 'edit', item: i })
  }
  async function save(e: React.FormEvent) {
    e.preventDefault(); setBusy(true)
    try {
      if (modal?.mode === 'edit' && modal.item) {
        const u = await api.put<Indicator>(`/head/indicators/${modal.item.id}`, form)
        setData((prev) => (prev || []).map((x) => (x.id === u.id ? u : x)))
      } else {
        const c = await api.post<Indicator>('/head/indicators', form)
        setData((prev) => [c, ...(prev || [])])
      }
      setModal(null)
    } catch (err) { alert(err instanceof Error ? err.message : 'Erro ao salvar') } finally { setBusy(false) }
  }
  async function remove(i: Indicator) {
    if (!confirm(`Excluir o indicador "${i.name}"?`)) return
    try { await api.del(`/head/indicators/${i.id}`); setData((prev) => (prev || []).filter((x) => x.id !== i.id)) }
    catch (err) { alert(err instanceof Error ? err.message : 'Erro ao excluir') }
  }

  return (
    <>
      <PageHead
        title="Indicadores & KPIs"
        subtitle="Metas mensais de operação, custo, adoção, qualidade e risco de IA"
        actions={canEdit ? <Button variant="primary" onClick={openCreate}>+ Novo indicador</Button> : undefined}
      />

      <Card style={{ marginBottom: '1.25rem' }}>
        <div className="row" style={{ gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <select value={catFilter} onChange={(e) => setCatFilter(e.target.value)} style={{ maxWidth: 200 }}>
            <option value="">Todas as categorias</option>
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={periodFilter} onChange={(e) => setPeriodFilter(e.target.value)} style={{ maxWidth: 160 }}>
            <option value="">Todos os períodos</option>
            {periods.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <span className="muted" style={{ marginLeft: 'auto', fontSize: '0.85rem' }}>
            <strong>{onTargetCount}/{filtered.length}</strong> na meta
          </span>
        </div>
      </Card>

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && !loading && (
        <Card>
          {filtered.length === 0 ? (
            <Empty>Nenhum indicador encontrado.</Empty>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Indicador</th><th>Categoria</th><th>Período</th><th>Meta</th>
                    <th>Realizado</th><th>Tendência</th><th>Situação</th>{canEdit && <th></th>}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((i) => {
                    const ok = onTarget(i)
                    return (
                      <tr key={i.id}>
                        <td style={{ fontWeight: 600 }}>{i.name}</td>
                        <td>{i.category}</td>
                        <td className="muted">{i.period}</td>
                        <td>{i.target}{i.unit}</td>
                        <td style={{ fontWeight: 600 }}>{i.actual}{i.unit}</td>
                        <td>{trendIcon(i.trend)} {i.trend}</td>
                        <td><Badge tone={ok ? 'success' : 'danger'}>{ok ? 'Na meta' : 'Fora da meta'}</Badge></td>
                        {canEdit && (
                          <td>
                            <div className="row" style={{ gap: '0.4rem', justifyContent: 'flex-end' }}>
                              <Button size="sm" variant="ghost" onClick={() => openEdit(i)}>Editar</Button>
                              <Button size="sm" variant="danger" onClick={() => remove(i)}>Excluir</Button>
                            </div>
                          </td>
                        )}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {modal && (
        <Modal title={modal.mode === 'edit' ? 'Editar indicador' : 'Novo indicador'} onClose={() => setModal(null)}>
          <form onSubmit={save}>
            <div className="field"><label>Nome do indicador</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="field"><label>Categoria</label>
                <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value as IndicatorCategory })}>
                  {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select></div>
              <div className="field"><label>Período (AAAA-MM)</label>
                <input value={form.period} placeholder="2026-08" onChange={(e) => setForm({ ...form, period: e.target.value })} /></div>
              <div className="field"><label>Meta</label>
                <input type="number" step="0.01" value={form.target} onChange={(e) => setForm({ ...form, target: Number(e.target.value) })} /></div>
              <div className="field"><label>Realizado</label>
                <input type="number" step="0.01" value={form.actual} onChange={(e) => setForm({ ...form, actual: Number(e.target.value) })} /></div>
              <div className="field"><label>Unidade</label>
                <input value={form.unit} placeholder="%, R$, h, un" onChange={(e) => setForm({ ...form, unit: e.target.value })} /></div>
              <div className="field"><label>Tendência</label>
                <select value={form.trend} onChange={(e) => setForm({ ...form, trend: e.target.value as Trend })}>
                  {TRENDS.map((t) => <option key={t} value={t}>{t}</option>)}
                </select></div>
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
