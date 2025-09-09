import { SelectHTMLAttributes, forwardRef } from 'react'
import { cn } from '../../ui-system/cn'

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {}

const base = 'block w-full rounded-input border border-surface-border bg-white text-text focus-ring disabled:opacity-60 disabled:cursor-not-allowed'

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { className, children, ...props },
  ref
) {
  return (
    <select ref={ref} className={cn(base, 'px-3 h-[48px] leading-[1.2]')} {...props}>
      {children}
    </select>
  )
})

