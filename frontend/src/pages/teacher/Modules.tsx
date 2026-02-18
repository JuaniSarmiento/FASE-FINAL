import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import teacherService, { type TeacherModule, type TeacherCourse } from '../../services/teacher.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import { FolderOpen, Plus, Trash2, Users, ListChecks, ChevronRight } from 'lucide-react'

export default function TeacherModules() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [modules, setModules] = useState<TeacherModule[]>([])
  const [courses, setCourses] = useState<TeacherCourse[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({ name: '', description: '' })

  const loadData = async () => {
    if (!user) return
    try {
      const [m, c] = await Promise.all([
        teacherService.getModules(user.id),
        teacherService.getCourses(user.id).catch(() => []),
      ])
      setModules(m)
      setCourses(c)
    } catch {
      toast({ title: 'Error cargando módulos', variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [user])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user || !form.name) return
    setCreating(true)
    try {
      await teacherService.createModule(form.name, user.id, form.description || undefined)
      toast({ title: 'Módulo creado', variant: 'success' })
      setForm({ name: '', description: '' })
      setShowCreate(false)
      loadData()
    } catch {
      toast({ title: 'Error creando módulo', variant: 'error' })
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (moduleId: string) => {
    if (!confirm('¿Eliminar este módulo?')) return
    try {
      await teacherService.deleteModule(moduleId)
      toast({ title: 'Módulo eliminado', variant: 'success' })
      setModules((prev) => prev.filter((m) => m.module_id !== moduleId))
    } catch {
      toast({ title: 'Error eliminando módulo', variant: 'error' })
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Módulos"
        description="Organiza el contenido de tus cursos en módulos"
        actions={
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Nuevo Módulo
          </button>
        }
      />

      {showCreate && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Nombre del módulo</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                placeholder="Ej: Módulo 1 - Introducción a Python"
                className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Descripción (opcional)</label>
              <input
                type="text"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Descripción breve"
                className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              />
            </div>
            <div className="flex gap-3">
              <button type="submit" disabled={creating} className="inline-flex items-center rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 transition-colors">
                {creating ? <Spinner size="sm" className="border-gray-600 border-t-white" /> : 'Crear'}
              </button>
              <button type="button" onClick={() => setShowCreate(false)} className="rounded-lg px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors">
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {modules.length === 0 ? (
        <EmptyState icon={<FolderOpen className="h-12 w-12" />} title="No hay módulos" description="Crea un módulo para organizar las actividades de tu curso." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {modules.map((m) => (
            <div 
              key={m.module_id} 
              onClick={() => navigate(`/teacher/modules/${m.module_id}`)}
              className="rounded-xl border border-gray-100 bg-white p-5 hover:shadow-md hover:border-gray-200 transition-all cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 group-hover:bg-gray-900 transition-colors shrink-0">
                    <FolderOpen className="h-5 w-5 text-gray-500 group-hover:text-white transition-colors" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-semibold text-gray-900">{m.name}</h3>
                      <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-gray-900 transition-colors" />
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">{m.description || 'Sin descripción'}</p>
                  </div>
                </div>
                <button 
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDelete(m.module_id)
                  }} 
                  className="rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-500 transition-colors"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
              <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
                <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" /> {m.student_count} estudiantes</span>
                <span className="flex items-center gap-1"><ListChecks className="h-3.5 w-3.5" /> {m.course_id ? '1 curso' : '—'}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
