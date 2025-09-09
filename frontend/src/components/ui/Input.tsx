import { InputHTMLAttributes, forwardRef } from 'react'
import { cn } from '../../ui-system/cn'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

const base = 'block w-full rounded-input border border-surface-border bg-white text-text placeholder:text-text-muted focus-ring disabled:opacity-60 disabled:cursor-not-allowed'

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { className, ...props },
  ref
) {
  return (
    <input
      ref={ref}
      className={cn(base, 'px-3 h-[48px] leading-[1.2]')}
      {...props}
    />
  )
})

