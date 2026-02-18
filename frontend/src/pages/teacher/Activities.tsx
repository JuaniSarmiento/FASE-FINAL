import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import teacherService, { type CreateActivityRequest } from '../../services/teacher.service'
import type { Activity } from '../../services/student.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import { Plus, ListChecks, ArrowRight, Trash2, Send } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function TeacherActivities() {
  const { user } = useAuth()
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({ title: '', instructions: '', course_id: '' })
  const [courses, setCourses] = useState<{ course_id: string; course_name: string }[]>([])

  const loadData = async () => {
    if (!user) return
    try {
      const [acts, crss] = await Promise.all([
        teacherService.getActivities(user.id),
        teacherService.getCourses(user.id).catch(() => []),
      ])
      setActivities(acts)
      setCourses(crss)
    } catch {
      toast({ title: 'Error cargando actividades', variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [user])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user || !form.title || !form.course_id) return
    setCreating(true)
    try {
      const data: CreateActivityRequest = {
        title: form.title,
        instructions: form.instructions,
        course_id: form.course_id,
        teacher_id: user.id,
      }
      await teacherService.createActivity(data)
      toast({ title: 'Actividad creada', variant: 'success' })
      setForm({ title: '', instructions: '', course_id: '' })
      setShowCreate(false)
      loadData()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Error'
      toast({ title: 'Error', description: msg, variant: 'error' })
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (activityId: string) => {
    if (!confirm('¿Eliminar esta actividad?')) return
    try {
      await teacherService.deleteActivity(activityId)
      toast({ title: 'Actividad eliminada', variant: 'success' })
      setActivities((prev) => prev.filter((a) => a.activity_id !== activityId))
    } catch {
      toast({ title: 'Error eliminando', variant: 'error' })
    }
  }

  const handlePublish = async (activityId: string) => {
    try {
      await teacherService.publishActivity(activityId)
      toast({ title: 'Actividad publicada', variant: 'success' })
      loadData()
    } catch {
      toast({ title: 'Error publicando', variant: 'error' })
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Actividades"
        description="Gestiona las actividades de tus cursos"
        actions={
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Nueva Actividad
          </button>
        }
      />

      {/* Create form */}
      {showCreate && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Crear Actividad</h3>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Título</label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                required
                className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                placeholder="Ej: Ejercicio de funciones en Python"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Curso</label>
              <select
                value={form.course_id}
                onChange={(e) => setForm({ ...form, course_id: e.target.value })}
                required
                className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              >
                <option value="">Seleccionar curso</option>
                {courses.map((c) => (
                  <option key={c.course_id} value={c.course_id}>{c.course_name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Instrucciones (opcional)</label>
              <textarea
                value={form.instructions}
                onChange={(e) => setForm({ ...form, instructions: e.target.value })}
                rows={3}
                className="flex w-full rounded-lg border border-gray-200 bg-white px-3.5 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                placeholder="Instrucciones para los estudiantes..."
              />
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={creating}
                className="inline-flex items-center rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 transition-colors"
              >
                {creating ? <Spinner size="sm" className="border-gray-600 border-t-white" /> : 'Crear'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="rounded-lg px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Activities list */}
      {activities.length === 0 ? (
        <EmptyState
          icon={<ListChecks className="h-12 w-12" />}
          title="No hay actividades"
          description="Crea tu primera actividad para que tus estudiantes puedan practicar."
        />
      ) : (
        <div className="space-y-3">
          {activities.map((a) => (
            <div
              key={a.activity_id}
              className="flex items-center gap-4 rounded-xl border border-gray-100 bg-white px-6 py-5 hover:shadow-sm transition-all"
            >
              <Link to={`/teacher/activities/${a.activity_id}`} className="min-w-0 flex-1 group">
                <div className="flex items-center gap-3">
                  <h3 className="text-sm font-semibold text-gray-900 group-hover:text-gray-700 truncate transition-colors">
                    {a.title}
                  </h3>
                  <span className={`shrink-0 inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${
                    a.status === 'published' ? 'bg-emerald-50 text-emerald-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {a.status === 'published' ? 'Publicada' : 'Borrador'}
                  </span>
                </div>
                {a.instructions && (
                  <p className="mt-1 text-xs text-gray-500 truncate max-w-lg">{a.instructions}</p>
                )}
              </Link>
              <div className="flex items-center gap-2 shrink-0">
                {a.status !== 'published' && (
                  <button
                    onClick={() => handlePublish(a.activity_id)}
                    className="rounded-lg p-2 text-gray-400 hover:bg-emerald-50 hover:text-emerald-600 transition-colors"
                    title="Publicar"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                )}
                <button
                  onClick={() => handleDelete(a.activity_id)}
                  className="rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-500 transition-colors"
                  title="Eliminar"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
                <Link to={`/teacher/activities/${a.activity_id}`} className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors">
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
