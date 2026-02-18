import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import studentService from '../../services/student.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import { BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function StudentDashboard() {
  const { user } = useAuth()
  const [courses, setCourses] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    const load = async () => {
      try {
        const data = await studentService.getCourses(user.id)
        setCourses(data)
      } catch (err) {
        console.error(err)
        toast({ title: 'Error cargando cursos', variant: 'error' })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [user])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title={`Bienvenido, ${user?.full_name || user?.username || 'Estudiante'}`}
        description="Tus Módulos Activos"
      />

      {courses.length === 0 ? (
        <div className="rounded-xl border border-gray-100 bg-white p-8 text-center">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-gray-900">No tienes inscripciones activas</h3>
          <p className="text-gray-500 mt-1">Cuando un docente te inscriba a un módulo, aparecerá aquí.</p>
        </div>
      ) : (
        <div className="grid gap-6">
          {courses.map(course => (
            <div key={course.course_id} className="space-y-4">
              {/* Optional: Show Course Header if we have multiple courses */}
              {/* <h2 className="text-lg font-semibold text-gray-900">{course.name}</h2> */}

              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {course.modules.map((mod: any) => (
                  <div key={mod.module_id} className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                        <BookOpen className="h-5 w-5" />
                      </div>
                      <span className="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700">
                        Activo
                      </span>
                    </div>

                    <h3 className="text-base font-semibold text-gray-900 mb-1">{mod.title}</h3>
                    <p className="text-sm text-gray-500 mb-4">{mod.activities?.length || 0} actividades</p>

                    <Link
                      to={`/courses/${course.course_id}?module_id=${mod.module_id}`}
                      className="flex items-center justify-center gap-2 w-full rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
                    >
                      Ver Módulo
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}


