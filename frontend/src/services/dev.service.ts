import api from './api'

export const devService = {
  async seed(payload: {
    sender_phone: string
    receiver_phone: string
    seed_balance_cop: number
  }) {
    const { data } = await api.post('/api/v1/dev/seed', payload)
    return data
  },

  async clearSeed(payload: {
    sender_phone: string
    receiver_phone: string
    seed_balance_cop: number
  }) {
    const { data } = await api.delete('/api/v1/dev/seed', { data: payload })
    return data
  },
}
