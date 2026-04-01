import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

export const uploadPDF = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Upload failed')
  }
}

export const getTaskStatus = async (taskId) => {
  try {
    const response = await apiClient.get(`/api/v1/task/${taskId}`)
    return response.data
  } catch (error) {
    console.error('Error fetching task status:', error)
    throw error
  }
}

export const getDocumentParagraphs = async (bookId) => {
  try {
    const response = await apiClient.get(`/api/v1/documents/${bookId}`)
    return response.data
  } catch (error) {
    console.error('Error fetching document:', error)
    throw error
  }
}

export const searchDocuments = async (bookId, query) => {
  try {
    const response = await apiClient.get(`/api/v1/documents/${bookId}/search`, {
      params: { q: query }
    })
    return response.data
  } catch (error) {
    console.error('Error searching documents:', error)
    throw error
  }
}

export default apiClient
