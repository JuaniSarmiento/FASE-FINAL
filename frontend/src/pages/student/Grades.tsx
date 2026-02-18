import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import studentService, { type Grade, type GradesSummary } from '../../services/student.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import StatCard from '../../components/ui/StatCard'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import { GraduationCap, TrendingUp, Award, CheckCircle2, XCircle } from 'lucide-react'

export default function StudentGrades() {
  const { user } = useAuth()
  const [grades, setGrades] = useState<Grade[]>([])
  const [summary, setSummary] = useState<GradesSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    Promise.all([
      studentService.getGrades(user.id).catch(() => []),
      studentService.getGradesSummary(user.id).catch(() => null),
    ])
      .then(([g, s]) => { setGrades(g); setSummary(s) })
      .finally(() => setLoading(false))
  }, [user])

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Calificaciones" description="Resumen de tus notas y evaluaciones" />

      {/* Stats */}
      {summary && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Promedio General"
            value={summary.average_grade ? `${summary.average_grade.toFixed(1)}/10` : '—'}
            icon={<TrendingUp className="h-5 w-5" />}
          />
          <StatCard
            label="Actividades Evaluadas"
            value={`${summary.graded_activities}/${summary.total_activities}`}
            icon={<GraduationCap className="h-5 w-5" />}
          />
          <StatCard
            label="Mejor Nota"
            value={summary.highest_grade ? `${summary.highest_grade.toFixed(1)}/10` : '—'}
            icon={<Award className="h-5 w-5" />}
          />
          <StatCard
            label="Nota más Baja"
            value={summary.lowest_grade ? `${summary.lowest_grade.toFixed(1)}/10` : '—'}
            icon={<TrendingUp className="h-5 w-5" />}
          />
        </div>
      )}

      {/* Grades list */}
      {grades.length === 0 ? (
        <EmptyState
          icon={<GraduationCap className="h-12 w-12" />}
          title="No hay calificaciones aún"
          description="Las calificaciones aparecerán aquí cuando completes actividades."
        />
      ) : (
        <div className="rounded-xl border border-gray-100 bg-white overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="px-6 py-3.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actividad</th>
                <th className="px-6 py-3.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Curso</th>
                <th className="px-6 py-3.5 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Nota</th>
                <th className="px-6 py-3.5 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Feedback</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {grades.map((grade) => (
                <tr key={grade.grade_id} className="hover:bg-gray-50/50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{grade.activity_title}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{grade.course_name || '—'}</td>
                  <td className="px-6 py-4 text-center">
                    <span className={`text-sm font-semibold ${grade.grade >= 6 ? 'text-emerald-600' : 'text-red-500'}`}>
                      {grade.grade.toFixed(1)}/{grade.max_grade}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    {grade.passed ? (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-600">
                        <CheckCircle2 className="h-3.5 w-3.5" /> Aprobado
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-red-500">
                        <XCircle className="h-3.5 w-3.5" /> Desaprobado
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                    {grade.teacher_feedback || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
