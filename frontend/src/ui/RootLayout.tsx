import { NavLink, Outlet } from 'react-router-dom'
import { useRole } from '../api/client'

export default function RootLayout() {
  const role = useRole()
  return (
    <div className="h-full flex">
      <aside className="w-64 bg-gray-900 text-white p-4 space-y-2">
        <div className="text-xl font-bold mb-4">Pig Farm</div>
        <nav className="flex flex-col gap-1">
          <NavLink className={({isActive}) => `px-3 py-2 rounded ${isActive? 'bg-gray-800':'hover:bg-gray-800'}`} to="/">Dashboard</NavLink>
          <NavLink className={({isActive}) => `px-3 py-2 rounded ${isActive? 'bg-gray-800':'hover:bg-gray-800'}`} to="/pigs">Pigs</NavLink>
          <NavLink className={({isActive}) => `px-3 py-2 rounded ${isActive? 'bg-gray-800':'hover:bg-gray-800'}`} to="/breeding">Breeding</NavLink>
          <NavLink className={({isActive}) => `px-3 py-2 rounded ${isActive? 'bg-gray-800':'hover:bg-gray-800'}`} to="/tasks">Tasks</NavLink>
          <NavLink className={({isActive}) => `px-3 py-2 rounded ${isActive? 'bg-gray-800':'hover:bg-gray-800'}`} to="/litters">Litters</NavLink>
          <NavLink className={({isActive}) => `px-3 py-2 rounded ${isActive? 'bg-gray-800':'hover:bg-gray-800'}`} to="/imports">Imports</NavLink>
          <NavLink className={({isActive}) => `px-3 py-2 rounded ${isActive? 'bg-gray-800':'hover:bg-gray-800'}`} to="/reports">Reports</NavLink>
          <NavLink className={({isActive}) => `px-3 py-2 rounded ${isActive? 'bg-gray-800':'hover:bg-gray-800'}`} to="/settings">Settings</NavLink>
        </nav>
      </aside>
      <main className="flex-1 flex flex-col">
        <header className="h-12 border-b flex items-center justify-between px-4">
          <div className="font-semibold">Dashboard</div>
          <div className="text-sm text-gray-400">{role ? `Role: ${role}` : 'Signed in'}</div>
        </header>
        <div className="p-4 flex-1 overflow-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

