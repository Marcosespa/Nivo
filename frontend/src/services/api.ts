import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// Request interceptor: attach Authorization token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('nivo_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle 401 and extract error messages
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('nivo_token')
      // Use location instead of router to avoid circular dependency
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    // Extract a human-readable error message
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'Ocurrió un error inesperado'

    return Promise.reject(new Error(message))
  }
)

export default api
