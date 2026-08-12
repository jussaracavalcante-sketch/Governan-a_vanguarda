// Utilitários de formatação (pt-BR) para o app Gestão HEAD de IA.

export const brl = (v: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v || 0)

export const num = (v: number) => new Intl.NumberFormat('pt-BR').format(v || 0)

/** Período atual no formato YYYY-MM. */
export const currentPeriod = () => new Date().toISOString().slice(0, 7)
