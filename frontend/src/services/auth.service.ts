import api from './api'
import type { User } from '../types'

export const authService = {
  async requestOtp(phone: string): Promise<{ message: string }> {
    const { data } = await api.post('/api/v1/auth/request-otp', { phone })
    return data
  },

  async verifyOtp(
    phone: string,
    otp: string
  ): Promise<{ access_token: string; user: User }> {
    const { data } = await api.post('/api/v1/auth/verify-otp', { phone, otp })
    return data
  },

  async getProfile(): Promise<User> {
    const { data } = await api.get('/api/v1/users/me')
    return data
  },
}
