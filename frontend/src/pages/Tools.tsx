import { useMemo, useState } from 'react'
import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { useAuth } from '@/context/AuthContext'
import { Card, Button, Badge, Modal, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { Tool } from '@/types'

const STATUSES: Tool['status'][] = ['Ativa', 'Manutenção', 'Desativada']
const toneFor = (s: Tool['status']) =>
  s === 'Ativa' ? 'success' : s === 'Manutenção' ? 'warning' : 'danger'
const emptyForm = { name: '', category: '', team: '', status: 'Ativa' as Tool['status'], acquisition_date: '' }

export default function Tools() {
  const { user } = useAuth()
  const canEdit = user?.role === 'Admin' || user?.role === 'Manager'
  const { data, loading, error, setData } = useAsync<Tool[]>(() => api.get('/tools'))
  const [modal, setModal] = useState<null | { mode: 'create' | 'edit'; tool?: Tool }>(null)
  const [form, setForm] = useState(emptyForm)
  const [busy, setBusy] = useState(false)

  const filterState = useState('')
  const [statusFilter, setStatusFilter] = filterState
  const filtered = useMemo(
    () => (data || []).filter((t) => !statusFilter || t.status === statusFilter),
    [data, statusFilter],
  )

  function openCreate() {
    setForm(emptyForm)
    setModal({ mode: 'create' })
  }
  function openEdit(t: Tool) {
    setForm({ name: t.name, category: t.category, team: t.team, status: t.status, acquisition_date: t.acquisition_date })
    setModal({ mode: 'edit', tool: t })
  }
  async function save(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    try {
      if (modal?.mode === 'edit' && modal.tool) {
        const updated = await api.put<Tool>(`/tools/${modal.tool.id}`, form)
        setData((prev) => (prev || []).map((t) => (t.id === updated.id ? updated : t)))
      } else {
        const created = await api.post<Tool>('/tools', form)
        setData((prev) => [created, ...(prev || [])])
      }
      setModal(null)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erro ao salvar')
    } finally {
      setBusy(false)
    }
  }
  async function remove(t: Tool) {
    if (!confirm(`Excluir a ferramenta "${t.name}"?`)) return
    try {
      await api.del(`/tools/${t.id}`)
      setData((prev) => (prev || []).filter((x) => x.id !== t.id))
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erro ao excluir')
    }
  }

  return (
    <>
      <PageHead
        title="Stack & Ferramentas"
        subtitle="Ferramentas homologadas por time e status operacional"
        actions={canEdit ? <Button variant="primary" onClick={openCreate}>+ Nova ferramenta</Button> : undefined}
      />

      <Card style={{ marginBottom: '1.25rem' }}>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ maxWidth: 240 }}>
          <option value="">Todos os status</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </Card>

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && !loading && (
        <Card>
          {filtered.length === 0 ? (
            <Empty>Nenhuma ferramenta encontrada.</Empty>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Ferramenta</th><th>Categoria</th><th>Time</th><th>Status</th>
                    {canEdit && <th></th>}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((t) => (
                    <tr key={t.id}>
                      <td style={{ fontWeight: 600 }}>{t.name}</td>
                      <td>{t.category}</td>
                      <td>{t.team}</td>
                      <td><Badge tone={toneFor(t.status)}>{t.status}</Badge></td>
                      {canEdit && (
                        <td>
                          <div className="row" style={{ gap: '0.4rem', justifyContent: 'flex-end' }}>
                            <Button size="sm" variant="ghost" onClick={() => openEdit(t)}>Editar</Button>
                            <Button size="sm" variant="danger" onClick={() => remove(t)}>Excluir</Button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {modal && (
        <Modal title={modal.mode === 'edit' ? 'Editar ferramenta' : 'Nova ferramenta'} onClose={() => setModal(null)}>
          <form onSubmit={save}>
            <div className="field"><label>Nome</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
            <div className="field"><label>Categoria</label>
              <input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required /></div>
            <div className="field"><label>Time</label>
              <input value={form.team} onChange={(e) => setForm({ ...form, team: e.target.value })} required /></div>
            <div className="field"><label>Status</label>
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as Tool['status'] })}>
                {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select></div>
            <div className="field"><label>Data de aquisição</label>
              <input type="date" value={form.acquisition_date} onChange={(e) => setForm({ ...form, acquisition_date: e.target.value })} /></div>
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
