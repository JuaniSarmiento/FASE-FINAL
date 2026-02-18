import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import authService, { type User, type LoginRequest, type RegisterRequest } from '../services/auth.service'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  isTeacher: boolean
  isStudent: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem('user')
    const token = localStorage.getItem('access_token')
    if (stored && token) {
      try {
        setUser(JSON.parse(stored))
      } catch {
        localStorage.removeItem('user')
      }
    }
    setIsLoading(false)
  }, [])

  const login = useCallback(async (data: LoginRequest) => {
    const res = await authService.login(data)
    localStorage.setItem('access_token', res.tokens.access_token)
    localStorage.setItem('refresh_token', res.tokens.refresh_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    setUser(res.user)
  }, [])

  const register = useCallback(async (data: RegisterRequest) => {
    const res = await authService.register(data)
    localStorage.setItem('access_token', res.tokens.access_token)
    localStorage.setItem('refresh_token', res.tokens.refresh_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    setUser(res.user)
  }, [])

  const logout = useCallback(() => {
    authService.logout()
    setUser(null)
  }, [])

  const isTeacher = user?.roles?.includes('teacher') ?? false
  const isStudent = user?.roles?.includes('student') ?? false

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, isTeacher, isStudent }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
