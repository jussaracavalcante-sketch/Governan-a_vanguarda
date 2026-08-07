import { api } from '@/lib/api'
import { useAsync } from '@/lib/useAsync'
import { Card, Badge, Spinner, Empty } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import type { User } from '@/types'

const roleTone = (r: User['role']) => (r === 'Admin' ? 'danger' : r === 'Manager' ? 'accent' : 'default')

export default function Access() {
  const { data, loading, error } = useAsync<User[]>(() => api.get('/users'))

  return (
    <>
      <PageHead
        title="Controle de Acessos"
        subtitle="Usuários, perfis (RBAC) e status de acesso"
      />
      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}
      {data && !loading && (
        <Card>
          {data.length === 0 ? (
            <Empty>Nenhum usuário encontrado.</Empty>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr><th>Nome</th><th>E-mail</th><th>Perfil</th><th>Status</th><th>Último acesso</th></tr>
                </thead>
                <tbody>
                  {data.map((u) => (
                    <tr key={u.id}>
                      <td style={{ fontWeight: 600 }}>{u.name}</td>
                      <td className="muted">{u.email}</td>
                      <td><Badge tone={roleTone(u.role)}>{u.role}</Badge></td>
                      <td><Badge tone={u.status === 'Ativo' ? 'success' : 'danger'}>{u.status}</Badge></td>
                      <td className="muted">{u.last_access || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}
    </>
  )
}
