import api from './api'
import { useAuthStore } from '../store/authStore'

function apiKeyHeader() {
  const apiKey = useAuthStore.getState().apiKey
  return apiKey ? { 'X-Nivo-Key': apiKey } : {}
}

export const cryptoService = {
  async algorithms() {
    const { data } = await api.get('/api/v1/crypto/algorithms', {
      headers: apiKeyHeader(),
    })
    return data
  },

  async sign(data_hex: string) {
    const { data } = await api.post(
      '/api/v1/crypto/sign',
      { data_hex },
      { headers: apiKeyHeader() }
    )
    return data
  },

  async verify(payload: {
    data_hex: string
    signature_hex: string
    public_key_hex: string
  }) {
    const { data } = await api.post('/api/v1/crypto/verify', payload, {
      headers: apiKeyHeader(),
    })
    return data
  },
}
