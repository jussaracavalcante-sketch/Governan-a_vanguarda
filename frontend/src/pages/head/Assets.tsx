import { useMemo, useState } from 'react'
import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { useAuth } from '@/context/AuthContext'
import { brl } from '@/lib/format'
import { Card, Button, Badge, Modal, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { Asset, AssetType, AssetStatus, Environment, Criticality } from '@/types'

const TYPES: AssetType[] = ['Modelo LLM', 'Agente', 'Automação', 'Integração', 'Dataset', 'Infraestrutura']
const STATUSES: AssetStatus[] = ['Ativo', 'Em avaliação', 'Descontinuado']
const ENVS: Environment[] = ['Produção', 'Homologação', 'Desenvolvimento']
const CRITS: Criticality[] = ['Baixa', 'Média', 'Alta', 'Crítica']

const statusTone = (s: AssetStatus) => (s === 'Ativo' ? 'success' : s === 'Em avaliação' ? 'warning' : 'danger')
const critTone = (c: Criticality) => (c === 'Crítica' ? 'danger' : c === 'Alta' ? 'warning' : c === 'Média' ? 'accent' : 'default')

const emptyForm = {
  name: '', asset_type: 'Modelo LLM' as AssetType, vendor: '', owner: '',
  status: 'Ativo' as AssetStatus, environment: 'Produção' as Environment,
  criticality: 'Média' as Criticality, monthly_cost: 0, description: '', acquisition_date: '',
}

export default function Assets() {
  const { user } = useAuth()
  const canEdit = user?.role === 'Admin' || user?.role === 'Manager'
  const { data, loading, error, setData } = useAsync<Asset[]>(() => api.get('/head/assets'))
  const [modal, setModal] = useState<null | { mode: 'create' | 'edit'; item?: Asset }>(null)
  const [form, setForm] = useState(emptyForm)
  const [busy, setBusy] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  const filtered = useMemo(
    () => (data || []).filter((a) => (!statusFilter || a.status === statusFilter) && (!typeFilter || a.asset_type === typeFilter)),
    [data, statusFilter, typeFilter],
  )
  const totalCost = useMemo(() => filtered.reduce((s, a) => s + (a.monthly_cost || 0), 0), [filtered])

  function openCreate() { setForm(emptyForm); setModal({ mode: 'create' }) }
  function openEdit(a: Asset) {
    setForm({
      name: a.name, asset_type: a.asset_type, vendor: a.vendor, owner: a.owner, status: a.status,
      environment: a.environment, criticality: a.criticality, monthly_cost: a.monthly_cost,
      description: a.description, acquisition_date: a.acquisition_date,
    })
    setModal({ mode: 'edit', item: a })
  }
  async function save(e: React.FormEvent) {
    e.preventDefault(); setBusy(true)
    try {
      if (modal?.mode === 'edit' && modal.item) {
        const u = await api.put<Asset>(`/head/assets/${modal.item.id}`, form)
        setData((prev) => (prev || []).map((x) => (x.id === u.id ? u : x)))
      } else {
        const c = await api.post<Asset>('/head/assets', form)
        setData((prev) => [c, ...(prev || [])])
      }
      setModal(null)
    } catch (err) { alert(err instanceof Error ? err.message : 'Erro ao salvar') } finally { setBusy(false) }
  }
  async function remove(a: Asset) {
    if (!confirm(`Excluir o ativo "${a.name}"?`)) return
    try { await api.del(`/head/assets/${a.id}`); setData((prev) => (prev || []).filter((x) => x.id !== a.id)) }
    catch (err) { alert(err instanceof Error ? err.message : 'Erro ao excluir') }
  }

  return (
    <>
      <PageHead
        title="Controle de Ativos"
        subtitle="Modelos, agentes, automações e integrações de IA sob gestão"
        actions={canEdit ? <Button variant="primary" onClick={openCreate}>+ Novo ativo</Button> : undefined}
      />

      <Card style={{ marginBottom: '1.25rem' }}>
        <div className="row" style={{ gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} style={{ maxWidth: 220 }}>
            <option value="">Todos os tipos</option>
            {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ maxWidth: 200 }}>
            <option value="">Todos os status</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <span className="muted" style={{ marginLeft: 'auto', fontSize: '0.85rem' }}>
            {filtered.length} ativos · <strong>{brl(totalCost)}</strong>/mês
          </span>
        </div>
      </Card>

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && !loading && (
        <Card>
          {filtered.length === 0 ? (
            <Empty>Nenhum ativo encontrado.</Empty>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Ativo</th><th>Tipo</th><th>Fornecedor</th><th>Ambiente</th>
                    <th>Criticidade</th><th>Custo/mês</th><th>Status</th>{canEdit && <th></th>}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((a) => (
                    <tr key={a.id}>
                      <td style={{ fontWeight: 600 }}>{a.name}{a.owner && <div className="muted" style={{ fontSize: '0.75rem' }}>{a.owner}</div>}</td>
                      <td>{a.asset_type}</td>
                      <td>{a.vendor || '—'}</td>
                      <td>{a.environment}</td>
                      <td><Badge tone={critTone(a.criticality)}>{a.criticality}</Badge></td>
                      <td>{brl(a.monthly_cost)}</td>
                      <td><Badge tone={statusTone(a.status)}>{a.status}</Badge></td>
                      {canEdit && (
                        <td>
                          <div className="row" style={{ gap: '0.4rem', justifyContent: 'flex-end' }}>
                            <Button size="sm" variant="ghost" onClick={() => openEdit(a)}>Editar</Button>
                            <Button size="sm" variant="danger" onClick={() => remove(a)}>Excluir</Button>
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
        <Modal title={modal.mode === 'edit' ? 'Editar ativo' : 'Novo ativo'} onClose={() => setModal(null)}>
          <form onSubmit={save}>
            <div className="field"><label>Nome</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="field"><label>Tipo</label>
                <select value={form.asset_type} onChange={(e) => setForm({ ...form, asset_type: e.target.value as AssetType })}>
                  {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                </select></div>
              <div className="field"><label>Fornecedor</label>
                <input value={form.vendor} onChange={(e) => setForm({ ...form, vendor: e.target.value })} /></div>
              <div className="field"><label>Responsável</label>
                <input value={form.owner} onChange={(e) => setForm({ ...form, owner: e.target.value })} /></div>
              <div className="field"><label>Ambiente</label>
                <select value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value as Environment })}>
                  {ENVS.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Criticidade</label>
                <select value={form.criticality} onChange={(e) => setForm({ ...form, criticality: e.target.value as Criticality })}>
                  {CRITS.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Status</label>
                <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as AssetStatus })}>
                  {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Custo mensal (R$)</label>
                <input type="number" min={0} step="0.01" value={form.monthly_cost} onChange={(e) => setForm({ ...form, monthly_cost: Number(e.target.value) })} /></div>
              <div className="field"><label>Data de aquisição</label>
                <input type="date" value={form.acquisition_date} onChange={(e) => setForm({ ...form, acquisition_date: e.target.value })} /></div>
            </div>
            <div className="field"><label>Descrição</label>
              <textarea rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
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
