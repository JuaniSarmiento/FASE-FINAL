import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import studentService from '../../services/student.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import { FileText, Lock, CheckCircle2, Clock, ChevronRight } from 'lucide-react'
import type { Activity } from '../../services/student.service'

interface ActivityWithGrade extends Activity {
  final_grade?: number
  is_completed?: boolean
}

export default function CourseDetail() {
  const { courseId } = useParams<{ courseId: string }>()
  const { user } = useAuth()
  const [activities, setActivities] = useState<ActivityWithGrade[]>([])
  const [courseName, setCourseName] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user || !courseId) return

    const loadData = async () => {
      try {
        // Get courses with modules and activities
        const courses = await studentService.getCourses(user.id)
        const course = courses.find(c => c.course_id === courseId)

        if (!course) {
          toast({ title: 'Curso no encontrado', variant: 'error' })
          setLoading(false)
          return
        }

        // Get module_id from query params
        const searchParams = new URLSearchParams(window.location.search);
        const moduleId = searchParams.get('module_id');

        if (moduleId) {
          const activeModule = course.modules.find((m: any) => m.module_id === moduleId || m.id === moduleId)
          if (activeModule) {
            setCourseName(activeModule.title) // Show Module Title instead of Course Name
          } else {
            setCourseName(course.name)
          }
        } else {
          setCourseName(course.name)
        }

        // Extract all activities from all modules
        const allActivities: Activity[] = []

        if (course.modules) {
          for (const module of course.modules) {
            // Filter by module if moduleId is present
            if (moduleId && module.module_id !== moduleId && module.id !== moduleId) continue;

            if (module.activities && module.activities.length > 0) {
              allActivities.push(...module.activities)
            }
          }
        }

        // Get grades for all activities (Single optimized call)
        // Note: The backend returns a list of all graded submissions for the student.
        // We match them by activity_id to avoid the N+1 problem and incorrect mapping.
        let gradesMap = new Map<string, any>()
        try {
          const allGrades = await studentService.getGrades(user.id)
          allGrades.forEach(g => {
            // Store the grade keyed by activity_id
            // If multiple grades exist, this takes the last one (or we could logic for best/latest)
            gradesMap.set(g.activity_id, g)
          })
        } catch (e) {
          console.error("Error fetching grades", e)
        }

        // Map activities with their corresponding grade
        const activitiesWithGrades = allActivities.map((activity) => {
          const grade = gradesMap.get(activity.activity_id)
          return {
            ...activity,
            final_grade: grade ? grade.grade : undefined,
            is_completed: !!grade,
          }
        })

        setActivities(activitiesWithGrades)
      } catch {
        toast({ title: 'Error cargando actividades', variant: 'error' })
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [user, courseId])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={courseName}
        description={`${activities.length} actividad${activities.length !== 1 ? 'es' : ''} disponible${activities.length !== 1 ? 's' : ''}`}
      />

      {activities.length === 0 ? (
        <EmptyState
          icon={<FileText className="h-12 w-12" />}
          title="No hay actividades"
          description="Este curso aún no tiene actividades asignadas"
        />
      ) : (
        <div className="grid gap-4">
          {activities.map((activity) => (
            <div
              key={activity.activity_id}
              className="rounded-xl border border-gray-100 bg-white p-5 hover:border-gray-200 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-base font-semibold text-gray-900 truncate">
                      {activity.title}
                    </h3>

                    {activity.is_completed ? (
                      <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 shrink-0">
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                        <span className="text-xs font-medium text-emerald-700">
                          Nota: {activity.final_grade?.toFixed(1)}/10
                        </span>
                      </div>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-medium shrink-0">
                        <Clock className="h-3 w-3" />
                        Pendiente
                      </span>
                    )}
                  </div>

                  {activity.instructions && (
                    <p className="text-sm text-gray-500 line-clamp-2 mb-3">
                      {activity.instructions}
                    </p>
                  )}

                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    {activity.difficulty && (
                      <span className="capitalize">{activity.difficulty}</span>
                    )}
                  </div>
                </div>

                <div className="shrink-0">
                  {activity.is_completed ? (
                    <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-50 text-gray-400 cursor-not-allowed">
                      <Lock className="h-4 w-4" />
                      <span className="text-sm font-medium">Completada</span>
                    </div>
                  ) : (
                    <Link
                      to={`/activities/${activity.activity_id}`}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-900 text-white hover:bg-gray-800 transition-colors"
                    >
                      <span className="text-sm font-medium">Comenzar</span>
                      <ChevronRight className="h-4 w-4" />
                    </Link>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
