import { ReactNode, useId } from 'react'
import { cn } from '../../ui-system/cn'

type FieldProps = {
  id?: string
  label: string
  required?: boolean
  helpText?: string
  error?: string
  children: (controlProps: { id: string; ariaDescribedBy?: string }) => ReactNode
  className?: string
}

export function FormField({ id, label, required, helpText, error, children, className }: FieldProps) {
  const reactId = useId()
  const fieldId = id ?? `field-${reactId}`
  const helpId = helpText ? `${fieldId}-help` : undefined
  const errorId = error ? `${fieldId}-error` : undefined
  const ariaDescribedBy = [helpId, errorId].filter(Boolean).join(' ') || undefined

  return (
    <div className={cn('space-y-1', className)}>
      <label htmlFor={fieldId} className="block text-sm font-medium text-text">
        {label} {required && <span className="text-danger" aria-hidden>*</span>}
      </label>
      {children({ id: fieldId, ariaDescribedBy })}
      {helpText && !error && (
        <p id={helpId} className="text-sm text-text-muted">
          {helpText}
        </p>
      )}
      {error && (
        <p id={errorId} className="text-sm text-danger">
          {error}
        </p>
      )}
    </div>
  )
}

