import { SwitchHTMLAttributes } from 'react'

type ToggleProps = {
  checked: boolean
  onChange: (checked: boolean) => void
  onLabel?: string
  offLabel?: string
  disabled?: boolean
}

export function Toggle({ checked, onChange, onLabel = 'On', offLabel = 'Off', disabled }: ToggleProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      disabled={disabled}
      className={`hit-target inline-flex items-center gap-2 rounded-card px-3 h-[44px] focus-ring ${
        checked ? 'bg-primary text-white' : 'bg-surface-muted text-text'
      } disabled:opacity-60 disabled:cursor-not-allowed`}
    >
      <span
        className={`inline-block h-5 w-5 rounded-full transition-colors ${
          checked ? 'bg-white' : 'bg-surface-border'
        }`}
        aria-hidden
      />
      <span className="text-sm">{checked ? onLabel : offLabel}</span>
    </button>
  )
}

