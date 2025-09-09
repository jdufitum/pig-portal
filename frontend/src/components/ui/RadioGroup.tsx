import { InputHTMLAttributes, ReactNode } from 'react'

type RadioOption = {
  label: string
  value: string
  helpText?: string
}

type RadioGroupProps = {
  name: string
  value?: string
  onChange?: (value: string) => void
  options: RadioOption[]
  disabled?: boolean
}

export function RadioGroup({ name, value, onChange, options, disabled }: RadioGroupProps) {
  return (
    <div role="radiogroup" className="space-y-2">
      {options.map(opt => (
        <label key={opt.value} className="flex items-center gap-2">
          <input
            type="radio"
            name={name}
            value={opt.value}
            checked={value === opt.value}
            onChange={(e) => onChange?.(e.target.value)}
            disabled={disabled}
            className="h-[20px] w-[20px] text-primary focus-ring"
          />
          <span className="text-text">{opt.label}</span>
          {opt.helpText && <span className="text-text-muted text-sm">{opt.helpText}</span>}
        </label>
      ))}
    </div>
  )
}

