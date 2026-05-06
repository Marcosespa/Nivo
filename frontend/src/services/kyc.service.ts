import api from './api'

export const kycService = {
  async initiate() {
    const { data } = await api.post('/api/v1/kyc/initiate')
    return data
  },

  async status() {
    const { data } = await api.get('/api/v1/kyc/status')
    return data
  },
}
