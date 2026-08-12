export type Role = 'Admin' | 'Manager' | 'User'
export type UserStatus = 'Ativo' | 'Inativo'

export interface User {
  id: number
  name: string
  email: string
  role: Role
  status: UserStatus
  is_superuser: boolean
  last_access: string
  created_at: string
  updated_at?: string | null
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface Prompt {
  id: number
  title: string
  category: string
  text: string
  is_favorite: boolean
  uses: number
  created_at: string
  updated_at?: string | null
}

export interface Tool {
  id: number
  name: string
  category: string
  team: string
  status: 'Ativa' | 'Manutenção' | 'Desativada'
  acquisition_date: string
  created_at: string
  updated_at?: string | null
}

export type SkillLevel = 'Iniciante' | 'Intermediário' | 'Avançado' | 'Especialista'
export interface Skill {
  id: number
  team: string
  skill: string
  category: string
  level: SkillLevel
  reviewer: string
  reviewer_id?: number | null
  updated_date: string
  created_at: string
  updated_at?: string | null
}

export interface Activity {
  id: number
  action: string
  user: string
  user_id?: number | null
  date: string
  created_at: string
}

export interface DashboardStats {
  total_users: number
  active_users: number
  total_tools: number
  active_tools: number
  total_skills: number
  total_prompts: number
  favorite_prompts: number
  total_teams: number
  avg_skill_level: number
  critical_skills: number
  recent_activities: Activity[]
}

// ─────────────── Gestão HEAD de IA ───────────────
export type AssetType = 'Modelo LLM' | 'Agente' | 'Automação' | 'Integração' | 'Dataset' | 'Infraestrutura'
export type AssetStatus = 'Ativo' | 'Em avaliação' | 'Descontinuado'
export type Environment = 'Produção' | 'Homologação' | 'Desenvolvimento'
export type Criticality = 'Baixa' | 'Média' | 'Alta' | 'Crítica'
export type TaskStatus = 'Pendente' | 'Em andamento' | 'Concluída' | 'Bloqueada'
export type Priority = 'Baixa' | 'Média' | 'Alta' | 'Crítica'
export type LicenseStatus = 'Ativa' | 'Em renovação' | 'Expirada' | 'Cancelada'
export type IndicatorCategory = 'Operacional' | 'Financeiro' | 'Adoção' | 'Qualidade' | 'Risco'
export type Trend = 'Subindo' | 'Estável' | 'Caindo'
export type KnowledgeStatus = 'Rascunho' | 'Publicado' | 'Arquivado'

export interface Asset {
  id: number
  name: string
  asset_type: AssetType
  vendor: string
  owner: string
  status: AssetStatus
  environment: Environment
  criticality: Criticality
  monthly_cost: number
  description: string
  acquisition_date: string
  created_at: string
  updated_at?: string | null
}

export interface HeadTask {
  id: number
  title: string
  description: string
  responsible: string
  category: string
  status: TaskStatus
  priority: Priority
  task_date: string
  hours_spent: number
  created_at: string
  updated_at?: string | null
}

export interface License {
  id: number
  software: string
  vendor: string
  plan: string
  seats_total: number
  seats_used: number
  monthly_cost: number
  status: LicenseStatus
  renewal_date: string
  owner: string
  notes: string
  created_at: string
  updated_at?: string | null
}

export interface Indicator {
  id: number
  name: string
  category: IndicatorCategory
  period: string
  unit: string
  target: number
  actual: number
  trend: Trend
  notes: string
  created_at: string
  updated_at?: string | null
}

export interface KnowledgeArticle {
  id: number
  title: string
  category: string
  summary: string
  content: string
  tags: string
  author: string
  status: KnowledgeStatus
  updated_date: string
  created_at: string
  updated_at?: string | null
}

export interface HeadDashboard {
  total_assets: number
  active_assets: number
  assets_monthly_cost: number
  critical_assets: number
  total_tasks: number
  tasks_done: number
  tasks_pending: number
  tasks_in_progress: number
  hours_this_month: number
  total_licenses: number
  licenses_monthly_cost: number
  seats_total: number
  seats_used: number
  seats_utilization: number
  licenses_renewing: number
  total_indicators: number
  kpis_on_target: number
  kpis_off_target: number
  total_articles: number
  published_articles: number
  recent_tasks: HeadTask[]
}

export interface ReportTaskBreakdown {
  status: TaskStatus
  count: number
  hours: number
}

export interface MonthlyReport {
  period: string
  tasks_total: number
  tasks_done: number
  tasks_hours: number
  tasks_by_status: ReportTaskBreakdown[]
  assets_total: number
  assets_monthly_cost: number
  licenses_total: number
  licenses_monthly_cost: number
  total_monthly_cost: number
  indicators: Indicator[]
  kpis_on_target: number
  kpis_off_target: number
}
