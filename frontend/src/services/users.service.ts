import api from './api'

export const usersService = {
  async me() {
    const { data } = await api.get('/api/v1/users/me')
    return data
  },

  async wallet() {
    const { data } = await api.get('/api/v1/users/me/wallet')
    return data
  },
}
