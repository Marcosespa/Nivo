import api from './api'

export const topupService = {
  async initiate(payload: { amount_cop: number; bank_code: string }) {
    const { data } = await api.post('/api/v1/topup/initiate', payload)
    return data
  },

  async history(limit: number) {
    const { data } = await api.get('/api/v1/topup/history', { params: { limit } })
    return data
  },
}
