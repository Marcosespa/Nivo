import api from './api'

export const healthService = {
  async root() {
    const { data } = await api.get('/')
    return data
  },
  async health() {
    const { data } = await api.get('/health')
    return data
  },
  async pqc() {
    const { data } = await api.get('/health/pqc')
    return data
  },
  async ready() {
    const { data } = await api.get('/health/ready')
    return data
  },
  async live() {
    const { data } = await api.get('/health/live')
    return data
  },
}
