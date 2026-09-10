import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import api from '../services/api'

interface AuthContextValue {
  token: string | null
  user: any | null
  loading: boolean
  login: (token: string) => void
  logout: () => void
  fetchProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('expertverse_token'))
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const login = (newToken: string) => {
    localStorage.setItem('expertverse_token', newToken)
    setToken(newToken)
  }

  const logout = () => {
    localStorage.removeItem('expertverse_token')
    setToken(null)
    setUser(null)
  }

  const fetchProfile = async () => {
    if (!token) return
    setLoading(true)
    try {
      const response = await api.get('/auth/profile')
      setUser(response.data)
    } catch (error) {
      logout()
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (token) {
      fetchProfile()
    }
  }, [token])

  const value = useMemo(
    () => ({ token, user, loading, login, logout, fetchProfile }),
    [token, user, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
