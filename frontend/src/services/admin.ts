import api from './api'

export interface AdminSummary {
  users: number
  experts: number
  pending_experts: number
  approved_experts: number
  rejected_experts: number
  bookings: number
  pending_bookings: number
  completed_bookings: number
  paid_bookings: number
  total_revenue: number
  pending_documents: number
}

export const getAdminSummary = async (): Promise<AdminSummary> => {
  const response = await api.get('/admin/summary')
  return response.data
}

export const getAdminUsers = async () => {
  const response = await api.get('/admin/users')
  return response.data
}

export const getAdminExperts = async () => {
  const response = await api.get('/admin/experts')
  return response.data
}

export const getAdminBookings = async () => {
  const response = await api.get('/admin/bookings')
  return response.data
}

export const getPendingVerifications = async () => {
  const response = await api.get('/admin/pending-verifications')
  return response.data
}

export const approveExpert = async (expertId: number) => {
  const response = await api.post(`/admin/experts/${expertId}/approve`)
  return response.data
}

export const rejectExpert = async (expertId: number, reason: string) => {
  const response = await api.post(`/admin/experts/${expertId}/reject`, { reason })
  return response.data
}

export const reviewDocument = async (documentId: number, status: 'approved' | 'rejected', reviewNotes?: string) => {
  const response = await api.post(`/admin/documents/${documentId}/review`, {
    status,
    review_notes: reviewNotes,
  })
  return response.data
}

export const askAdminAI = async (query: string) => {
  const response = await api.post('/admin/ai-assistant', { query })
  return response.data
}
