import type { MonthlyReport } from '@/types'

const money = (n: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(n || 0)

const ACCENT: [number, number, number] = [176, 30, 36]
const ACCENT2: [number, number, number] = [212, 44, 56]

// ─────────────────────────────── PDF ───────────────────────────────
export async function exportReportPDF(r: MonthlyReport) {
  const { jsPDF } = await import('jspdf')
  const autoTable = (await import('jspdf-autotable')).default
  const doc = new jsPDF()

  doc.setFontSize(16)
  doc.text('Relatório Mensal — Gestão HEAD de IA', 14, 18)
  doc.setFontSize(10)
  doc.setTextColor(120)
  doc.text(`Projeto Executivo Head de IA · Período: ${r.period}`, 14, 25)
  doc.setTextColor(0)

  autoTable(doc, {
    startY: 32,
    head: [['Resumo do período', 'Valor']],
    body: [
      ['Tarefas no mês', String(r.tasks_total)],
      ['Tarefas concluídas', String(r.tasks_done)],
      ['Horas registradas', `${r.tasks_hours}h`],
      ['KPIs na meta', `${r.kpis_on_target}/${r.kpis_on_target + r.kpis_off_target}`],
      ['Custo de ativos', money(r.assets_monthly_cost)],
      ['Custo de licenças', money(r.licenses_monthly_cost)],
      ['Custo mensal total', money(r.total_monthly_cost)],
    ],
    theme: 'grid',
    headStyles: { fillColor: ACCENT },
  })

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let y = (doc as any).lastAutoTable.finalY + 8
  autoTable(doc, {
    startY: y,
    head: [['Tarefas por status', 'Quantidade', 'Horas']],
    body: r.tasks_by_status.map((b) => [b.status, String(b.count), `${b.hours}h`]),
    theme: 'grid',
    headStyles: { fillColor: ACCENT2 },
  })

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  y = (doc as any).lastAutoTable.finalY + 8
  autoTable(doc, {
    startY: y,
    head: [['Indicador', 'Categoria', 'Meta', 'Realizado', 'Tendência']],
    body: r.indicators.map((i) => [i.name, i.category, `${i.target}${i.unit}`, `${i.actual}${i.unit}`, i.trend]),
    theme: 'grid',
    headStyles: { fillColor: ACCENT },
    styles: { fontSize: 8 },
  })

  doc.save(`relatorio-head-ia-${r.period}.pdf`)
}

// ─────────────────────────────── PPTX ───────────────────────────────
export async function exportReportPPTX(r: MonthlyReport) {
  const PptxGenJS = (await import('pptxgenjs')).default
  const p = new PptxGenJS()
  p.author = 'Gestão HEAD de IA'
  p.title = `Relatório ${r.period}`

  // Slide 1 — capa
  const s1 = p.addSlide()
  s1.background = { color: '080708' }
  s1.addText('Gestão HEAD de IA', { x: 0.6, y: 1.8, w: 8.8, h: 1, fontSize: 40, bold: true, color: 'FFFFFF' })
  s1.addText(`Relatório Mensal · ${r.period}`, { x: 0.6, y: 2.9, w: 8.8, h: 0.6, fontSize: 20, color: 'B01E24' })
  s1.addText('Projeto Executivo Head de IA — Grupo Vanguarda', { x: 0.6, y: 3.5, w: 8.8, h: 0.5, fontSize: 14, color: 'AFA8B0' })

  // Slide 2 — indicadores executivos (KPIs em cartões)
  const s2 = p.addSlide()
  s2.background = { color: 'F4F1F5' }
  s2.addText('Resumo executivo', { x: 0.5, y: 0.3, w: 9, h: 0.6, fontSize: 24, bold: true, color: '080708' })
  const cards: [string, string][] = [
    ['Tarefas concluídas', `${r.tasks_done}/${r.tasks_total}`],
    ['Horas registradas', `${r.tasks_hours}h`],
    ['KPIs na meta', `${r.kpis_on_target}/${r.kpis_on_target + r.kpis_off_target}`],
    ['Custo mensal total', money(r.total_monthly_cost)],
  ]
  cards.forEach((c, idx) => {
    const x = 0.5 + (idx % 2) * 4.7
    const yy = 1.2 + Math.floor(idx / 2) * 1.9
    s2.addShape(p.ShapeType.roundRect, { x, y: yy, w: 4.3, h: 1.6, fill: { color: 'FFFFFF' }, line: { color: 'E2DBE5' }, rectRadius: 0.1 })
    s2.addText(c[0], { x: x + 0.2, y: yy + 0.2, w: 3.9, h: 0.4, fontSize: 12, color: '6B6470' })
    s2.addText(c[1], { x: x + 0.2, y: yy + 0.6, w: 3.9, h: 0.8, fontSize: 30, bold: true, color: '080708' })
  })

  // Slide 3 — indicadores (tabela)
  const s3 = p.addSlide()
  s3.background = { color: 'FFFFFF' }
  s3.addText('Indicadores de Sucesso', { x: 0.5, y: 0.3, w: 9, h: 0.6, fontSize: 24, bold: true, color: '080708' })
  const indRows = [
    [
      { text: 'Indicador', options: { bold: true, color: 'FFFFFF', fill: { color: 'B01E24' } } },
      { text: 'Meta', options: { bold: true, color: 'FFFFFF', fill: { color: 'B01E24' } } },
      { text: 'Realizado', options: { bold: true, color: 'FFFFFF', fill: { color: 'B01E24' } } },
      { text: 'Tendência', options: { bold: true, color: 'FFFFFF', fill: { color: 'B01E24' } } },
    ],
    ...r.indicators.map((i) => [
      { text: i.name },
      { text: `${i.target}${i.unit}` },
      { text: `${i.actual}${i.unit}` },
      { text: i.trend || '—' },
    ]),
  ]
  s3.addTable(indRows as never, { x: 0.5, y: 1.1, w: 9, colW: [4.5, 1.5, 1.5, 1.5], fontSize: 11, border: { pt: 1, color: 'E2DBE5' }, valign: 'middle' })

  await p.writeFile({ fileName: `relatorio-head-ia-${r.period}.pptx` })
}
