import api from './api'

export const withdrawalService = {
  async registerAccount(payload: {
    bank_code: string
    account_type: string
    account_number: string
    account_holder_name: string
  }) {
    const { data } = await api.post('/api/v1/withdrawal/accounts', payload)
    return data
  },

  async listAccounts() {
    const { data } = await api.get('/api/v1/withdrawal/accounts')
    return data
  },

  async verifyAccount(accountId: string, verification_amount_cop: number) {
    const { data } = await api.post(`/api/v1/withdrawal/accounts/${accountId}/verify`, {
      verification_amount_cop,
    })
    return data
  },

  async initiate(payload: { bank_account_id: string; amount_cop: number }) {
    const { data } = await api.post('/api/v1/withdrawal/initiate', payload)
    return data
  },

  async history(limit: number) {
    const { data } = await api.get('/api/v1/withdrawal/history', { params: { limit } })
    return data
  },
}
