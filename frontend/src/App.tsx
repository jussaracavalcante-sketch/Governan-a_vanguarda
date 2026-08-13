import { HashRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import { ThemeProvider } from '@/context/ThemeContext'
import { Spinner } from '@/components/ui'
import Layout from '@/components/layout/Layout'
import Login from '@/pages/Login'
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
        {/* Gestão HEAD de IA */}
        <Route path="/" element={<HeadDashboard />} />
        <Route path="/ativos" element={<Assets />} />
        <Route path="/tarefas" element={<Tasks />} />
        <Route path="/indicadores" element={<Indicators />} />
        <Route path="/relatorios" element={<Reports />} />
        <Route path="/licencas" element={<Licenses />} />
        <Route path="/processos" element={<Processes />} />
        <Route path="/conhecimento" element={<Knowledge />} />
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
