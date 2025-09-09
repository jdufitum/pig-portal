import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api/client'
import { Line, LineChart, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function PigDetail(){
  const { id } = useParams()
  const [tab, setTab] = useState<'profile'|'weights'|'health'|'breeding'|'files'>('profile')
  const [pig, setPig] = useState<any>(null)
  const [edit, setEdit] = useState(false)
  const [form, setForm] = useState<any>({})
  const [weights, setWeights] = useState<any[]>([])
  const [weightDate, setWeightDate] = useState('')
  const [weightKg, setWeightKg] = useState('')
  const [healthList, setHealthList] = useState<any[]>([])
  const [files, setFiles] = useState<any[]>([])

  async function loadPig(){
    const { data } = await api.get(`/pigs/${id}`)
    setPig(data); setForm({ sex: data.sex || '', current_pen: data.current_pen || '' })
  }
  async function loadWeights(){
    const { data } = await api.get(`/pigs/${id}/weights`)
    setWeights(data)
  }
  async function loadHealth(){
    const { data } = await api.get(`/health`, { params: { pig_id: id } })
    setHealthList(data)
  }
  async function loadFiles(){
    const { data } = await api.get(`/files/pigs/${id}`)
    setFiles(data)
  }

  useEffect(()=>{
    loadPig(); loadWeights(); loadHealth(); loadFiles()
  },[id])

  async function addWeight(){
    if (!weightDate || !weightKg) return
    await api.post(`/pigs/${id}/weights`, { date: weightDate, weight_kg: Number(weightKg) })
    setWeightDate(''); setWeightKg('');
    await loadWeights()
  }

  async function uploadFile(e: React.ChangeEvent<HTMLInputElement>){
    const file = e.target.files?.[0]
    if (!file) return
    const form = new FormData()
    form.append('image', file)
    const { data } = await api.post(`/files/pigs/${id}/photo`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
    await fetch(data.upload_url, { method: 'PUT', body: file, headers: { 'Content-Type': file.type || 'application/octet-stream' } })
    await loadFiles()
  }

  return <div className="space-y-4">
    <h2 className="text-xl font-semibold">Pig Detail</h2>
    <div className="flex gap-2 border-b">
      {['profile','weights','health','breeding','files'].map(t => (
        <button key={t} onClick={()=>setTab(t as any)} className={`px-3 py-2 ${tab===t?'border-b-2 border-blue-600':''}`}>{t}</button>
      ))}
    </div>

    {tab==='profile' && pig && (
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 border rounded space-y-2">
          <div className="flex justify-between items-center">
            <div className="text-lg font-semibold">{pig.ear_tag}</div>
            <button className="border rounded px-2 py-1" onClick={()=>setEdit(!edit)}>{edit? 'Cancel':'Edit'}</button>
          </div>
          {!edit ? (
            <>
              <div><span className="text-gray-600 text-sm">Sex:</span> {pig.sex}</div>
              <div><span className="text-gray-600 text-sm">Status:</span> {pig.status}</div>
              <div><span className="text-gray-600 text-sm">Pen:</span> {pig.current_pen}</div>
            </>
          ) : (
            <div className="space-y-2">
              <div>
                <label className="block text-xs text-gray-600">Sex</label>
                <select className="border rounded px-2 py-1" value={form.sex} onChange={e=>setForm((f:any)=>({...f, sex: e.target.value}))}>
                  <option value="">-</option>
                  <option value="M">M</option>
                  <option value="F">F</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-600">Pen</label>
                <input className="border rounded px-2 py-1" value={form.current_pen} onChange={e=>setForm((f:any)=>({...f, current_pen: e.target.value}))} />
              </div>
              <button className="bg-blue-600 text-white px-3 py-1 rounded" onClick={async()=>{ await api.patch(`/pigs/${id}`, { sex: form.sex || undefined, current_pen: form.current_pen || undefined }); setEdit(false); await loadPig() }}>Save</button>
            </div>
          )}
        </div>
      </div>
    )}

    {tab==='weights' && (
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 border rounded">
          <h3 className="font-semibold mb-2">Add Weight</h3>
          <div className="space-y-2">
            <input className="border rounded px-2 py-1 w-full" type="date" value={weightDate} onChange={e=>setWeightDate(e.target.value)} />
            <input className="border rounded px-2 py-1 w-full" type="number" step="0.01" placeholder="kg" value={weightKg} onChange={e=>setWeightKg(e.target.value)} />
            <button onClick={addWeight} className="bg-blue-600 text-white px-3 py-1 rounded">Add</button>
          </div>
        </div>
        <div className="p-4 border rounded">
          <h3 className="font-semibold mb-2">Growth Curve</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={weights.map(w=>({ date: w.date, kg: Number(w.weight_kg) }))}>
              <XAxis dataKey="date" hide />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="kg" stroke="#2563eb" />
            </LineChart>
          </ResponsiveContainer>
          <table className="min-w-full border mt-4">
            <thead><tr className="bg-gray-50"><th className="p-2 border">Date</th><th className="p-2 border">kg</th></tr></thead>
            <tbody>
              {weights.map(w => (<tr key={w.id}><td className="p-2 border">{w.date}</td><td className="p-2 border">{w.weight_kg}</td></tr>))}
            </tbody>
          </table>
        </div>
      </div>
    )}

    {tab==='health' && (
      <div className="p-4 border rounded space-y-2">
        <h3 className="font-semibold">Health Events</h3>
        <ul className="list-disc pl-6">
          {healthList.map(e=> (<li key={e.id}>{e.date}: {e.diagnosis || e.product} {e.dose}</li>))}
        </ul>
      </div>
    )}

    {tab==='breeding' && (
      <div className="p-4 border rounded">Breeding records coming soon</div>
    )}

    {tab==='files' && (
      <div className="p-4 border rounded space-y-3">
        <input type="file" accept="image/*" onChange={uploadFile} />
        <div className="grid grid-cols-4 gap-2">
          {files.map(f => (<a className="block" key={f.id} href={f.url} target="_blank"><img src={f.url} className="w-full h-32 object-cover rounded" /></a>))}
        </div>
      </div>
    )}
  </div>
}

