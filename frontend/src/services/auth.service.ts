import api from './api'

export const authService = {
  async requestOtp(phone_number: string) {
    const { data } = await api.post('/api/v1/auth/request-otp', { phone_number })
    return data
  },

  async verifyOtp(payload: {
    phone_number: string
    otp_code: string
    device_id: string
  }) {
    const { data } = await api.post('/api/v1/auth/verify-otp', payload)
    return data
  },

  async refresh(refresh_token: string) {
    const { data } = await api.post('/api/v1/auth/refresh', { refresh_token })
    return data
  },

  async logout(refresh_token: string) {
    const { data } = await api.post('/api/v1/auth/logout', { refresh_token })
    return data
  },
}
