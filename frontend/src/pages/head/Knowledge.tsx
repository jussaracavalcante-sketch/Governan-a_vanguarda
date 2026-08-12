import { useMemo, useState } from 'react'
import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { Card, Button, Badge, Modal, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { KnowledgeArticle, KnowledgeStatus } from '@/types'

const STATUSES: KnowledgeStatus[] = ['Rascunho', 'Publicado', 'Arquivado']
const statusTone = (s: KnowledgeStatus) => (s === 'Publicado' ? 'success' : s === 'Rascunho' ? 'warning' : 'default')
const today = () => new Date().toISOString().slice(0, 10)

const emptyForm = {
  title: '', category: 'Geral', summary: '', content: '', tags: '',
  author: '', status: 'Publicado' as KnowledgeStatus, updated_date: today(),
}

export default function Knowledge() {
  const { data, loading, error, setData } = useAsync<KnowledgeArticle[]>(() => api.get('/head/knowledge'))
  const [modal, setModal] = useState<null | { mode: 'create' | 'edit' | 'view'; item?: KnowledgeArticle }>(null)
  const [form, setForm] = useState(emptyForm)
  const [busy, setBusy] = useState(false)
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return data || []
    return (data || []).filter((a) =>
      a.title.toLowerCase().includes(q) || a.summary.toLowerCase().includes(q) || a.tags.toLowerCase().includes(q))
  }, [data, search])

  function openCreate() { setForm({ ...emptyForm, updated_date: today() }); setModal({ mode: 'create' }) }
  function openEdit(a: KnowledgeArticle) {
    setForm({ title: a.title, category: a.category, summary: a.summary, content: a.content, tags: a.tags, author: a.author, status: a.status, updated_date: a.updated_date || today() })
    setModal({ mode: 'edit', item: a })
  }
  async function save(e: React.FormEvent) {
    e.preventDefault(); setBusy(true)
    try {
      if (modal?.mode === 'edit' && modal.item) {
        const u = await api.put<KnowledgeArticle>(`/head/knowledge/${modal.item.id}`, form)
        setData((prev) => (prev || []).map((x) => (x.id === u.id ? u : x)))
      } else {
        const c = await api.post<KnowledgeArticle>('/head/knowledge', form)
        setData((prev) => [c, ...(prev || [])])
      }
      setModal(null)
    } catch (err) { alert(err instanceof Error ? err.message : 'Erro ao salvar') } finally { setBusy(false) }
  }
  async function remove(a: KnowledgeArticle) {
    if (!confirm(`Excluir o artigo "${a.title}"?`)) return
    try { await api.del(`/head/knowledge/${a.id}`); setData((prev) => (prev || []).filter((x) => x.id !== a.id)) }
    catch (err) { alert(err instanceof Error ? err.message : 'Erro ao excluir') }
  }

  return (
    <>
      <PageHead
        title="Base de Conhecimento"
        subtitle="Políticas, runbooks e guias do HEAD de IA"
        actions={<Button variant="primary" onClick={openCreate}>+ Novo artigo</Button>}
      />

      <Card style={{ marginBottom: '1.25rem' }}>
        <input placeholder="Buscar por título, resumo ou tag…" value={search} onChange={(e) => setSearch(e.target.value)} />
      </Card>

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && !loading && (
        filtered.length === 0 ? (
          <Card><Empty>Nenhum artigo encontrado.</Empty></Card>
        ) : (
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
            {filtered.map((a) => (
              <Card key={a.id}>
                <div className="row" style={{ justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <Badge tone="accent">{a.category}</Badge>
                  <Badge tone={statusTone(a.status)}>{a.status}</Badge>
                </div>
                <div className="card-title" style={{ cursor: 'pointer' }} onClick={() => setModal({ mode: 'view', item: a })}>{a.title}</div>
                <p className="muted" style={{ fontSize: '0.85rem', margin: '0.35rem 0 0.75rem' }}>{a.summary || 'Sem resumo.'}</p>
                {a.tags && (
                  <div className="row" style={{ gap: '0.35rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
                    {a.tags.split(',').map((t) => t.trim()).filter(Boolean).map((t) => (
                      <span key={t} className="badge" style={{ fontSize: '0.7rem' }}>#{t}</span>
                    ))}
                  </div>
                )}
                <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="muted" style={{ fontSize: '0.72rem' }}>{a.author || '—'} · {a.updated_date || '—'}</span>
                  <div className="row" style={{ gap: '0.4rem' }}>
                    <Button size="sm" variant="ghost" onClick={() => setModal({ mode: 'view', item: a })}>Ler</Button>
                    <Button size="sm" variant="ghost" onClick={() => openEdit(a)}>Editar</Button>
                    <Button size="sm" variant="danger" onClick={() => remove(a)}>Excluir</Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )
      )}

      {modal?.mode === 'view' && modal.item && (
        <Modal title={modal.item.title} onClose={() => setModal(null)}>
          <div className="row" style={{ gap: '0.5rem', marginBottom: '0.75rem' }}>
            <Badge tone="accent">{modal.item.category}</Badge>
            <Badge tone={statusTone(modal.item.status)}>{modal.item.status}</Badge>
          </div>
          {modal.item.summary && <p style={{ marginBottom: '0.75rem', fontStyle: 'italic' }}>{modal.item.summary}</p>}
          <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', lineHeight: 1.6 }}>{modal.item.content || 'Sem conteúdo.'}</div>
          <p className="muted" style={{ fontSize: '0.72rem', marginTop: '1rem' }}>
            {modal.item.author || '—'} · atualizado em {modal.item.updated_date || '—'}
          </p>
        </Modal>
      )}

      {(modal?.mode === 'create' || modal?.mode === 'edit') && (
        <Modal title={modal.mode === 'edit' ? 'Editar artigo' : 'Novo artigo'} onClose={() => setModal(null)}>
          <form onSubmit={save}>
            <div className="field"><label>Título</label>
              <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></div>
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="field"><label>Categoria</label>
                <input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} /></div>
              <div className="field"><label>Status</label>
                <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as KnowledgeStatus })}>
                  {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select></div>
              <div className="field"><label>Autor</label>
                <input value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })} /></div>
              <div className="field"><label>Data de atualização</label>
                <input type="date" value={form.updated_date} onChange={(e) => setForm({ ...form, updated_date: e.target.value })} /></div>
            </div>
            <div className="field"><label>Resumo</label>
              <input value={form.summary} onChange={(e) => setForm({ ...form, summary: e.target.value })} maxLength={300} /></div>
            <div className="field"><label>Tags (separadas por vírgula)</label>
              <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} placeholder="governança, runbook, finops" /></div>
            <div className="field"><label>Conteúdo</label>
              <textarea rows={6} value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} /></div>
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
