import api from './api'
import type { Wallet, Transaction } from '../types'

export const walletService = {
  async getWallet(): Promise<Wallet> {
    const { data } = await api.get('/api/v1/users/me/wallet')
    return data
  },

  async getTransactions(): Promise<Transaction[]> {
    const { data } = await api.get('/api/v1/payments/history')
    return data
  },

  async topUp(amount: number): Promise<{ message: string; transaction_id: string }> {
    const { data } = await api.post('/api/v1/topup', { amount })
    return data
  },

  async withdraw(
    amount: number,
    bank_account_id: string
  ): Promise<{ message: string; transaction_id: string }> {
    const { data } = await api.post('/api/v1/withdrawal', { amount, bank_account_id })
    return data
  },
}
