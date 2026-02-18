import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import studentService, { type Course } from '../../services/student.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import { BookOpen, Plus, FolderOpen } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function StudentCourses() {
  const { user } = useAuth()
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [joinCode, setJoinCode] = useState('')
  const [joining, setJoining] = useState(false)
  const [showJoin, setShowJoin] = useState(false)

  const loadCourses = async () => {
    if (!user) return
    try {
      const data = await studentService.getCourses(user.id)
      setCourses(data)
    } catch {
      toast({ title: 'Error cargando cursos', variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadCourses() }, [user])

  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user || !joinCode.trim()) return
    setJoining(true)
    try {
      await studentService.joinCourse(user.id, joinCode.trim())
      toast({ title: 'Te uniste al curso exitosamente', variant: 'success' })
      setJoinCode('')
      setShowJoin(false)
      loadCourses()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Código inválido'
      toast({ title: 'Error', description: msg, variant: 'error' })
    } finally {
      setJoining(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Mis Cursos"
        description="Cursos en los que estás inscripto"
        actions={
          <button
            onClick={() => setShowJoin(!showJoin)}
            className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Unirme a curso
          </button>
        }
      />

      {/* Join Course */}
      {showJoin && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Unirse con código de acceso</h3>
          <form onSubmit={handleJoin} className="flex gap-3">
            <input
              type="text"
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value)}
              placeholder="Ingresa el código de acceso"
              className="flex h-10 flex-1 rounded-lg border border-gray-200 bg-white px-3.5 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={joining}
              className="inline-flex items-center rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 transition-colors"
            >
              {joining ? <Spinner size="sm" className="border-gray-600 border-t-white" /> : 'Unirme'}
            </button>
          </form>
        </div>
      )}

      {/* Courses */}
      {courses.length === 0 ? (
        <EmptyState
          icon={<BookOpen className="h-12 w-12" />}
          title="No estás inscripto en ningún curso"
          description="Usa un código de acceso proporcionado por tu docente para unirte a un curso."
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {courses.map((course) => (
            <div key={course.course_id} className="rounded-xl border border-gray-100 bg-white p-6 hover:shadow-sm transition-shadow">
              <div className="flex items-start gap-3 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 shrink-0">
                  <BookOpen className="h-5 w-5 text-gray-500" />
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-gray-900">{course.name}</h3>
                  <p className="text-xs text-gray-500">
                    {course.year} - Semestre {course.semester}
                  </p>
                </div>
              </div>

              {course.modules && course.modules.length > 0 && (
                <div className="space-y-2 mb-4">
                  {course.modules.map((mod) => (
                    <div key={mod.module_id} className="rounded-lg bg-gray-50 px-3 py-2">
                      <div className="flex items-center gap-2">
                        <FolderOpen className="h-3.5 w-3.5 text-gray-400" />
                        <span className="text-xs font-medium text-gray-700">{mod.title}</span>
                        <span className="ml-auto text-xs text-gray-400">
                          {mod.activities?.length || 0} actividades
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <Link
                to={`/courses/${course.course_id}`}
                className="flex items-center justify-center gap-2 w-full rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
              >
                Ver Actividades
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
