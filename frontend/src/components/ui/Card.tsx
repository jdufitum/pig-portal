import { ReactNode } from 'react'

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`bg-surface rounded-card shadow-subtle border border-surface-border ${className}`}>{children}</div>
}

export function CardHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="px-4 py-3 border-b border-surface-border">
      <h3 className="text-lg font-semibold text-text">{title}</h3>
      {subtitle && <p className="text-sm text-text-muted">{subtitle}</p>}
    </div>
  )
}

export function CardBody({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`p-4 ${className}`}>{children}</div>
}

