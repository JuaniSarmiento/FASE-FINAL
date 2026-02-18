import { useEffect } from 'react'
import { useToast } from '../../hooks/useToast'
import { X } from 'lucide-react'

export function Toaster() {
  const { toasts, addListener } = useToast()

  useEffect(() => {
    return addListener()
  }, [addListener])

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`flex items-start gap-3 rounded-lg border px-4 py-3 shadow-lg transition-all animate-in slide-in-from-bottom-2 ${
            t.variant === 'error'
              ? 'border-red-200 bg-red-50 text-red-900'
              : t.variant === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-900'
              : 'border-gray-200 bg-white text-gray-900'
          }`}
        >
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium">{t.title}</p>
            {t.description && <p className="mt-0.5 text-xs opacity-80">{t.description}</p>}
          </div>
          <button className="shrink-0 opacity-50 hover:opacity-100">
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  )
}
