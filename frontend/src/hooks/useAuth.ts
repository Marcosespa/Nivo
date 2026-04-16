import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authService } from '../services/auth.service'

export function useAuth() {
  const { token, user, isAuthenticated, login, logout } = useAuthStore()
  const navigate = useNavigate()

  /**
   * Verifies the stored token is still valid by hitting /users/me.
   * Logs out and redirects to /login on failure.
   */
  const checkAuth = useCallback(async (): Promise<boolean> => {
    if (!token) {
      logout()
      navigate('/login', { replace: true })
      return false
    }

    try {
      const profile = await authService.getProfile()
      // Update user data in the store with fresh data
      login(token, profile)
      return true
    } catch {
      logout()
      navigate('/login', { replace: true })
      return false
    }
  }, [token, login, logout, navigate])

  const handleLogout = useCallback(() => {
    logout()
    navigate('/login', { replace: true })
  }, [logout, navigate])

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout: handleLogout,
    checkAuth,
  }
}
