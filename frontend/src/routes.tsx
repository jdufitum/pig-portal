import { createBrowserRouter, Navigate } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useAuthStore } from './api/client'
import Dashboard from './pages/Dashboard'
import Pigs from './pages/Pigs'
import PigDetail from './pages/PigDetail'
import Breeding from './pages/Breeding'
import Tasks from './pages/Tasks'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import Login from './pages/Login'
import RootLayout from './ui/RootLayout'
import DevUI from './pages/DevUI'

function Protected({ children }: { children: ReactNode }) {
  const token = useAuthStore((s: any) => s.accessToken)
  if (!token) return <Navigate to="/login" replace />
  return children
}

export const router = createBrowserRouter([
  { path: '/login', element: <Login /> },
  { path: '/dev/ui', element: <DevUI /> },
  {
    path: '/', element: <Protected><RootLayout /></Protected>, children: [
      { index: true, element: <Dashboard /> },
      { path: 'pigs', element: <Pigs /> },
      { path: 'pigs/:id', element: <PigDetail /> },
      { path: 'breeding', element: <Breeding /> },
      { path: 'tasks', element: <Tasks /> },
      { path: 'reports', element: <Reports /> },
      { path: 'settings', element: <Settings /> },
    ]
  }
])

