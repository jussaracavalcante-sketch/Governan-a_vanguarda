import { HashRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import { ThemeProvider } from '@/context/ThemeContext'
import { Spinner } from '@/components/ui'
import Layout from '@/components/layout/Layout'
import Login from '@/pages/Login'
import Dashboard from '@/pages/Dashboard'
import Prompts from '@/pages/Prompts'
import Tools from '@/pages/Tools'
import Skills from '@/pages/Skills'
import Access from '@/pages/Access'
import Admin from '@/pages/Admin'
import NotFound from '@/pages/NotFound'
import HeadDashboard from '@/pages/head/HeadDashboard'
import Assets from '@/pages/head/Assets'
import Tasks from '@/pages/head/Tasks'
import Licenses from '@/pages/head/Licenses'
import Indicators from '@/pages/head/Indicators'
import Reports from '@/pages/head/Reports'
import Processes from '@/pages/head/Processes'
import Knowledge from '@/pages/head/Knowledge'

function Protected({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  if (!user) return <Navigate to="/login" replace />
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <Protected>
            <Layout />
          </Protected>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/prompts" element={<Prompts />} />
        <Route path="/ferramentas" element={<Tools />} />
        <Route path="/skills" element={<Skills />} />
        <Route path="/acessos" element={<Access />} />
        <Route path="/admin" element={<Admin />} />

        {/* App · Gestão HEAD de IA */}
        <Route path="/head" element={<HeadDashboard />} />
        <Route path="/head/ativos" element={<Assets />} />
        <Route path="/head/tarefas" element={<Tasks />} />
        <Route path="/head/indicadores" element={<Indicators />} />
        <Route path="/head/relatorios" element={<Reports />} />
        <Route path="/head/licencas" element={<Licenses />} />
        <Route path="/head/processos" element={<Processes />} />
        <Route path="/head/conhecimento" element={<Knowledge />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <HashRouter>
          <AppRoutes />
        </HashRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}
