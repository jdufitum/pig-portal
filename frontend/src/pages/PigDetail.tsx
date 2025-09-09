import { useParams } from 'react-router-dom'

export default function PigDetail(){
  const { id } = useParams()
  return <div>
    <h2 className="text-xl font-semibold mb-4">Pig Detail</h2>
    <div className="p-4 border rounded">Pig ID: {id}</div>
  </div>
}

