import { hasAnyRole } from '../api/client'

export default function Settings(){
  const canView = hasAnyRole('owner')
  if (!canView) return <div className="text-red-600">Forbidden</div>
  return <div className="p-4 border rounded">Settings page placeholder</div>
}

