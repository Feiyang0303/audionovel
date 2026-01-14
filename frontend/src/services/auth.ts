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

// Create axios instance with auth interceptor
const authApi = axios.create({
  baseURL: `${API_BASE_URL}/auth`,
})

// Add auth token to requests if available
authApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token expiration
authApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth functions
export const register = async (data: RegisterData): Promise<AuthResponse> => {
  const response = await authApi.post<AuthResponse>('/register', data)
  
  // Store token and user data
  localStorage.setItem('authToken', response.data.token)
  localStorage.setItem('user', JSON.stringify(response.data.user))
  
  return response.data
}

export const login = async (data: LoginData): Promise<AuthResponse> => {
  const response = await authApi.post<AuthResponse>('/login', data)
  
  // Store token and user data
  localStorage.setItem('authToken', response.data.token)
  localStorage.setItem('user', JSON.stringify(response.data.user))
  
  return response.data
}

export const logout = (): void => {
  localStorage.removeItem('authToken')
  localStorage.removeItem('user')
}

export const getProfile = async (): Promise<{ user: User; library_stats: any }> => {
  const response = await authApi.get('/profile')
  return response.data
}

export const updateProfile = async (data: ProfileUpdateData): Promise<{ message: string; user: User }> => {
  const response = await authApi.put('/profile', data)
  
  // Update stored user data
  localStorage.setItem('user', JSON.stringify(response.data.user))
  
  return response.data
}

export const changePassword = async (data: ChangePasswordData): Promise<{ message: string }> => {
  const response = await authApi.post('/change-password', data)
  return response.data
}

export const verifyToken = async (token: string): Promise<{ valid: boolean; user: User }> => {
  const response = await authApi.post('/verify-token', { token })
  return response.data
}

// Utility functions
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

// Create authenticated API instance
export const createAuthenticatedApi = () => {
  const api = axios.create({
    baseURL: API_BASE_URL,
  })

  api.interceptors.request.use((config) => {
    const token = getAuthToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        logout()
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
  )

  return api
} 