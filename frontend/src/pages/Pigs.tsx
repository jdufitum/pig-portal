import { useState } from 'react'
import { api } from '../api/client'
import { Link } from 'react-router-dom'
import { Table, Th, Td } from '../components/Table'

export default function Pigs(){
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [sex, setSex] = useState('')
  const [pen, setPen] = useState('')
  const [offset, setOffset] = useState(0)
  const [limit] = useState(20)

  async function fetchData(newOffset = offset){
    setLoading(true)
    const resp = await api.get('/pigs', { params: {
      search: search || undefined,
      status: status || undefined,
      sex: sex || undefined,
      pen: pen || undefined,
      limit, offset: newOffset
    }})
    setItems(resp.data)
    const header = resp.headers['x-total-count']
    if (header) setTotal(Number(header))
    setOffset(newOffset)
    setLoading(false)
  }

  function exportCsv(){
    const url = new URL((api.defaults.baseURL || '') + '/pigs/export', window.location.origin)
    if (search) url.searchParams.set('search', search)
    if (status) url.searchParams.set('status', status)
    if (sex) url.searchParams.set('sex', sex)
    if (pen) url.searchParams.set('pen', pen)
    window.location.href = url.toString()
  }

  const [showCreate, setShowCreate] = useState(false)
  const [newEarTag, setNewEarTag] = useState('')
  const [newSex, setNewSex] = useState('')
  const [newPen, setNewPen] = useState('')

  async function createPig(){
    await api.post('/pigs', { ear_tag: newEarTag, sex: newSex || undefined, current_pen: newPen || undefined })
    setShowCreate(false); setNewEarTag(''); setNewSex(''); setNewPen('')
    fetchData(offset)
  }

  return <div className="space-y-4">
    <h2 className="text-xl font-semibold">Pigs</h2>
    <div className="flex flex-wrap gap-2 items-end">
      <div>
        <label className="block text-xs text-gray-600">Search</label>
        <input className="border rounded px-2 py-1" value={search} onChange={e=>setSearch(e.target.value)} />
      </div>
      <div>
        <label className="block text-xs text-gray-600">Status</label>
        <select className="border rounded px-2 py-1" value={status} onChange={e=>setStatus(e.target.value)}>
          <option value="">All</option>
          <option value="active">Active</option>
          <option value="sold">Sold</option>
          <option value="dead">Dead</option>
        </select>
      </div>
      <div>
        <label className="block text-xs text-gray-600">Sex</label>
        <select className="border rounded px-2 py-1" value={sex} onChange={e=>setSex(e.target.value)}>
          <option value="">All</option>
          <option value="M">M</option>
          <option value="F">F</option>
        </select>
      </div>
      <div>
        <label className="block text-xs text-gray-600">Pen</label>
        <input className="border rounded px-2 py-1" value={pen} onChange={e=>setPen(e.target.value)} />
      </div>
      <button onClick={()=>fetchData(0)} className="bg-blue-600 text-white px-3 py-1 rounded">Filter</button>
      <button onClick={()=>setShowCreate(true)} className="border px-3 py-1 rounded">Create</button>
      <button onClick={exportCsv} className="border px-3 py-1 rounded">Export CSV</button>
    </div>
    <div className="overflow-auto">
      <Table>
        <thead>
          <tr>
            <Th>Ear Tag</Th>
            <Th>Sex</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody>
          {items.map(p => (
            <tr key={p.id} className="hover:bg-gray-50">
              <Td><Link className="text-blue-600" to={`/pigs/${p.id}`}>{p.ear_tag}</Link></Td>
              <Td>{p.sex}</Td>
              <Td>{p.status}</Td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
    <div className="flex items-center gap-3">
      <button className="border rounded px-2 py-1" onClick={()=>fetchData(Math.max(0, offset - limit))} disabled={offset===0}>Prev</button>
      <div className="text-sm">{offset + 1}-{Math.min(offset + items.length, total)} of {total}</div>
      <button className="border rounded px-2 py-1" onClick={()=>fetchData(offset + limit)} disabled={offset + limit >= total}>Next</button>
    </div>
    {loading && <div>Loading...</div>}

    {showCreate && (
      <div className="fixed inset-0 bg-black/40 grid place-items-center">
        <div className="bg-white rounded shadow w-[420px] p-4 space-y-3">
          <div className="text-lg font-semibold">Create Pig</div>
          <div>
            <label className="block text-xs text-gray-600">Ear tag</label>
            <input className="border rounded w-full px-2 py-1" value={newEarTag} onChange={e=>setNewEarTag(e.target.value)} />
          </div>
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="block text-xs text-gray-600">Sex</label>
              <select className="border rounded w-full px-2 py-1" value={newSex} onChange={e=>setNewSex(e.target.value)}>
                <option value="">-</option>
                <option value="M">M</option>
                <option value="F">F</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-xs text-gray-600">Pen</label>
              <input className="border rounded w-full px-2 py-1" value={newPen} onChange={e=>setNewPen(e.target.value)} />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button className="px-3 py-1" onClick={()=>setShowCreate(false)}>Cancel</button>
            <button className="bg-blue-600 text-white px-3 py-1 rounded" onClick={createPig} disabled={!newEarTag}>Create</button>
          </div>
        </div>
      </div>
    )}
  </div>
}

