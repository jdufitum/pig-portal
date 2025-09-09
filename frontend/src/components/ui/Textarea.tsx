import { TextareaHTMLAttributes, forwardRef } from 'react'
import { cn } from '../../ui-system/cn'

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {}

const base = 'block w-full rounded-input border border-surface-border bg-white text-text placeholder:text-text-muted focus-ring disabled:opacity-60 disabled:cursor-not-allowed'

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { className, rows = 4, ...props },
  ref
) {
  return (
    <textarea
      ref={ref}
      rows={rows}
      className={cn(base, 'px-3 py-2 leading-[1.2] min-h-[96px]')}
      {...props}
    />
  )
})

