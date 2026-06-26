import api from './api'

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
  role: string
}

export const login = async (payload: LoginPayload) => {
  const response = await api.post('/auth/login', new URLSearchParams({
    username: payload.username,
    password: payload.password,
  }))
  return response.data
}

export const register = async (payload: RegisterPayload) => {
  const response = await api.post('/auth/register', payload)
  return response.data
}
