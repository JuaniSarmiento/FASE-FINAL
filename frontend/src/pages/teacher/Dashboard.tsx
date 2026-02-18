import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import teacherService, { type TeacherCourse, type TeacherModule } from '../../services/teacher.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import StatCard from '../../components/ui/StatCard'
import Spinner from '../../components/ui/Spinner'
import { Link } from 'react-router-dom'
import { BookOpen, FolderOpen, Users, ListChecks, ArrowRight } from 'lucide-react'

export default function TeacherDashboard() {
  const { user } = useAuth()
  const [courses, setCourses] = useState<TeacherCourse[]>([])
  const [modules, setModules] = useState<TeacherModule[]>([])
  const [activities, setActivities] = useState<{ activity_id: string; title: string; status: string }[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    Promise.all([
      teacherService.getCourses(user.id).catch(() => []),
      teacherService.getModules(user.id).catch(() => []),
      teacherService.getActivities(user.id, 10).catch(() => []),
    ])
      .then(([c, m, a]) => { setCourses(c); setModules(m); setActivities(a) })
      .catch(() => toast({ title: 'Error cargando dashboard', variant: 'error' }))
      .finally(() => setLoading(false))
  }, [user])

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  const totalStudents = modules.reduce((sum, m) => sum + (m.student_count || 0), 0)

  return (
    <div className="space-y-8">
      <PageHeader
        title="Panel Docente"
        description="Gestiona tus cursos, actividades y estudiantes"
      />

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Cursos" value={courses.length} icon={<BookOpen className="h-5 w-5" />} />
        <StatCard label="Módulos" value={modules.length} icon={<FolderOpen className="h-5 w-5" />} />
        <StatCard label="Actividades" value={activities.length} icon={<ListChecks className="h-5 w-5" />} />
        <StatCard label="Estudiantes" value={totalStudents} icon={<Users className="h-5 w-5" />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activities */}
        <div className="rounded-xl border border-gray-100 bg-white">
          <div className="flex items-center justify-between p-5 pb-3">
            <h2 className="text-sm font-semibold text-gray-900">Actividades Recientes</h2>
            <Link to="/teacher/activities" className="text-xs font-medium text-gray-500 hover:text-gray-900 transition-colors">
              Ver todas
            </Link>
          </div>
          <div className="border-t border-gray-50 divide-y divide-gray-50">
            {activities.length === 0 ? (
              <p className="p-5 text-center text-sm text-gray-400">No hay actividades creadas</p>
            ) : (
              activities.slice(0, 5).map((a) => (
                <Link
                  key={a.activity_id}
                  to={`/teacher/activities/${a.activity_id}`}
                  className="flex items-center justify-between px-5 py-3.5 hover:bg-gray-50/50 transition-colors group"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{a.title}</p>
                    <span className={`mt-0.5 inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${
                      a.status === 'published' ? 'bg-emerald-50 text-emerald-700' :
                      a.status === 'draft' ? 'bg-gray-100 text-gray-600' :
                      'bg-blue-50 text-blue-600'
                    }`}>
                      {a.status === 'published' ? 'Publicada' : a.status === 'draft' ? 'Borrador' : a.status}
                    </span>
                  </div>
                  <ArrowRight className="h-4 w-4 text-gray-300 group-hover:text-gray-500 shrink-0 transition-colors" />
                </Link>
              ))
            )}
          </div>
        </div>

        {/* Modules */}
        <div className="rounded-xl border border-gray-100 bg-white">
          <div className="flex items-center justify-between p-5 pb-3">
            <h2 className="text-sm font-semibold text-gray-900">Módulos</h2>
            <Link to="/teacher/modules" className="text-xs font-medium text-gray-500 hover:text-gray-900 transition-colors">
              Ver todos
            </Link>
          </div>
          <div className="border-t border-gray-50 divide-y divide-gray-50">
            {modules.length === 0 ? (
              <p className="p-5 text-center text-sm text-gray-400">No hay módulos creados</p>
            ) : (
              modules.slice(0, 5).map((m) => (
                <div key={m.module_id} className="flex items-center justify-between px-5 py-3.5">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{m.name}</p>
                    <p className="text-xs text-gray-500">{m.description || 'Sin descripción'}</p>
                  </div>
                  <span className="text-xs text-gray-400">{m.student_count} estudiantes</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
