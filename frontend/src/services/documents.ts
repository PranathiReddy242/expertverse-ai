import api from './api'

export interface DocumentSearchMatch {
  text: string
  score: number
  expert_id: number
  expert_name: string
  expert_title?: string
  file_type: string
}

export const searchDocuments = async (query: string, topK: number = 5) => {
  const response = await api.post('/documents/search', {
    query,
    top_k: topK,
  })
  return response.data
}

export const ragChatWithDocuments = async (query: string, expertId?: number) => {
  const response = await api.post('/documents/rag-chat', {
    query,
    expert_id: expertId,
  })
  return response.data
}
