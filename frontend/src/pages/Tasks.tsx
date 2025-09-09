import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Tasks(){
  const [items, setItems] = useState<any[]>([])
  const [title, setTitle] = useState('')
  const [due, setDue] = useState('')

  async function load(){
    const { data } = await api.get('/tasks')
    setItems(data)
  }
  useEffect(()=>{ load() }, [])

  async function create(){
    if (!title || !due) return
    await api.post('/tasks', { title, due_date: due })
    setTitle(''); setDue('')
    await load()
  }
  async function toggle(id: string, status: string){
    const next = status === 'open' ? 'done' : 'open'
    await api.patch(`/tasks/${id}`, { status: next })
    await load()
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Tasks</h2>
      <div className="flex gap-2">
        <input placeholder="Title" className="border rounded px-2 py-1" value={title} onChange={e=>setTitle(e.target.value)} />
        <input type="date" className="border rounded px-2 py-1" value={due} onChange={e=>setDue(e.target.value)} />
        <button onClick={create} className="bg-blue-600 text-white px-3 py-1 rounded">Create</button>
      </div>
      <ul className="space-y-2">
        {items.map(t => (
          <li key={t.id} className="border rounded px-3 py-2 flex justify-between items-center">
            <div>
              <div className="font-medium">{t.title}</div>
              <div className="text-xs text-gray-500">Due {t.due_date}</div>
            </div>
            <button className="border px-2 py-1 rounded" onClick={()=>toggle(t.id, t.status)}>{t.status === 'open' ? 'Mark Done' : 'Reopen'}</button>
          </li>
        ))}
      </ul>
    </div>
  )
}

