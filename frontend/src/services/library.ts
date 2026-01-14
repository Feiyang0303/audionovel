import { createAuthenticatedApi } from './auth'

const api = createAuthenticatedApi()

export interface LibraryItem {
  _id: string
  user_id: string
  file_id: string
  title: string
  description: string
  tags: string[]
  is_favorite: boolean
  created_at: string
  updated_at: string
  file?: {
    _id: string
    filename: string
    original_filename: string
    file_type: string
    file_size: number
    upload_date: string
    status: string
    target_age_group: string
  }
  processing?: {
    _id: string
    status: string
    simplified_text: string
    characters: Array<{
      name: string
      dialogue_count: number
    }>
    expert_analyses: Record<string, string>
    processing_date: string
  }
}

export interface AddToLibraryData {
  file_id: string
  title?: string
  description?: string
  tags?: string[]
  is_favorite?: boolean
}

export interface UpdateLibraryData {
  title?: string
  description?: string
  tags?: string[]
  is_favorite?: boolean
}

export interface LibraryStats {
  total_items: number
  pdf_items: number
  txt_items: number
  recent_items: number
}

// Library functions
export const getUserLibrary = async (): Promise<{ library: LibraryItem[]; count: number }> => {
  const response = await api.get('/api/library')
  return response.data
}

export const getLibraryItem = async (itemId: string): Promise<{ item: LibraryItem }> => {
  const response = await api.get(`/api/library/${itemId}`)
  return response.data
}

export const addToLibrary = async (data: AddToLibraryData): Promise<{ message: string; item_id: string }> => {
  const response = await api.post('/api/library', data)
  return response.data
}

export const updateLibraryItem = async (itemId: string, data: UpdateLibraryData): Promise<{ message: string }> => {
  const response = await api.put(`/api/library/${itemId}`, data)
  return response.data
}

export const removeFromLibrary = async (itemId: string): Promise<{ message: string }> => {
  const response = await api.delete(`/api/library/${itemId}`)
  return response.data
}

export const getLibraryStats = async (): Promise<{ stats: LibraryStats }> => {
  const response = await api.get('/api/library/stats')
  return response.data
}

export const searchLibrary = async (query: string): Promise<{ results: LibraryItem[]; count: number; query: string }> => {
  const response = await api.get(`/api/library/search?q=${encodeURIComponent(query)}`)
  return response.data
}

export const getFavorites = async (): Promise<{ favorites: LibraryItem[]; count: number }> => {
  const response = await api.get('/api/library/favorites')
  return response.data
}

export const toggleFavorite = async (itemId: string): Promise<{ message: string; is_favorite: boolean }> => {
  const response = await api.post(`/api/library/${itemId}/favorite`)
  return response.data
}

// Utility functions
export const saveProcessedFileToLibrary = async (
  fileId: string, 
  title?: string, 
  description?: string
): Promise<{ message: string; item_id: string }> => {
  return addToLibrary({
    file_id: fileId,
    title: title,
    description: description,
    is_favorite: false
  })
}

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

export const getFileTypeIcon = (fileType: string): string => {
  switch (fileType.toLowerCase()) {
    case 'pdf':
      return '📄'
    case 'txt':
      return '📝'
    case 'epub':
      return '📚'
    default:
      return '📄'
  }
} 