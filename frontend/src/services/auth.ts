import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:5001'

export interface User {
  _id: string
  username: string
  email: string
  name: string
  profile_pic: string
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  message: string
  user: User
  token: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  name?: string
  profile_pic?: string
}

export interface LoginData {
  email: string
  password: string
}

export interface ProfileUpdateData {
  name?: string
  profile_pic?: string
}

export interface ChangePasswordData {
  current_password: string
  new_password: string
}

/** Shared client for REST API (Bearer token when present). */
export const api = axios.create({
  baseURL: API_BASE_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Do not redirect on failed login / register / token validation
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url ?? ''
      const method = (error.config?.method || '').toLowerCase()
      const isPublicAuth =
        url.includes('/api/auth/sessions') ||
        url.includes('/api/auth/token/validation') ||
        (method === 'post' && (url === '/api/users' || url.endsWith('/api/users')))
      if (!isPublicAuth) {
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const register = async (data: RegisterData): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/api/users', data)
  localStorage.setItem('authToken', response.data.token)
  localStorage.setItem('user', JSON.stringify(response.data.user))
  return response.data
}

export const login = async (data: LoginData): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/api/auth/sessions', data)
  localStorage.setItem('authToken', response.data.token)
  localStorage.setItem('user', JSON.stringify(response.data.user))
  return response.data
}

export const logout = async (): Promise<void> => {
  try {
    await api.delete('/api/auth/sessions')
  } catch {
    /* ignore network errors — still clear client */
  }
  localStorage.removeItem('authToken')
  localStorage.removeItem('user')
}

export const getProfile = async (): Promise<{ user: User; library_stats: unknown }> => {
  const response = await api.get('/api/users/me')
  return response.data
}

/** Updates profile; also call `syncSessionUser(user)` from AuthContext so UI state matches. */
export const updateProfile = async (
  data: ProfileUpdateData
): Promise<{ message: string; user: User }> => {
  const response = await api.patch('/api/users/me', data)
  localStorage.setItem('user', JSON.stringify(response.data.user))
  return response.data
}

export const changePassword = async (
  data: ChangePasswordData
): Promise<{ message: string }> => {
  const response = await api.patch('/api/users/me/password', data)
  return response.data
}

export const verifyToken = async (
  token: string
): Promise<{ valid: boolean; user: User }> => {
  const response = await api.post('/api/auth/token/validation', { token })
  return response.data
}

export const getCurrentUser = (): User | null => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}

export const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken')
}

export const isAuthenticated = (): boolean => {
  return !!getAuthToken()
}

/** @deprecated Use `api` from this module instead */
export const createAuthenticatedApi = () => api
