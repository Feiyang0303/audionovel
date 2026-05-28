import {
  useState,
  useEffect,
  useCallback,
  createContext,
  useContext,
  type ReactNode,
} from 'react'
import {
  getCurrentUser,
  getAuthToken,
  logout as clearServerSession,
} from '../services/auth'
import type { User } from '../services/auth'

export interface AuthContextType {
  user: User | null
  token: string | null
  /** After login or register — sets user + token + localStorage */
  login: (userData: User, authToken: string) => void
  /** After GET /api/users/me or profile PATCH — keeps token, aligns context + localStorage with server */
  syncSessionUser: (userData: User) => void
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

function parseStoredUser(): User | null {
  const raw = getCurrentUser()
  if (!raw || typeof raw !== 'object') return null
  return raw as User
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = getAuthToken()
        const storedUser = parseStoredUser()
        if (storedToken && storedUser?._id) {
          setToken(storedToken)
          setUser(storedUser)
        }
      } catch (error) {
        console.error('Auth initialization error:', error)
      } finally {
        setLoading(false)
      }
    }
    initializeAuth()
  }, [])

  const login = useCallback((userData: User, authToken: string) => {
    setUser(userData)
    setToken(authToken)
    localStorage.setItem('authToken', authToken)
    localStorage.setItem('user', JSON.stringify(userData))
  }, [])

  const syncSessionUser = useCallback((userData: User) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }, [])

  const logout = () => {
    void clearServerSession()
    setUser(null)
    setToken(null)
  }

  const value: AuthContextType = {
    user,
    token,
    login,
    syncSessionUser,
    logout,
    isAuthenticated: !!user && !!token,
  }

  return (
    <AuthContext.Provider value={value}>
      {loading ? (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600" />
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  )
}
