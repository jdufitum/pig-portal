import { usePigs } from '../api/hooks'
import { Link } from 'react-router-dom'

export default function Pigs(){
  const { data, isLoading } = usePigs()
  if (isLoading) return <div>Loading...</div>
  return <div>
    <h2 className="text-xl font-semibold mb-4">Pigs</h2>
    <table className="min-w-full border">
      <thead>
        <tr className="bg-gray-50">
          <th className="text-left p-2 border">Ear Tag</th>
          <th className="text-left p-2 border">Sex</th>
          <th className="text-left p-2 border">Status</th>
        </tr>
      </thead>
      <tbody>
        {data?.map((p: any) => (
          <tr key={p.id} className="border-b">
            <td className="p-2 border"><Link className="text-blue-600" to={`/pigs/${p.id}`}>{p.ear_tag}</Link></td>
            <td className="p-2 border">{p.sex}</td>
            <td className="p-2 border">{p.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
}

