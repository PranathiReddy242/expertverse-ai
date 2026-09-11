import axios from 'axios'

const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
const defaultBaseUrl = isLocal ? 'http://localhost:8000' : ''

const api = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_BASE_URL || defaultBaseUrl,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('expertverse_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
