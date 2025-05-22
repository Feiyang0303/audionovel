import axios from 'axios'

const API_BASE_URL = 'http://localhost:5001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface UploadResponse {
  status: string
  message: string
  file_path: string
  filename: string
}

export interface SimplifyResponse {
  simplified_story: string
}

export interface AudiobookResponse {
  message: string
  audio_files: string[]
}

export const uploadBook = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const simplifyText = async (text: string): Promise<SimplifyResponse> => {
  const response = await api.post<SimplifyResponse>('/simplify', { text })
  return response.data
}

export const generateAudiobook = async (text: string): Promise<AudiobookResponse> => {
  const response = await api.post<AudiobookResponse>('/generate-audiobook', { text })
  return response.data
}

export const getFileUrl = (filename: string) => `${API_BASE_URL}/files/${filename}`
export const getAudioUrl = (filename: string) => `${API_BASE_URL}/audio/${filename}` 