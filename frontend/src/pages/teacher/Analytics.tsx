import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import teacherService, { type TeacherCourse } from '../../services/teacher.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import StatCard from '../../components/ui/StatCard'
import { BarChart3, Users, AlertTriangle, TrendingUp } from 'lucide-react'

interface CourseAnalyticsData {
  total_students: number
  average_risk_score: number
  students_at_risk: number
  completion_rate: number
  student_profiles?: Array<{
    student_id: string
    name: string
    risk_score: number
    risk_level: string
  }>
}

export default function TeacherAnalytics() {
  const { user } = useAuth()
  const [courses, setCourses] = useState<TeacherCourse[]>([])
  const [selectedCourse, setSelectedCourse] = useState('')
  const [analytics, setAnalytics] = useState<CourseAnalyticsData | null>(null)
  const [alerts, setAlerts] = useState<{ alerts: unknown[] }>({ alerts: [] })
  const [loading, setLoading] = useState(true)
  const [loadingAnalytics, setLoadingAnalytics] = useState(false)

  useEffect(() => {
    if (!user) return
    Promise.all([
      teacherService.getCourses(user.id).catch(() => []),
      teacherService.getTeacherAlerts().catch(() => ({ alerts: [] })),
    ])
      .then(([c, a]) => { setCourses(c); setAlerts(a) })
      .finally(() => setLoading(false))
  }, [user])

  useEffect(() => {
    if (!selectedCourse) { setAnalytics(null); return }
    setLoadingAnalytics(true)
    teacherService.getCourseAnalytics(selectedCourse)
      .then(setAnalytics)
      .catch(() => toast({ title: 'Error cargando analytics', variant: 'error' }))
      .finally(() => setLoadingAnalytics(false))
  }, [selectedCourse])

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Analytics" description="Análisis del rendimiento de tus cursos y estudiantes" />

      {/* Course selector */}
      <div className="max-w-sm">
        <select
          value={selectedCourse}
          onChange={(e) => setSelectedCourse(e.target.value)}
          className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
        >
          <option value="">Seleccionar curso</option>
          {courses.map((c) => (
            <option key={c.course_id} value={c.course_id}>{c.course_name}</option>
          ))}
        </select>
      </div>

      {/* Alerts */}
      {Array.isArray(alerts?.alerts) && alerts.alerts.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            <h3 className="text-sm font-semibold text-amber-800">Alertas de Gobernanza</h3>
          </div>
          <p className="text-xs text-amber-700">{alerts.alerts.length} alertas activas</p>
        </div>
      )}

      {loadingAnalytics && (
        <div className="flex items-center justify-center py-12"><Spinner size="lg" /></div>
      )}

      {analytics && !loadingAnalytics && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Total Estudiantes" value={analytics.total_students} icon={<Users className="h-5 w-5" />} />
            <StatCard label="Riesgo Promedio" value={analytics.average_risk_score?.toFixed(1) || '—'} icon={<AlertTriangle className="h-5 w-5" />} />
            <StatCard label="Estudiantes en Riesgo" value={analytics.students_at_risk} icon={<BarChart3 className="h-5 w-5" />} />
            <StatCard label="Tasa de Completado" value={`${(analytics.completion_rate * 100 || 0).toFixed(0)}%`} icon={<TrendingUp className="h-5 w-5" />} />
          </div>

          {/* Student Profiles */}
          {analytics.student_profiles && analytics.student_profiles.length > 0 && (
            <div className="rounded-xl border border-gray-100 bg-white overflow-hidden">
              <div className="p-5 pb-3">
                <h2 className="text-sm font-semibold text-gray-900">Perfiles de Riesgo</h2>
              </div>
              <div className="border-t border-gray-50">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-100">
                      <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estudiante</th>
                      <th className="px-5 py-3 text-center text-xs font-medium text-gray-500 uppercase">Score Riesgo</th>
                      <th className="px-5 py-3 text-center text-xs font-medium text-gray-500 uppercase">Nivel</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {analytics.student_profiles.map((p) => (
                      <tr key={p.student_id} className="hover:bg-gray-50/50">
                        <td className="px-5 py-3 text-sm font-medium text-gray-900">{p.name || p.student_id}</td>
                        <td className="px-5 py-3 text-center text-sm text-gray-600">{p.risk_score?.toFixed(1)}</td>
                        <td className="px-5 py-3 text-center">
                          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                            p.risk_level === 'high' || p.risk_level === 'critical' ? 'bg-red-50 text-red-700' :
                            p.risk_level === 'medium' ? 'bg-amber-50 text-amber-700' :
                            'bg-emerald-50 text-emerald-700'
                          }`}>
                            {p.risk_level === 'high' ? 'Alto' : p.risk_level === 'critical' ? 'Crítico' :
                             p.risk_level === 'medium' ? 'Medio' : 'Bajo'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {!selectedCourse && !analytics && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <BarChart3 className="h-12 w-12 text-gray-200 mb-4" />
          <p className="text-sm font-medium text-gray-500">Selecciona un curso para ver los analytics</p>
        </div>
      )}
    </div>
  )
}
