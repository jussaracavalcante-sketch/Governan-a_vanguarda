import { useEffect, useState } from 'react'
import { api, ApiError } from '@/lib/api'
import { brl, currentPeriod } from '@/lib/format'
import { Card, StatCard, Badge, Spinner, Empty, Button } from '@/components/ui'
import { PageHead } from '@/components/layout/PageHead'
import { exportReportPDF, exportReportPPTX } from '@/lib/export'
import type { MonthlyReport } from '@/types'

export default function Reports() {
  const [period, setPeriod] = useState(currentPeriod())
  const [data, setData] = useState<MonthlyReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [exporting, setExporting] = useState<null | 'pdf' | 'pptx'>(null)

  async function download(kind: 'pdf' | 'pptx') {
    if (!data) return
    setExporting(kind)
    try {
      if (kind === 'pdf') await exportReportPDF(data)
      else await exportReportPPTX(data)
    } catch {
      alert('Não foi possível gerar o arquivo. Tente novamente.')
    } finally {
      setExporting(null)
    }
  }

  useEffect(() => {
    let alive = true
    setLoading(true); setError(null)
    api.get<MonthlyReport>(`/head/report/${period}`)
      .then((d) => { if (alive) setData(d) })
      .catch((e) => { if (alive) setError(e instanceof ApiError ? e.message : 'Erro ao carregar relatório') })
      .finally(() => { if (alive) setLoading(false) })
    return () => { alive = false }
  }, [period])

  const completion = data && data.tasks_total ? Math.round((data.tasks_done / data.tasks_total) * 100) : 0

  return (
    <>
      <PageHead
        title="Relatórios Mensais"
        subtitle="Consolidação mensal de esforço, custos e desempenho de KPIs"
        actions={
          <div className="row" style={{ gap: '0.5rem', flexWrap: 'wrap' }}>
            <input
              type="month"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              style={{ maxWidth: 170 }}
            />
            <Button variant="ghost" onClick={() => download('pdf')} disabled={!data || exporting !== null}>
              {exporting === 'pdf' ? 'Gerando…' : '⬇️ PDF'}
            </Button>
            <Button variant="ghost" onClick={() => download('pptx')} disabled={!data || exporting !== null}>
              {exporting === 'pptx' ? 'Gerando…' : '⬇️ PPTX'}
            </Button>
          </div>
        }
      />

      {loading && <Spinner />}
      {error && <Card><Empty>{error}</Empty></Card>}

      {data && !loading && (
        <div className="stack">
          <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <StatCard label="Tarefas no mês" value={data.tasks_total} hint={`${data.tasks_done} concluídas (${completion}%)`} />
            <StatCard label="Horas registradas" value={`${data.tasks_hours}h`} hint="esforço total" />
            <StatCard label="Custo mensal total" value={brl(data.total_monthly_cost)} hint="ativos + licenças" />
            <StatCard label="KPIs na meta" value={`${data.kpis_on_target}/${data.kpis_on_target + data.kpis_off_target}`} hint={`${data.kpis_off_target} fora da meta`} />
          </div>

          <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
            <StatCard label="Custo de ativos" value={brl(data.assets_monthly_cost)} hint={`${data.assets_total} ativos`} />
            <StatCard label="Custo de licenças" value={brl(data.licenses_monthly_cost)} hint={`${data.licenses_total} licenças`} />
            <StatCard label="Taxa de conclusão" value={`${completion}%`} hint="tarefas concluídas no mês" />
          </div>

          <Card title="Tarefas por status" subtitle={`Distribuição de esforço em ${data.period}`}>
            {data.tasks_by_status.length === 0 ? (
              <Empty>Nenhuma tarefa registrada neste período.</Empty>
            ) : (
              <div className="table-wrap">
                <table className="table">
                  <thead><tr><th>Status</th><th>Quantidade</th><th>Horas</th></tr></thead>
                  <tbody>
                    {data.tasks_by_status.map((b) => (
                      <tr key={b.status}>
                        <td><Badge tone={b.status === 'Concluída' ? 'success' : b.status === 'Bloqueada' ? 'danger' : b.status === 'Em andamento' ? 'accent' : 'warning'}>{b.status}</Badge></td>
                        <td>{b.count}</td>
                        <td>{b.hours}h</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          <Card title="Indicadores do período" subtitle="Metas vs. realizado por KPI">
            {data.indicators.length === 0 ? (
              <Empty>Nenhum indicador cadastrado para {data.period}.</Empty>
            ) : (
              <div className="table-wrap">
                <table className="table">
                  <thead><tr><th>Indicador</th><th>Categoria</th><th>Meta</th><th>Realizado</th><th>Tendência</th></tr></thead>
                  <tbody>
                    {data.indicators.map((i) => (
                      <tr key={i.id}>
                        <td style={{ fontWeight: 600 }}>{i.name}</td>
                        <td>{i.category}</td>
                        <td>{i.target}{i.unit}</td>
                        <td style={{ fontWeight: 600 }}>{i.actual}{i.unit}</td>
                        <td className="muted">{i.trend}</td>
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
