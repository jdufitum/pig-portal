/**
 * Design tokens and small helpers. These mirror Tailwind config values.
 */

export const colors = {
  primary: '#1D4ED8',
  primaryHover: '#1E40AF',
  success: '#15803D',
  warning: '#B45309',
  danger: '#B91C1C',
  text: '#111827',
  textMuted: '#6B7280',
  bg: '#F9FAFB',
  card: '#FFFFFF',
  border: '#E5E7EB',
}

export const radii = {
  card: '0.75rem',
  input: '0.5rem',
}

export const shadows = {
  subtle: '0 1px 2px 0 rgba(0,0,0,0.05)',
  medium:
    '0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)',
}

export const fontSizes = {
  sm: 14,
  base: 16,
  lg: 18,
  xl: 20,
  x2: 24,
  x3: 28,
  x4: 32,
}

export const sizes = {
  controlMd: 44,
  controlLg: 52,
}

export const focusRing = 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-primary';

