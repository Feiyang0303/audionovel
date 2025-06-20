import axios from 'axios'

const API_BASE_URL = 'http://localhost:5001'

const api = axios.create({
  baseURL: API_BASE_URL,
  // Remove default headers to allow Content-Type to be set per request
})

export interface UploadResponse {
  status: string
  message: string
  file_path: string
  filename: string
  analysis: {
    status: string
    target_age_group: string
    simplified_text: string
    characters: Array<{
      name: string
      dialogue_count: number
      first_appearance: number
      sample_dialogue: string
    }>
    // Add other analysis fields as needed
  }
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