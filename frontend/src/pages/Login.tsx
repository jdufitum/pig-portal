import { useState } from 'react'
import { useLogin } from '../api/hooks'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../api/client'

export default function Login(){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { mutateAsync, isPending, error } = useLogin()
  const token = useAuthStore((s: any) => s.accessToken)
  const nav = useNavigate()

  if (token) return <Navigate to="/" replace />

  async function onSubmit(e: React.FormEvent){
    e.preventDefault()
    try {
      await mutateAsync({ email, password })
      nav('/')
    } catch {}
  }

  return (
    <div className="h-full grid place-items-center bg-gray-50">
      <form onSubmit={onSubmit} className="w-80 bg-white shadow p-6 rounded space-y-4">
        <h1 className="text-xl font-semibold">Sign in</h1>
        <div className="space-y-1">
          <label className="text-sm text-gray-600">Email</label>
          <input className="w-full border rounded px-3 py-2" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
        </div>
        <div className="space-y-1">
          <label className="text-sm text-gray-600">Password</label>
          <input className="w-full border rounded px-3 py-2" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
        </div>
        {error && <div className="text-red-600 text-sm">Login failed</div>}
        <button disabled={isPending} className="w-full bg-blue-600 text-white py-2 rounded">{isPending? 'Signing in...':'Sign in'}</button>
      </form>
    </div>
  )
}

