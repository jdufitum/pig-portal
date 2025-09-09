import { InputHTMLAttributes, forwardRef } from 'react'
import { cn } from '../../ui-system/cn'

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(function Checkbox(
  { className, ...props },
  ref
) {
  return (
    <input
      ref={ref}
      type="checkbox"
      className={cn(
        'h-[20px] w-[20px] rounded border-surface-border text-primary focus-ring',
        className
      )}
      {...props}
    />
  )
})

