import api from './api'

export const paymentsService = {
  async initiate(payload: {
    receiver_phone: string
    amount_cop: number
    message?: string
  }) {
    const { data } = await api.post('/api/v1/payments/initiate', payload)
    return data
  },

  async confirm(payload: { tx_id: string; otp_code: string }) {
    const { data } = await api.post('/api/v1/payments/confirm', payload)
    return data
  },

  async history(query: { page: number; page_size: number; direction: string }) {
    const { data } = await api.get('/api/v1/payments/history', { params: query })
    return data
  },

  async detail(txId: string) {
    const { data } = await api.get(`/api/v1/payments/${txId}`)
    return data
  },
}
