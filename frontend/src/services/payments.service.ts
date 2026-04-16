import api from './api'
import type { Transaction } from '../types'

export const paymentsService = {
  async sendPayment(
    recipient_phone: string,
    amount: number,
    description?: string
  ): Promise<Transaction> {
    const { data } = await api.post('/api/v1/payments/send', {
      recipient_phone,
      amount,
      description,
    })
    return data
  },

  async getHistory(): Promise<Transaction[]> {
    const { data } = await api.get('/api/v1/payments/history')
    return data
  },
}
