import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import teacherService, { type ActivityStudentProgress } from '../../services/teacher.service'
import studentService, { type Activity, type Exercise } from '../../services/student.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import StudentAIAnalytics from '../../components/teacher/StudentAIAnalytics'
import { ArrowLeft, Users, BarChart3, CheckCircle2, Clock, AlertCircle, Bot, FileText, Code2, BookOpen } from 'lucide-react'

export default function ModuleActivityAnalytics() {
  const { moduleId, activityId } = useParams<{ moduleId: string; activityId: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [activity, setActivity] = useState<Activity | null>(null)
  const [progress, setProgress] = useState<ActivityStudentProgress[]>([])
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [activeTab, setActiveTab] = useState<'analytics' | 'content'>('analytics')

  const [selectedStudent, setSelectedStudent] = useState<ActivityStudentProgress | null>(null)
  const [showAIAnalytics, setShowAIAnalytics] = useState(false)
  const [aiAnalyticsStudent, setAIAnalyticsStudent] = useState<{ id: string, name: string } | null>(null)

  const loadData = async () => {
    if (!activityId || !user) return
    try {
      const [activityData, progressData, exercisesData] = await Promise.all([
        teacherService.getActivity(activityId),
        teacherService.getActivityStudentProgress(activityId),
        teacherService.getExercises(activityId)
      ])
      setActivity(activityData)
      setProgress(progressData)
      setExercises(exercisesData)
    } catch {
      toast({ title: 'Error cargando datos', variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [activityId, user])

  const avgProgress = progress.length > 0
    ? progress.reduce((sum, p) => sum + p.progress_percentage, 0) / progress.length
    : 0

  const avgScore = progress.length > 0
    ? progress.reduce((sum, p) => sum + p.avg_score, 0) / progress.length
    : 0

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(`/teacher/modules/${moduleId}`)}
              className="rounded-lg p-2 hover:bg-gray-100 transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-500" />
            </button>
            <span>{activity?.title || 'Actividad'}</span>
          </div>
        }
        description={activeTab === 'analytics' ? "Resultados y progreso por estudiante" : "Contenido y ejercicios de la actividad"}
      />

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('analytics')}
            className={`
              whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2
              ${activeTab === 'analytics'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
            `}
          >
            <BarChart3 className="h-4 w-4" />
            Analytics
          </button>
          <button
            onClick={() => setActiveTab('content')}
            className={`
              whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2
              ${activeTab === 'content'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
            `}
          >
            <BookOpen className="h-4 w-4" />
            Contenido ({exercises.length})
          </button>
        </nav>
      </div>

      {activeTab === 'analytics' ? (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
                  <Users className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Estudiantes</p>
                  <p className="text-2xl font-semibold text-gray-900">{progress.length}</p>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-50">
                  <BarChart3 className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Progreso Promedio</p>
                  <p className="text-2xl font-semibold text-gray-900">{avgProgress.toFixed(0)}%</p>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-50">
                  <CheckCircle2 className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Nota Promedio</p>
                  <p className="text-2xl font-semibold text-gray-900">{avgScore.toFixed(1)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Student List */}
          <div className="rounded-xl border border-gray-200 bg-white">
            <div className="border-b border-gray-100 p-5">
              <h2 className="text-lg font-semibold text-gray-900">Resultados por Estudiante</h2>
            </div>

            {progress.length === 0 ? (
              <div className="p-6">
                <EmptyState
                  icon={<Users className="h-12 w-12" />}
                  title="Sin datos"
                  description="Ningún estudiante ha trabajado en esta actividad aún"
                />
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {progress.map((student) => {
                  const statusIcon = student.progress_percentage === 100
                    ? <CheckCircle2 className="h-5 w-5 text-green-500" />
                    : student.progress_percentage > 0
                      ? <Clock className="h-5 w-5 text-yellow-500" />
                      : <AlertCircle className="h-5 w-5 text-gray-400" />

                  const statusText = student.progress_percentage === 100
                    ? 'Completado'
                    : student.progress_percentage > 0
                      ? 'En progreso'
                      : 'No iniciado'

                  return (
                    <div
                      key={student.student_id}
                      className="p-5 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 flex-1">
                          {statusIcon}
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">{student.email}</p>
                            <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                              <span>{statusText}</span>
                              <span>•</span>
                              <span>{student.submitted_exercises} / {student.total_exercises} ejercicios</span>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-6">
                          {/* Progress bar */}
                          <div className="hidden sm:flex items-center gap-3 w-32">
                            <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-blue-500 transition-all duration-300"
                                style={{ width: `${student.progress_percentage}%` }}
                              />
                            </div>
                            <span className="text-xs font-medium text-gray-600 w-10 text-right">
                              {student.progress_percentage.toFixed(0)}%
                            </span>
                          </div>

                          {/* Score */}
                          <div className="text-right min-w-[60px]">
                            <p className="text-lg font-semibold text-gray-900">{student.avg_score.toFixed(1)}</p>
                            <p className="text-xs text-gray-500">Nota</p>
                          </div>

                          {/* AI Analytics Button */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              setAIAnalyticsStudent({ id: student.student_id, name: student.email })
                              setShowAIAnalytics(true)
                            }}
                            className="rounded-lg p-2 hover:bg-blue-50 border border-blue-200 transition-colors group"
                            title="Ver análisis de IA"
                          >
                            <Bot className="h-4 w-4 text-blue-600 group-hover:text-blue-700" />
                          </button>
                        </div>
                      </div>

                      {/* Mobile progress */}
                      <div className="sm:hidden mt-3 flex items-center gap-2">
                        <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500"
                            style={{ width: `${student.progress_percentage}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-gray-600">
                          {student.progress_percentage.toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {exercises.length === 0 ? (
            <EmptyState
              icon={<FileText className="h-12 w-12" />}
              title="Sin Contenido"
              description="No se encontraron ejercicios en esta actividad"
            />
          ) : (
            <div className="space-y-4">
              {exercises.map((ex, idx) => (
                <div key={ex.id || idx} className="rounded-xl border border-gray-200 bg-white p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-600">
                          {idx + 1}
                        </span>
                        {ex.title}
                      </h3>
                      <div className="mt-2 text-sm text-gray-600">{ex.problem_statement || ex.description}</div>
                    </div>
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium uppercase ${ex.difficulty === 'Easy' || ex.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                        ex.difficulty === 'Hard' || ex.difficulty === 'hard' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                      }`}>
                      {ex.difficulty}
                    </span>
                  </div>

                  <div className="mt-4 bg-gray-50 rounded-lg p-4 font-mono text-sm border border-gray-200 overflow-x-auto">
                    <pre className="text-gray-800">{ex.starter_code}</pre>
                  </div>

                  <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
                    <Code2 className="h-3 w-3" />
                    <span>Lenguaje: {ex.language}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* AI Analytics Modal */}
      {showAIAnalytics && aiAnalyticsStudent && activityId && (
        <StudentAIAnalytics
          studentId={aiAnalyticsStudent.id}
          studentName={aiAnalyticsStudent.name}
          activityId={activityId}
          onClose={() => {
            setShowAIAnalytics(false)
            setAIAnalyticsStudent(null)
          }}
        />
      )}
    </div>
  )
}
