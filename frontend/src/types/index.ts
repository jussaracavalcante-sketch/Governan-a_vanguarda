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
