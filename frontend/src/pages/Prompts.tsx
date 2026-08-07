import { useMemo, useState } from 'react'
import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { useAuth } from '@/context/AuthContext'
import { Card, Button, Badge, Modal, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { Prompt } from '@/types'

const emptyForm = { title: '', category: '', text: '', is_favorite: false }

export default function Prompts() {
  const { user } = useAuth()
  const canEdit = user?.role === 'Admin' || user?.role === 'Manager'
  const { data, loading, error, setData } = useAsync<Prompt[]>(() => api.get('/prompts'))
  const [search, setSearch] = useState('')
  const [cat, setCat] = useState('')
  const [modal, setModal] = useState<null | { mode: 'create' | 'edit'; prompt?: Prompt }>(null)
  const [form, setForm] = useState(emptyForm)
  const [busy, setBusy] = useState(false)
  const [copied, setCopied] = useState<number | null>(null)

  const categories = useMemo(
    () => Array.from(new Set((data || []).map((p) => p.category))).sort(),
    [data],
  )
  const filtered = useMemo(() => {
    return (data || []).filter((p) => {
      const q = search.toLowerCase()
      const matchesQ = !q || p.title.toLowerCase().includes(q) || p.text.toLowerCase().includes(q)
      const matchesCat = !cat || p.category === cat
      return matchesQ && matchesCat
    })
  }, [data, search, cat])

  function openCreate() {
    setForm(emptyForm)
    setModal({ mode: 'create' })
  }
  function openEdit(p: Prompt) {
    setForm({ title: p.title, category: p.category, text: p.text, is_favorite: p.is_favorite })
    setModal({ mode: 'edit', prompt: p })
  }

  async function save(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    try {
      if (modal?.mode === 'edit' && modal.prompt) {
        const updated = await api.put<Prompt>(`/prompts/${modal.prompt.id}`, form)
        setData((prev) => (prev || []).map((p) => (p.id === updated.id ? updated : p)))
      } else {
        const created = await api.post<Prompt>('/prompts', form)
        setData((prev) => [created, ...(prev || [])])
      }
      setModal(null)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erro ao salvar')
    } finally {
      setBusy(false)
    }
  }

  async function remove(p: Prompt) {
    if (!confirm(`Excluir o prompt "${p.title}"?`)) return
    try {
      await api.del(`/prompts/${p.id}`)
      setData((prev) => (prev || []).filter((x) => x.id !== p.id))
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erro ao excluir')
    }
  }

  async function toggleFav(p: Prompt) {
    try {
      const updated = await api.put<Prompt>(`/prompts/${p.id}`, { is_favorite: !p.is_favorite })
      setData((prev) => (prev || []).map((x) => (x.id === updated.id ? updated : x)))
    } catch {
      /* silencioso */
    }
  }

  async function copy(p: Prompt) {
    try {
      await navigator.clipboard.writeText(p.text)
      setCopied(p.id)
      setTimeout(() => setCopied((c) => (c === p.id ? null : c)), 1500)
    } catch {
      /* clipboard indisponível */
    }
  }

  return (
    <>
      <PageHead
        title="Biblioteca de Prompts"
        subtitle="Acervo institucional versionado e homologado (NIA-001)"
        actions={canEdit ? <Button variant="primary" onClick={openCreate}>+ Novo prompt</Button> : undefined}
      />

      <Card style={{ marginBottom: '1.25rem' }}>
        <div className="row" style={{ gap: '0.75rem', flexWrap: 'wrap' }}>
          <input
            placeholder="Buscar por título ou conteúdo…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ flex: 1, minWidth: 220 }}
          />
          <select value={cat} onChange={(e) => setCat(e.target.value)} style={{ maxWidth: 220 }}>
            <option value="">Todas as categorias</option>
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </Card>

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && !loading && (
        filtered.length === 0 ? (
          <Card><Empty>Nenhum prompt encontrado.</Empty></Card>
        ) : (
          <div className="grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
            {filtered.map((p) => (
              <Card key={p.id}>
                <div className="row" style={{ justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div className="card-title">{p.title}</div>
                    <Badge tone="accent">{p.category}</Badge>{' '}
                    <span className="muted" style={{ fontSize: '0.78rem' }}>{p.uses} usos</span>
                  </div>
                  <button
                    className="icon-btn"
                    onClick={() => toggleFav(p)}
                    title={p.is_favorite ? 'Remover dos favoritos' : 'Favoritar'}
                    aria-label="Favoritar"
                  >
                    {p.is_favorite ? '★' : '☆'}
                  </button>
                </div>
                <p
                  className="muted"
                  style={{
                    fontSize: '0.85rem',
                    margin: '0.75rem 0',
                    whiteSpace: 'pre-wrap',
                    maxHeight: 120,
                    overflow: 'hidden',
                  }}
                >
                  {p.text}
                </p>
                <div className="row" style={{ gap: '0.5rem', flexWrap: 'wrap' }}>
                  <Button size="sm" onClick={() => copy(p)}>
                    {copied === p.id ? '✓ Copiado' : 'Copiar'}
                  </Button>
                  {canEdit && (
                    <>
                      <Button size="sm" variant="ghost" onClick={() => openEdit(p)}>Editar</Button>
                      <Button size="sm" variant="danger" onClick={() => remove(p)}>Excluir</Button>
                    </>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )
      )}

      {modal && (
        <Modal title={modal.mode === 'edit' ? 'Editar prompt' : 'Novo prompt'} onClose={() => setModal(null)}>
          <form onSubmit={save}>
            <div className="field">
              <label>Título</label>
              <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
            </div>
            <div className="field">
              <label>Categoria</label>
              <input
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                placeholder="Ex.: Criação, Mídia, Atendimento"
                required
              />
            </div>
            <div className="field">
              <label>Prompt</label>
              <textarea
                value={form.text}
                onChange={(e) => setForm({ ...form, text: e.target.value })}
                rows={8}
                required
              />
            </div>
            <label className="row" style={{ gap: '0.5rem', fontSize: '0.85rem', marginBottom: '1rem' }}>
              <input
                type="checkbox"
                checked={form.is_favorite}
                onChange={(e) => setForm({ ...form, is_favorite: e.target.checked })}
                style={{ width: 'auto' }}
              />
              Marcar como favorito
            </label>
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
