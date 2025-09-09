import { InputHTMLAttributes, forwardRef } from 'react'
import { cn } from '../../ui-system/cn'

export interface DateInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {}

const base = 'block w-full rounded-input border border-surface-border bg-white text-text focus-ring disabled:opacity-60 disabled:cursor-not-allowed'

export const DateInput = forwardRef<HTMLInputElement, DateInputProps>(function DateInput(
  { className, ...props },
  ref
) {
  return (
    <input ref={ref} type="date" className={cn(base, 'px-3 h-[48px] leading-[1.2]')} {...props} />
  )
})

