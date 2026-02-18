import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import studentService, { type Activity } from '../../services/student.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import { ListChecks, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function StudentActivities() {
  const { user } = useAuth()
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    studentService
      .getActivities(user.id)
      .then(setActivities)
      .catch(() => toast({ title: 'Error cargando actividades', variant: 'error' }))
      .finally(() => setLoading(false))
  }, [user])

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Actividades" description="Todas las actividades disponibles" />

      {activities.length === 0 ? (
        <EmptyState
          icon={<ListChecks className="h-12 w-12" />}
          title="No hay actividades disponibles"
          description="Las actividades aparecerán aquí cuando tu docente las publique."
        />
      ) : (
        <div className="space-y-3">
          {activities.map((activity) => (
            <Link
              key={activity.activity_id}
              to={`/activities/${activity.activity_id}`}
              className="flex items-center justify-between rounded-xl border border-gray-100 bg-white px-6 py-5 hover:shadow-sm hover:border-gray-200 transition-all group"
            >
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-gray-900 group-hover:text-gray-700 transition-colors">
                  {activity.title}
                </h3>
                {activity.instructions && (
                  <p className="mt-1 text-xs text-gray-500 truncate max-w-lg">
                    {activity.instructions}
                  </p>
                )}
                <div className="mt-2 flex items-center gap-3">
                  {activity.difficulty && (
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                      activity.difficulty === 'easy' ? 'bg-emerald-50 text-emerald-700' :
                      activity.difficulty === 'medium' ? 'bg-amber-50 text-amber-700' :
                      'bg-red-50 text-red-700'
                    }`}>
                      {activity.difficulty === 'easy' ? 'Fácil' : activity.difficulty === 'medium' ? 'Medio' : 'Difícil'}
                    </span>
                  )}
                  <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                    activity.status === 'published' ? 'bg-blue-50 text-blue-700' :
                    activity.status === 'completed' ? 'bg-emerald-50 text-emerald-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {activity.status === 'published' ? 'Disponible' :
                     activity.status === 'completed' ? 'Completada' : activity.status}
                  </span>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-300 group-hover:text-gray-500 transition-colors ml-4 shrink-0" />
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
