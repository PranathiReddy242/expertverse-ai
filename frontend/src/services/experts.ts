import api from './api'

export const getExperts = async (query?: string, allStatuses: boolean = false) => {
  const params: any = {}
  if (query) params.q = query
  if (allStatuses) params.all_statuses = true
  const response = await api.get('/experts/list', { params })
  return response.data
}

export const getExpertDetails = async (id: string | number) => {
  const response = await api.get(`/experts/details/${id}`)
  return response.data
}

export const submitVerification = async (data: {
  certificate_url?: string
  resume_url?: string
  linkedin_url?: string
  experience_years?: number
  notes?: string
}) => {
  const response = await api.post('/experts/submit-verification', data)
  return response.data
}

export const getMyVerification = async () => {
  const response = await api.get('/experts/my-verification')
  return response.data
}
