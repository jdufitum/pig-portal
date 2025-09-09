/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1D4ED8', // blue-700
          hover: '#1E40AF',   // blue-800
        },
        success: '#15803D',
        warning: '#B45309',
        danger: '#B91C1C',
        text: {
          DEFAULT: '#111827', // gray-900
          muted: '#6B7280',   // gray-500
        },
        surface: {
          DEFAULT: '#FFFFFF', // card
          muted: '#F9FAFB',   // bg
          border: '#E5E7EB',  // borders
        }
      },
      fontSize: {
        sm: ['0.875rem', { lineHeight: '1.25rem' }], // 14px
        base: ['1rem', { lineHeight: '1.5rem' }],     // 16px
        lg: ['1.125rem', { lineHeight: '1.75rem' }], // 18px
        xl: ['1.25rem', { lineHeight: '1.75rem' }],  // 20px
        '2xl': ['1.5rem', { lineHeight: '2rem' }],   // 24px
        '3xl': ['1.75rem', { lineHeight: '2.25rem' }], // 28px
        '4xl': ['2rem', { lineHeight: '2.5rem' }],   // 32px
      },
      borderRadius: {
        card: '0.75rem', // rounded-xl for cards/buttons
        input: '0.5rem', // rounded-lg for inputs
      },
      boxShadow: {
        subtle: '0 1px 2px 0 rgba(0,0,0,0.05)', // alias for shadow-sm
        medium: '0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)', // alias for shadow
      }
    },
  },
  plugins: [],
}

