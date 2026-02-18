import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { toast } from '../../hooks/useToast'
import Spinner from '../../components/ui/Spinner'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, user } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) return
    setLoading(true)
    try {
      await login({ email, password })
      // Redirect based on user role after login is complete
      // Wait a tick for user to be set in context
      setTimeout(() => {
        const storedUser = localStorage.getItem('user')
        if (storedUser) {
          const userData = JSON.parse(storedUser)
          const isTeacher = userData.roles?.includes('teacher')
          navigate(isTeacher ? '/teacher' : '/')
        } else {
          navigate('/')
        }
      }, 100)
    } catch (err: any) {
      console.error('Login Error:', err)
      const msg = err.response?.data?.detail || err.message || 'Credenciales inválidas'
      toast({ title: 'Error al iniciar sesión', description: msg, variant: 'error' })
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
            Plataforma de Aprendizaje con Inteligencia Artificial
          </h2>
          <p className="mt-4 text-gray-400 leading-relaxed">
            Aprende a programar con un tutor IA personalizado que se adapta a tu ritmo y estilo de aprendizaje.
          </p>
          <div className="mt-12 grid grid-cols-2 gap-6">
            {[
              { label: 'Tutor Socrático', desc: 'Guía personalizada con IA' },
              { label: 'Ejercicios', desc: 'Generados con contexto RAG' },
              { label: 'Feedback', desc: 'Evaluación detallada en tiempo real' },
              { label: 'Analytics', desc: 'Seguimiento de tu progreso' },
            ].map((f) => (
              <div key={f.label} className="rounded-lg border border-gray-800 p-4">
                <p className="text-sm font-medium text-white">{f.label}</p>
                <p className="mt-1 text-xs text-gray-500">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex flex-1 items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex h-10 w-10 items-center justify-center rounded-lg bg-gray-900 text-white text-sm font-bold mb-8">
            AI
          </div>

          <h1 className="text-2xl font-semibold text-gray-900">Iniciar sesión</h1>
          <p className="mt-2 text-sm text-gray-500">Ingresa tus credenciales para acceder a la plataforma</p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@email.com"
                required
                className="flex h-11 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-shadow"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Contraseña</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="flex h-11 w-full rounded-lg border border-gray-200 bg-white px-3.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-shadow"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex h-11 w-full items-center justify-center rounded-lg bg-gray-900 text-sm font-medium text-white hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 disabled:opacity-50 transition-colors"
            >
              {loading ? <Spinner size="sm" className="border-gray-600 border-t-white" /> : 'Iniciar sesión'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            ¿No tienes cuenta?{' '}
            <Link to="/register" className="font-medium text-gray-900 hover:underline">
              Registrarse
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
