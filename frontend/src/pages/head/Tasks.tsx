import { useMemo, useState } from 'react'
import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { Card, Button, Badge, Modal, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { HeadTask, TaskStatus, Priority } from '@/types'

const STATUSES: TaskStatus[] = ['Pendente', 'Em andamento', 'Concluída', 'Bloqueada']
const PRIORITIES: Priority[] = ['Baixa', 'Média', 'Alta', 'Crítica']

const statusTone = (s: TaskStatus) =>
  s === 'Concluída' ? 'success' : s === 'Bloqueada' ? 'danger' : s === 'Em andamento' ? 'accent' : 'warning'
const prioTone = (p: Priority) => (p === 'Crítica' ? 'danger' : p === 'Alta' ? 'warning' : p === 'Média' ? 'accent' : 'default')

const today = () => new Date().toISOString().slice(0, 10)
const emptyForm = {
  title: '', description: '', responsible: '', category: 'Operação',
  status: 'Pendente' as TaskStatus, priority: 'Média' as Priority, task_date: today(), hours_spent: 0,
}

export default function Tasks() {
  const { data, loading, error, setData } = useAsync<HeadTask[]>(() => api.get('/head/tasks'))
  const [modal, setModal] = useState<null | { mode: 'create' | 'edit'; item?: HeadTask }>(null)
  const [form, setForm] = useState(emptyForm)
  const [busy, setBusy] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')

  const filtered = useMemo(
    () => (data || []).filter((t) => !statusFilter || t.status === statusFilter),
    [data, statusFilter],
  )
  const totalHours = useMemo(() => filtered.reduce((s, t) => s + (t.hours_spent || 0), 0), [filtered])

  function openCreate() { setForm({ ...emptyForm, task_date: today() }); setModal({ mode: 'create' }) }
  function openEdit(t: HeadTask) {
    setForm({
      title: t.title, description: t.description, responsible: t.responsible, category: t.category,
      status: t.status, priority: t.priority, task_date: t.task_date, hours_spent: t.hours_spent,
    })
    setModal({ mode: 'edit', item: t })
  }
  async function save(e: React.FormEvent) {
    e.preventDefault(); setBusy(true)
    try {
      if (modal?.mode === 'edit' && modal.item) {
        const u = await api.put<HeadTask>(`/head/tasks/${modal.item.id}`, form)
        setData((prev) => (prev || []).map((x) => (x.id === u.id ? u : x)))
      } else {
        const c = await api.post<HeadTask>('/head/tasks', form)
        setData((prev) => [c, ...(prev || [])])
      }
      setModal(null)
    } catch (err) { alert(err instanceof Error ? err.message : 'Erro ao salvar') } finally { setBusy(false) }
  }
  async function remove(t: HeadTask) {
    if (!confirm(`Excluir a tarefa "${t.title}"?`)) return
    try { await api.del(`/head/tasks/${t.id}`); setData((prev) => (prev || []).filter((x) => x.id !== t.id)) }
    catch (err) { alert(err instanceof Error ? err.message : 'Erro ao excluir') }
  }

  return (
    <>
      <PageHead
        title="Tarefas do Dia a Dia"
        subtitle="Atividades operacionais da equipe de IA com esforço e status"
        actions={<Button variant="primary" onClick={openCreate}>+ Nova tarefa</Button>}
      />

      <Card style={{ marginBottom: '1.25rem' }}>
        <div className="row" style={{ gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ maxWidth: 220 }}>
            <option value="">Todos os status</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <span className="muted" style={{ marginLeft: 'auto', fontSize: '0.85rem' }}>
            {filtered.length} tarefas · <strong>{totalHours}h</strong> registradas
          </span>
        </div>
      </Card>

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && !loading && (
        <Card>
          {filtered.length === 0 ? (
            <Empty>Nenhuma tarefa encontrada.</Empty>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Tarefa</th><th>Responsável</th><th>Categoria</th><th>Prioridade</th>
                    <th>Horas</th><th>Data</th><th>Status</th><th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((t) => (
                    <tr key={t.id}>
                      <td style={{ fontWeight: 600 }}>{t.title}
                        {t.description && <div className="muted" style={{ fontSize: '0.75rem' }}>{t.description}</div>}</td>
                      <td>{t.responsible || '—'}</td>
                      <td>{t.category}</td>
                      <td><Badge tone={prioTone(t.priority)}>{t.priority}</Badge></td>
                      <td>{t.hours_spent}h</td>
                      <td className="muted">{t.task_date || '—'}</td>
                      <td><Badge tone={statusTone(t.status)}>{t.status}</Badge></td>
                      <td>
                        <div className="row" style={{ gap: '0.4rem', justifyContent: 'flex-end' }}>
                          <Button size="sm" variant="ghost" onClick={() => openEdit(t)}>Editar</Button>
                          <Button size="sm" variant="danger" onClick={() => remove(t)}>Excluir</Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {modal && (
        <Modal title={modal.mode === 'edit' ? 'Editar tarefa' : 'Nova tarefa'} onClose={() => setModal(null)}>
          <form onSubmit={save}>
            <div className="field"><label>Título</label>
              <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></div>
            <div className="field"><label>Descrição</label>
              <textarea rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="field"><label>Responsável</label>
                <input value={form.responsible} onChange={(e) => setForm({ ...form, responsible: e.target.value })} /></div>
              <div className="field"><label>Categoria</label>
                <input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} /></div>
              <div className="field"><label>Prioridade</label>
                <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value as Priority })}>
                  {PRIORITIES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Status</label>
                <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as TaskStatus })}>
                  {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Data</label>
                <input type="date" value={form.task_date} onChange={(e) => setForm({ ...form, task_date: e.target.value })} /></div>
              <div className="field"><label>Horas gastas</label>
                <input type="number" min={0} step="0.5" value={form.hours_spent} onChange={(e) => setForm({ ...form, hours_spent: Number(e.target.value) })} /></div>
            </div>
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
