import type { ReactNode } from 'react'

export function Table({ children }: { children: ReactNode }){
  return <table className="min-w-full border rounded overflow-hidden">{children}</table>
}

export function Th({ children }: { children: ReactNode }){
  return <th className="text-left p-2 border bg-gray-50 text-gray-700 text-sm">{children}</th>
}

export function Td({ children }: { children: ReactNode }){
  return <td className="p-2 border align-top">{children}</td>
}

