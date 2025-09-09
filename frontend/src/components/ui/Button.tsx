import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cn } from '../../ui-system/cn'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'
type Size = 'md' | 'lg'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  isLoading?: boolean
}

const base = 'inline-flex hit-target items-center justify-center rounded-card font-medium focus-ring select-none disabled:opacity-60 disabled:cursor-not-allowed'

const sizes: Record<Size, string> = {
  md: 'h-11 px-4 text-base', // 44px
  lg: 'h-13 px-5 text-lg',   // 52px (h-13 via arbitrary h-[52px])
}

const sizeFix: Record<Size, string> = {
  md: 'h-[44px] min-w-[44px]',
  lg: 'h-[52px] min-w-[52px]',
}

const variants: Record<Variant, string> = {
  primary: 'bg-primary text-white hover:bg-primary-hover shadow-medium',
  secondary: 'bg-white text-text border border-surface-border hover:bg-surface-muted shadow-subtle',
  ghost: 'bg-transparent text-text hover:bg-surface-muted',
  danger: 'bg-danger text-white hover:brightness-95 shadow-medium',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant = 'primary', size = 'md', isLoading, children, disabled, ...props },
  ref
) {
  const isDisabled = disabled || isLoading
  return (
    <button
      ref={ref}
      className={cn(base, sizes[size], sizeFix[size], variants[variant], className)}
      disabled={isDisabled}
      {...props}
    >
      {isLoading && (
        <span className="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/60 border-t-white" aria-hidden />
      )}
      <span>{children}</span>
    </button>
  )
})

