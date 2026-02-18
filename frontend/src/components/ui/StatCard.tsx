import { type ReactNode } from 'react'

interface StatCardProps {
  label: string
  value: string | number
  icon?: ReactNode
  trend?: { value: number; label: string }
  className?: string
}

export default function StatCard({ label, value, icon, trend, className = '' }: StatCardProps) {
  return (
    <div className={`rounded-xl border border-gray-100 bg-white p-5 ${className}`}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-500">{label}</p>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
      <p className="mt-2 text-2xl font-semibold text-gray-900">{value}</p>
      {trend && (
        <p className={`mt-1 text-xs font-medium ${trend.value >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
          {trend.value >= 0 ? '+' : ''}
          {trend.value}% {trend.label}
        </p>
      )}
    </div>
  )
}
