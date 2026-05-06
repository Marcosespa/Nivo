import axios, { AxiosError } from 'axios'
import { useAuthStore } from '../store/authStore'

export class ApiRequestError extends Error {
  status: number
  payload: unknown

  constructor(message: string, status: number, payload: unknown) {
    super(message)
    this.name = 'ApiRequestError'
    this.status = status
    this.payload = payload
  }
}

const api = axios.create({
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const { baseUrl, accessToken } = useAuthStore.getState()
  config.baseURL = baseUrl || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

  if (accessToken && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status ?? 500
    const payload = error.response?.data ?? { detail: error.message }

    const message =
      (typeof payload === 'object' &&
        payload !== null &&
        'detail' in payload &&
        typeof payload.detail === 'string' &&
        payload.detail) ||
      error.message ||
      'Ocurrio un error inesperado'

    return Promise.reject(new ApiRequestError(message, status, payload))
  }
)

export default api
