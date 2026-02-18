import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useUIStore } from '../stores/uiStore'
import {
  LayoutDashboard,
  BookOpen,
  ListChecks,
  GraduationCap,
  Menu,
  LogOut,
  ChevronRight,
  User,
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Mis Cursos', href: '/courses', icon: BookOpen },
  { name: 'Calificaciones', href: '/grades', icon: GraduationCap },
]

export default function StudentLayout() {
  const { user, logout, isTeacher } = useAuth()
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gray-50/50">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-30 flex flex-col border-r border-gray-200 bg-white transition-all duration-300 ${
          sidebarOpen ? 'w-64' : 'w-[70px]'
        }`}
      >
        {/* Logo */}
        <div className="flex h-16 items-center border-b border-gray-100 px-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-900 text-white text-sm font-bold shrink-0">
              AI
            </div>
            {sidebarOpen && (
              <span className="text-sm font-semibold text-gray-900 truncate">
                AI Learning
              </span>
            )}
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.href}
              to={item.href}
              end={item.href === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
            >
              <item.icon className="h-5 w-5 shrink-0" />
              {sidebarOpen && <span className="truncate">{item.name}</span>}
            </NavLink>
          ))}

          {isTeacher && (
            <>
              <div className="my-3 border-t border-gray-100" />
              <NavLink
                to="/teacher"
                className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
              >
                <ChevronRight className="h-5 w-5 shrink-0" />
                {sidebarOpen && <span>Panel Docente</span>}
              </NavLink>
            </>
          )}
        </nav>

        {/* User */}
        <div className="border-t border-gray-100 p-3">
          <div className="flex items-center gap-3 rounded-lg px-3 py-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 shrink-0">
              <User className="h-4 w-4 text-gray-500" />
            </div>
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            )}
          </div>
          <button
            onClick={handleLogout}
            className="mt-1 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-gray-500 hover:bg-red-50 hover:text-red-600 transition-colors"
          >
            <LogOut className="h-4 w-4 shrink-0" />
            {sidebarOpen && <span>Cerrar sesión</span>}
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-[70px]'}`}>
        {/* Top bar */}
        <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-gray-200 bg-white/80 backdrop-blur-sm px-6">
          <button onClick={toggleSidebar} className="rounded-lg p-2 hover:bg-gray-100 transition-colors">
            <Menu className="h-5 w-5 text-gray-500" />
          </button>
        </header>

        {/* Content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
