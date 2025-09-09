import { ReactNode, useEffect } from 'react'
import { Button } from './Button'

type Props = {
  open: boolean
  title: string
  description?: string
  confirmLabel: string
  cancelLabel?: string
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({ open, title, description, confirmLabel, cancelLabel = 'Cancel', onConfirm, onCancel }: Props) {
  useEffect(() => {
    function onKey(e: KeyboardEvent){ if(e.key === 'Escape') onCancel() }
    if(open) document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, onCancel])

  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" aria-modal="true" role="dialog">
      <div className="absolute inset-0 bg-black/40" onClick={onCancel} />
      <div className="relative bg-surface rounded-card shadow-medium border border-surface-border w-full max-w-sm p-4" role="document">
        <h2 className="text-lg font-semibold text-text">{title}</h2>
        {description && <p className="text-sm text-text-muted mt-1">{description}</p>}
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="secondary" onClick={onCancel}>{cancelLabel}</Button>
          <Button onClick={onConfirm}>{confirmLabel}</Button>
        </div>
      </div>
    </div>
  )
}

