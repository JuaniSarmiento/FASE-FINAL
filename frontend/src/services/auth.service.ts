import api from './api'
import { AuthResponseDTO, UserDTO } from '../types/dtos'

// BACKWARD COMPATIBILITY: Re-export UserDTO as User
export type User = UserDTO

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
  role?: string
}

const authService = {
  async login(data: LoginRequest): Promise<any> {
    const params = new URLSearchParams()
    params.append('username', data.email)
    params.append('password', data.password)

    const res = await api.post('/auth/token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })

    const backendResponse = res.data;
    console.log('LOGIN RESPONSE:', backendResponse);
    const user = {
      ...backendResponse.user,
      username: backendResponse.user.email.split('@')[0],
      id: backendResponse.user.id,
      roles: backendResponse.user.roles || (backendResponse.user.role ? [backendResponse.user.role] : ['student'])
    }

    const response = {
      user: user,
      tokens: {
        access_token: backendResponse.tokens.access_token,
        refresh_token: backendResponse.tokens.refresh_token,
        token_type: backendResponse.tokens.token_type
      }
    }

    localStorage.setItem('access_token', response.tokens.access_token)
    localStorage.setItem('user', JSON.stringify(user))

    return response
  },

  async register(data: RegisterRequest): Promise<any> {
    const payload = {
      email: data.email,
      password: data.password,
      full_name: data.full_name || data.username,
      role: data.role || 'student',
    }
    const res = await api.post('/auth/register', payload)

    const backendResponse = res.data;
    const user = {
      ...backendResponse.user,
      username: backendResponse.user.email.split('@')[0],
      id: backendResponse.user.id,
      roles: backendResponse.user.roles || (backendResponse.user.role ? [backendResponse.user.role] : ['student'])
    }
    const response = {
      user: user,
      tokens: {
        access_token: backendResponse.tokens.access_token,
        refresh_token: backendResponse.tokens.refresh_token,
        token_type: backendResponse.tokens.token_type
      }
    }
    return response
  },

  getMe(): User | null {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },

  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  },
}

export default authService
