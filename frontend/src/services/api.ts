import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300_000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: attach JWT token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: handle 401, unwrap data
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Try refresh token
      const refresh = localStorage.getItem('refresh_token')
      if (refresh && !error.config?.url?.includes('/auth/')) {
        try {
          const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refresh,
          })
          const { access_token } = res.data
          localStorage.setItem('access_token', access_token)
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${access_token}`
            return api.request(error.config)
          }
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default api
