import { Button } from './Button'

type Props = {
  icon?: React.ReactNode
  message: string
  actionLabel?: string
  onAction?: () => void
}

export function EmptyState({ icon, message, actionLabel, onAction }: Props) {
  return (
    <div className="text-center p-8 border border-dashed border-surface-border rounded-card bg-surface">
      <div className="mx-auto mb-2 h-12 w-12 text-text-muted flex items-center justify-center">
        {icon ?? <span aria-hidden>ⓘ</span>}
      </div>
      <p className="text-text mb-4">{message}</p>
      {actionLabel && (
        <Button onClick={onAction}>{actionLabel}</Button>
      )}
    </div>
  )
}

