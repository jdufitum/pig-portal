import { Card, CardBody } from './Card'

type Props = {
  label: string
  value: string | number
  help?: string
}

export function KpiCard({ label, value, help }: Props) {
  return (
    <Card className="p-4">
      <div className="text-sm text-text-muted">{label}</div>
      <div className="text-3xl font-bold text-text">{value}</div>
      {help && <div className="text-sm text-text-muted mt-1">{help}</div>}
    </Card>
  )
}

