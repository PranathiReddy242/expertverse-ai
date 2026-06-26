import api from './api'

export const getExperts = async () => {
  const response = await api.get('/experts/list')
  return response.data
}

export const getExpertDetails = async (id: string) => {
  const response = await api.get(`/experts/details/${id}`)
  return response.data
}
