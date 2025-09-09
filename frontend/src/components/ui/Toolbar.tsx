import { ReactNode } from 'react'

type Props = {
  title?: string
  subtitle?: string
  left?: ReactNode
  right?: ReactNode
  sticky?: boolean
}

export function Toolbar({ title, subtitle, left, right, sticky }: Props) {
  return (
    <div className={`${sticky ? 'sticky top-0 z-10 bg-surface-muted/80 backdrop-blur supports-[backdrop-filter]:bg-surface-muted/60' : ''}`}>
      <div className="flex items-center justify-between gap-3 py-3">
        <div className="min-w-0">
          {title && <h1 className="text-xl font-semibold text-text truncate">{title}</h1>}
          {subtitle && <p className="text-sm text-text-muted truncate">{subtitle}</p>}
          {left}
        </div>
        <div className="flex items-center gap-2">{right}</div>
      </div>
    </div>
  )
}

