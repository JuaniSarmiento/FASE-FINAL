import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { toast } from '../../hooks/useToast'
import Spinner from '../../components/ui/Spinner'

export default function RegisterPage() {
  const [form, setForm] = useState({ username: '', email: '', password: '', full_name: '', role: 'student' })
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const update = (field: string, value: string) => setForm((f) => ({ ...f, [field]: value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.username || !form.email || !form.password) return
    setLoading(true)
    try {
      await register(form)
      // Redirect based on registered role
      const isTeacher = form.role === 'teacher'
      navigate(isTeacher ? '/teacher' : '/')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Error al registrarse'
      toast({ title: 'Error', description: msg, variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 items-center justify-center bg-gray-950 p-12">
        <div className="max-w-md">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-gray-900 text-lg font-bold mb-8">
            AI
          </div>
          <h2 className="text-3xl font-semibold text-white">
            Comienza tu viaje de aprendizaje
          </h2>
          <p className="mt-4 text-gray-400 leading-relaxed">
            Únete a la plataforma y accede a ejercicios generados por IA, tutoría socrática personalizada y análisis detallado de tu progreso.
          </p>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex flex-1 items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex h-10 w-10 items-center justify-center rounded-lg bg-gray-900 text-white text-sm font-bold mb-8">
            AI
          </div>

          <h1 className="text-2xl font-semibold text-gray-900">Crear cuenta</h1>
          <p className="mt-2 text-sm text-gray-500">Completa la información para registrarte</p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Nombre completo</label>
              <input
                type="text"
                value={form.full_name}
                onChange={(e) => update('full_name', e.target.value)}
                placeholder="Juan Pérez"
                className="flex h-11 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-shadow"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Usuario</label>
              <input
                type="text"
                value={form.username}
                onChange={(e) => update('username', e.target.value)}
                placeholder="juanperez"
                required
                className="flex h-11 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-shadow"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => update('email', e.target.value)}
                placeholder="tu@email.com"
                required
                className="flex h-11 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-shadow"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Contraseña</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => update('password', e.target.value)}
                placeholder="••••••••"
                required
                className="flex h-11 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-shadow"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Rol</label>
              <select
                value={form.role}
                onChange={(e) => update('role', e.target.value)}
                className="flex h-11 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-shadow"
              >
                <option value="student">Estudiante</option>
                <option value="teacher">Docente</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex h-11 w-full items-center justify-center rounded-lg bg-gray-900 text-sm font-medium text-white hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 disabled:opacity-50 transition-colors"
            >
              {loading ? <Spinner size="sm" className="border-gray-600 border-t-white" /> : 'Crear cuenta'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            ¿Ya tienes cuenta?{' '}
            <Link to="/login" className="font-medium text-gray-900 hover:underline">
              Iniciar sesión
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
