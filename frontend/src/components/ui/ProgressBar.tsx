type Props = {
  value: number // 0..100
  label?: string
}

export function ProgressBar({ value, label }: Props) {
  const v = Math.max(0, Math.min(100, value))
  return (
    <div className="w-full" aria-label={label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={v} role="progressbar">
      <div className="h-3 bg-surface-border rounded-input overflow-hidden">
        <div className="h-full bg-primary" style={{ width: `${v}%` }} />
      </div>
      {label && <div className="text-sm text-text-muted mt-1">{label}</div>}
    </div>
  )
}

