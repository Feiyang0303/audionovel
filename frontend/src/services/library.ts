import { api } from './auth'

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

export const getUserLibrary = async (): Promise<{
  items: LibraryItem[]
  count: number
}> => {
  const response = await api.get('/api/library/items')
  return response.data
}

export const getLibraryItem = async (
  itemId: string
): Promise<{ item: LibraryItem }> => {
  const response = await api.get(`/api/library/items/${itemId}`)
  return response.data
}

export const addToLibrary = async (
  data: AddToLibraryData
): Promise<{ message: string; item_id: string }> => {
  const response = await api.post('/api/library/items', data)
  return response.data
}

export const updateLibraryItem = async (
  itemId: string,
  data: UpdateLibraryData
): Promise<{ message: string; item: LibraryItem }> => {
  const response = await api.patch(`/api/library/items/${itemId}`, data)
  return response.data
}

export const removeFromLibrary = async (itemId: string): Promise<void> => {
  await api.delete(`/api/library/items/${itemId}`)
}

export const getLibraryStats = async (): Promise<{ stats: LibraryStats }> => {
  const response = await api.get('/api/library/statistics')
  return response.data
}

export const searchLibrary = async (
  query: string
): Promise<{ items: LibraryItem[]; count: number }> => {
  const response = await api.get('/api/library/items', {
    params: { q: query },
  })
  return response.data
}

export const getFavorites = async (): Promise<{
  items: LibraryItem[]
  count: number
}> => {
  const response = await api.get('/api/library/items', {
    params: { is_favorite: 'true' },
  })
  return response.data
}

/** Set favorite explicitly (RESTful replacement for toggle RPC). */
export const setLibraryItemFavorite = async (
  itemId: string,
  is_favorite: boolean
): Promise<{ message: string; item: LibraryItem }> => {
  return updateLibraryItem(itemId, { is_favorite })
}

export const saveProcessedFileToLibrary = async (
  fileId: string,
  title?: string,
  description?: string
): Promise<{ message: string; item_id: string }> => {
  return addToLibrary({
    file_id: fileId,
    title: title,
    description: description,
    is_favorite: false,
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
    day: 'numeric',
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
