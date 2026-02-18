import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import teacherService, { type ModuleStudent, type ModuleActivity } from '../../services/teacher.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import { Users, ListChecks, Plus, ArrowLeft, UserPlus, Trash2, FileText, BarChart3, X } from 'lucide-react'

export default function ModuleDetail() {
  const { moduleId } = useParams<{ moduleId: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [moduleName, setModuleName] = useState('')
  const [students, setStudents] = useState<ModuleStudent[]>([])
  const [activities, setActivities] = useState<ModuleActivity[]>([])
  const [showAddStudent, setShowAddStudent] = useState(false)
  const [allStudents, setAllStudents] = useState<any[]>([])
  const [selectedStudentId, setSelectedStudentId] = useState<string>("")
  const [adding, setAdding] = useState(false)

  const loadData = async () => {
    if (!moduleId || !user) return
    try {
      const [studentsData, activitiesData, allStudentsData] = await Promise.all([
        teacherService.getModuleStudents(moduleId),
        teacherService.getModuleActivities(moduleId),
        teacherService.getStudents()
      ])
      setStudents(studentsData)
      setActivities(activitiesData)
      setAllStudents(allStudentsData)
    } catch {
      toast({ title: 'Error cargando datos del módulo', variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [moduleId, user])

  const handleAddStudent = async () => {
    if (!moduleId || !selectedStudentId) return
    setAdding(true)
    try {
      await teacherService.addStudentsToModule(moduleId, [selectedStudentId])
      toast({ title: 'Estudiante agregado', variant: 'success' })
      setSelectedStudentId("")
      setShowAddStudent(false)
      loadData()
    } catch {
      toast({ title: 'Error agregando estudiante', variant: 'error' })
    } finally {
      setAdding(false)
    }
  }

  const handleRemoveStudent = async (studentId: string) => {
    if (!moduleId || !confirm('¿Eliminar estudiante del módulo?')) return
    try {
      await teacherService.removeStudentFromModule(moduleId, studentId)
      toast({ title: 'Estudiante eliminado', variant: 'success' })
      setStudents(prev => prev.filter(s => s.user_id !== studentId))
    } catch {
      toast({ title: 'Error eliminando estudiante', variant: 'error' })
    }
  }

  // Filter out students already in module
  const availableStudents = allStudents.filter(
    s => !students.some(ms => ms.user_id === s.user_id)
  )

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/teacher/modules')}
              className="rounded-lg p-2 hover:bg-gray-100 transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-500" />
            </button>
            <span>{moduleName || 'Módulo'}</span>
          </div>
        }
        description="Gestiona estudiantes y actividades de este módulo"
      />

      {/* Students Section */}
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Estudiantes ({students.length})</h2>
          </div>
          <button
            onClick={() => setShowAddStudent(!showAddStudent)}
            className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
          >
            {showAddStudent ? <X className="h-4 w-4" /> : <UserPlus className="h-4 w-4" />}
            {showAddStudent ? "Cancelar" : "Agregar Estudiantes"}
          </button>
        </div>

        {showAddStudent && (
          <div className="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Agregar estudiante al módulo</h3>
            <div className="flex gap-3">
              <div className="flex-1">
                <select
                  value={selectedStudentId}
                  onChange={(e) => setSelectedStudentId(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-gray-900 focus:ring-1 focus:ring-gray-900"
                >
                  <option value="">Seleccionar estudiante...</option>
                  {availableStudents.map(student => (
                    <option key={student.user_id} value={student.user_id}>
                      {student.full_name || student.username} ({student.email})
                    </option>
                  ))}
                </select>
                {availableStudents.length === 0 && (
                  <p className="mt-1 text-xs text-gray-500">No hay estudiantes disponibles para agregar.</p>
                )}
              </div>
              <button
                onClick={handleAddStudent}
                disabled={!selectedStudentId || adding}
                className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 transition-colors"
              >
                {adding ? <Spinner size="sm" className="border-gray-600 border-t-white" /> : "Agregar"}
              </button>
            </div>
          </div>
        )}

        {students.length === 0 ? (
          <EmptyState
            icon={<Users className="h-12 w-12" />}
            title="No hay estudiantes"
            description="Agrega estudiantes a este módulo para que puedan ver las actividades."
          />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {students.map(student => (
              <div key={student.user_id} className="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 p-3">
                <div className="overflow-hidden">
                  <p className="text-sm font-medium text-gray-900 truncate" title={student.full_name}>{student.full_name || 'Sin nombre'}</p>
                  <p className="text-xs text-gray-500 truncate" title={student.email}>{student.email}</p>
                </div>
                <button
                  onClick={() => handleRemoveStudent(student.user_id)}
                  className="shrink-0 rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-500 transition-colors"
                  title="Eliminar del módulo"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Activities Section */}
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ListChecks className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Actividades ({activities.length})</h2>
          </div>
          <button
            onClick={() => navigate(`/teacher/modules/${moduleId}/create-activity`)}
            className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Crear Actividad
          </button>
        </div>

        {activities.length === 0 ? (
          <EmptyState
            icon={<ListChecks className="h-12 w-12" />}
            title="No hay actividades"
            description="Crea actividades para este módulo"
          />
        ) : (
          <div className="space-y-3">
            {activities.map(activity => (
              <div key={activity.activity_id} className="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 p-4 hover:border-gray-200 transition-colors">
                <div className="flex items-start gap-3 flex-1">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white border border-gray-200 shrink-0">
                    <FileText className="h-5 w-5 text-gray-500" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-gray-900">{activity.title}</h3>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      <span>{activity.exercise_count || 0} ejercicios</span>
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${activity.status === 'published'
                        ? 'bg-green-50 text-green-700'
                        : 'bg-yellow-50 text-yellow-700'
                        }`}>
                        {activity.status === 'published' ? 'Publicada' : 'Borrador'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={async () => {
                      const newStatus = activity.status === 'published' ? 'draft' : 'published';
                      try {
                        await teacherService.updateActivityStatus(activity.activity_id, newStatus);
                        setActivities(prev => prev.map(a =>
                          a.activity_id === activity.activity_id ? { ...a, status: newStatus } : a
                        ));
                        toast({ title: `Actividad ${newStatus === 'published' ? 'publicada' : 'oculta'}`, variant: 'success' });
                      } catch {
                        toast({ title: 'Error actualizando estado', variant: 'error' });
                      }
                    }}
                    className={`inline-flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${activity.status === 'published'
                        ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                        : 'bg-green-600 text-white hover:bg-green-700'
                      }`}
                  >
                    {activity.status === 'published' ? 'Ocultar' : 'Publicar'}
                  </button>
                  <Link
                    to={`/teacher/modules/${moduleId}/activities/${activity.activity_id}`}
                    className="inline-flex items-center gap-2 rounded-lg bg-white border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <BarChart3 className="h-4 w-4" />
                    Ver Analytics
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
