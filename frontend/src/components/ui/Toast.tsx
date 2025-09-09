import { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react'

type ToastType = 'success' | 'error' | 'info'
type ToastItem = { id: number; type: ToastType; message: string; duration: number }

type ToastContextType = {
  show: (type: ToastType, message: string, duration?: number) => void
}

const ToastContext = createContext<ToastContextType | null>(null)

export function useToast(){
  const ctx = useContext(ToastContext)
  if(!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

export function ToastProvider({ children }: { children: React.ReactNode }){
  const [items, setItems] = useState<ToastItem[]>([])
  const idRef = useRef(1)

  function show(type: ToastType, message: string, duration = 4000){
    const id = idRef.current++
    setItems(items => [...items, { id, type, message, duration }])
    window.setTimeout(() => {
      setItems(items => items.filter(i => i.id !== id))
    }, duration)
  }

  const value = useMemo(() => ({ show }), [])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed top-3 right-3 z-50 space-y-2" aria-live="polite" aria-atomic="true">
        {items.map(i => (
          <div key={i.id} className={`rounded-card shadow-medium border px-3 py-2 text-sm ${
            i.type === 'success' ? 'bg-white border-success text-text' :
            i.type === 'error' ? 'bg-white border-danger text-text' :
            'bg-white border-surface-border text-text'
          }`}>
            {i.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

