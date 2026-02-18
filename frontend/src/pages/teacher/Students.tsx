import { useEffect, useState } from 'react'
import teacherService, { type StudentInfo } from '../../services/teacher.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import { Users, Search, Mail } from 'lucide-react'

export default function TeacherStudents() {
  const [students, setStudents] = useState<StudentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    teacherService.getStudents()
      .then(setStudents)
      .catch(() => toast({ title: 'Error cargando estudiantes', variant: 'error' }))
      .finally(() => setLoading(false))
  }, [])

  const filtered = students.filter((s) =>
    s.full_name?.toLowerCase().includes(search.toLowerCase()) ||
    s.email?.toLowerCase().includes(search.toLowerCase()) ||
    s.username?.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Estudiantes" description="Lista de todos los estudiantes registrados" />

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por nombre o email..."
          className="flex h-10 w-full rounded-lg border border-gray-200 bg-white pl-9 pr-3.5 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={<Users className="h-12 w-12" />}
          title={search ? 'Sin resultados' : 'No hay estudiantes'}
          description={search ? 'Intenta con otro término de búsqueda' : 'Los estudiantes aparecerán aquí cuando se registren'}
        />
      ) : (
        <div className="rounded-xl border border-gray-100 bg-white overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="px-6 py-3.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                <th className="px-6 py-3.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                <th className="px-6 py-3.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filtered.map((s) => (
                <tr key={s.user_id} className="hover:bg-gray-50/50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-600 shrink-0">
                        {(s.full_name || s.username || '?').charAt(0).toUpperCase()}
                      </div>
                      <span className="text-sm font-medium text-gray-900">{s.full_name || s.username}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{s.username}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center gap-1.5 text-sm text-gray-500">
                      <Mail className="h-3.5 w-3.5" />
                      {s.email}
                    </span>
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
