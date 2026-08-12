import { useMemo, useState } from 'react'
import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { useAuth } from '@/context/AuthContext'
import { brl } from '@/lib/format'
import { Card, Button, Badge, Modal, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { License, LicenseStatus } from '@/types'

const STATUSES: LicenseStatus[] = ['Ativa', 'Em renovação', 'Expirada', 'Cancelada']
const statusTone = (s: LicenseStatus) =>
  s === 'Ativa' ? 'success' : s === 'Em renovação' ? 'warning' : s === 'Expirada' ? 'danger' : 'default'

const emptyForm = {
  software: '', vendor: '', plan: '', seats_total: 0, seats_used: 0,
  monthly_cost: 0, status: 'Ativa' as LicenseStatus, renewal_date: '', owner: '', notes: '',
}

export default function Licenses() {
  const { user } = useAuth()
  const canEdit = user?.role === 'Admin' || user?.role === 'Manager'
  const { data, loading, error, setData } = useAsync<License[]>(() => api.get('/head/licenses'))
  const [modal, setModal] = useState<null | { mode: 'create' | 'edit'; item?: License }>(null)
  const [form, setForm] = useState(emptyForm)
  const [busy, setBusy] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')

  const filtered = useMemo(
    () => (data || []).filter((l) => !statusFilter || l.status === statusFilter),
    [data, statusFilter],
  )
  const totals = useMemo(() => ({
    cost: filtered.reduce((s, l) => s + (l.monthly_cost || 0), 0),
    seats: filtered.reduce((s, l) => s + (l.seats_total || 0), 0),
    used: filtered.reduce((s, l) => s + (l.seats_used || 0), 0),
  }), [filtered])

  function openCreate() { setForm(emptyForm); setModal({ mode: 'create' }) }
  function openEdit(l: License) {
    setForm({
      software: l.software, vendor: l.vendor, plan: l.plan, seats_total: l.seats_total, seats_used: l.seats_used,
      monthly_cost: l.monthly_cost, status: l.status, renewal_date: l.renewal_date, owner: l.owner, notes: l.notes,
    })
    setModal({ mode: 'edit', item: l })
  }
  async function save(e: React.FormEvent) {
    e.preventDefault(); setBusy(true)
    try {
      if (modal?.mode === 'edit' && modal.item) {
        const u = await api.put<License>(`/head/licenses/${modal.item.id}`, form)
        setData((prev) => (prev || []).map((x) => (x.id === u.id ? u : x)))
      } else {
        const c = await api.post<License>('/head/licenses', form)
        setData((prev) => [c, ...(prev || [])])
      }
      setModal(null)
    } catch (err) { alert(err instanceof Error ? err.message : 'Erro ao salvar') } finally { setBusy(false) }
  }
  async function remove(l: License) {
    if (!confirm(`Excluir a licença "${l.software}"?`)) return
    try { await api.del(`/head/licenses/${l.id}`); setData((prev) => (prev || []).filter((x) => x.id !== l.id)) }
    catch (err) { alert(err instanceof Error ? err.message : 'Erro ao excluir') }
  }

  return (
    <>
      <PageHead
        title="Controle de Licenças"
        subtitle="Assinaturas e licenças de IA, assentos e custos de renovação"
        actions={canEdit ? <Button variant="primary" onClick={openCreate}>+ Nova licença</Button> : undefined}
      />

      <Card style={{ marginBottom: '1.25rem' }}>
        <div className="row" style={{ gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ maxWidth: 220 }}>
            <option value="">Todos os status</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <span className="muted" style={{ marginLeft: 'auto', fontSize: '0.85rem' }}>
            {filtered.length} licenças · <strong>{brl(totals.cost)}</strong>/mês · {totals.used}/{totals.seats} assentos
          </span>
        </div>
      </Card>

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && !loading && (
        <Card>
          {filtered.length === 0 ? (
            <Empty>Nenhuma licença encontrada.</Empty>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Software</th><th>Plano</th><th>Assentos</th><th>Custo/mês</th>
                    <th>Renovação</th><th>Status</th>{canEdit && <th></th>}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((l) => {
                    const util = l.seats_total ? Math.round((l.seats_used / l.seats_total) * 100) : 0
                    return (
                      <tr key={l.id}>
                        <td style={{ fontWeight: 600 }}>{l.software}
                          {l.vendor && <div className="muted" style={{ fontSize: '0.75rem' }}>{l.vendor}</div>}</td>
                        <td>{l.plan || '—'}</td>
                        <td>{l.seats_used}/{l.seats_total} <span className="muted">({util}%)</span></td>
                        <td>{brl(l.monthly_cost)}</td>
                        <td className="muted">{l.renewal_date || '—'}</td>
                        <td><Badge tone={statusTone(l.status)}>{l.status}</Badge></td>
                        {canEdit && (
                          <td>
                            <div className="row" style={{ gap: '0.4rem', justifyContent: 'flex-end' }}>
                              <Button size="sm" variant="ghost" onClick={() => openEdit(l)}>Editar</Button>
                              <Button size="sm" variant="danger" onClick={() => remove(l)}>Excluir</Button>
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
        <Modal title={modal.mode === 'edit' ? 'Editar licença' : 'Nova licença'} onClose={() => setModal(null)}>
          <form onSubmit={save}>
            <div className="field"><label>Software</label>
              <input value={form.software} onChange={(e) => setForm({ ...form, software: e.target.value })} required /></div>
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="field"><label>Fornecedor</label>
                <input value={form.vendor} onChange={(e) => setForm({ ...form, vendor: e.target.value })} /></div>
              <div className="field"><label>Plano</label>
                <input value={form.plan} onChange={(e) => setForm({ ...form, plan: e.target.value })} /></div>
              <div className="field"><label>Assentos totais</label>
                <input type="number" min={0} value={form.seats_total} onChange={(e) => setForm({ ...form, seats_total: Number(e.target.value) })} /></div>
              <div className="field"><label>Assentos em uso</label>
                <input type="number" min={0} value={form.seats_used} onChange={(e) => setForm({ ...form, seats_used: Number(e.target.value) })} /></div>
              <div className="field"><label>Custo mensal (R$)</label>
                <input type="number" min={0} step="0.01" value={form.monthly_cost} onChange={(e) => setForm({ ...form, monthly_cost: Number(e.target.value) })} /></div>
              <div className="field"><label>Status</label>
                <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as LicenseStatus })}>
                  {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Data de renovação</label>
                <input type="date" value={form.renewal_date} onChange={(e) => setForm({ ...form, renewal_date: e.target.value })} /></div>
              <div className="field"><label>Responsável</label>
                <input value={form.owner} onChange={(e) => setForm({ ...form, owner: e.target.value })} /></div>
            </div>
            <div className="field"><label>Observações</label>
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
