import { useState, useCallback } from 'react'

interface Toast {
  id: string
  title: string
  description?: string
  variant?: 'default' | 'success' | 'error'
}

let toastListeners: ((toast: Toast) => void)[] = []

export function toast(data: Omit<Toast, 'id'>) {
  const t: Toast = { ...data, id: Date.now().toString() }
  toastListeners.forEach((fn) => fn(t))
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addListener = useCallback(() => {
    const listener = (t: Toast) => {
      setToasts((prev) => [...prev, t])
      setTimeout(() => {
        setToasts((prev) => prev.filter((x) => x.id !== t.id))
      }, 4000)
    }
    toastListeners.push(listener)
    return () => {
      toastListeners = toastListeners.filter((fn) => fn !== listener)
    }
  }, [])

  return { toasts, addListener }
}
