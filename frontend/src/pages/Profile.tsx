import { useState, useEffect } from 'react'
import { getProfile, logout, getCurrentUser } from '../services/auth'
import { getUserLibrary, removeFromLibrary, toggleFavorite, formatDate, formatFileSize, getFileTypeIcon } from '../services/library'
import type { User } from '../services/auth'
import type { LibraryItem } from '../services/library'
import { useNavigate } from 'react-router-dom'

export function Profile() {
  const [user, setUser] = useState<User | null>(null)
  const [library, setLibrary] = useState<LibraryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const currentUser = getCurrentUser()
    if (!currentUser) {
      navigate('/login')
      return
    }

    setUser(currentUser)
    loadProfile()
  }, [navigate])

  const loadProfile = async () => {
    try {
      setLoading(true)
      const [profileData, libraryData] = await Promise.all([
        getProfile(),
        getUserLibrary()
      ])
      
      setUser(profileData.user)
      setLibrary(libraryData.library)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load profile')
      if (err.response?.status === 401) {
        navigate('/login')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleRemoveFromLibrary = async (itemId: string) => {
    try {
      await removeFromLibrary(itemId)
      setLibrary(library.filter(item => item._id !== itemId))
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to remove item')
    }
  }

  const handleToggleFavorite = async (itemId: string) => {
    try {
      const result = await toggleFavorite(itemId)
      setLibrary(library.map(item => 
        item._id === itemId 
          ? { ...item, is_favorite: result.is_favorite }
          : item
      ))
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update favorite')
    }
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto pt-32 px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow sm:rounded-lg p-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading profile...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="max-w-3xl mx-auto pt-32 px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow sm:rounded-lg p-8">
          <div className="text-center">
            <p className="text-gray-600">Please log in to view your profile.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto pt-32 px-4 sm:px-6 lg:px-8">
      <div className="bg-white shadow sm:rounded-lg">
        {/* Profile Section */}
        <div className="px-6 py-8 sm:p-8 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <img
                src={user.profile_pic}
                alt={user.name}
                className="h-24 w-24 rounded-full border-2 border-indigo-100"
              />
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{user.name}</h2>
                <p className="text-lg text-gray-600">{user.email}</p>
                <p className="text-sm text-gray-500">@{user.username}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="px-6 py-4 bg-red-50 border-b border-red-200">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Library Section */}
        <div className="px-6 py-8 sm:p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">My Library</h3>
          {library.length > 0 ? (
            <div className="space-y-4">
              {library.map((item) => (
                <div
                  key={item._id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
                >
                  <div className="flex items-center space-x-4">
                    <span className="text-2xl">{getFileTypeIcon(item.file?.file_type || 'txt')}</span>
                    <div>
                      <h4 className="text-lg font-medium text-gray-900">{item.title}</h4>
                      <p className="text-sm text-gray-500">
                        {item.file?.original_filename} • {formatDate(item.created_at)}
                      </p>
                      {item.file && (
                        <p className="text-xs text-gray-400">
                          {formatFileSize(item.file.file_size)} • {item.file.file_type.toUpperCase()}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleToggleFavorite(item._id)}
                      className={`p-2 rounded-full ${
                        item.is_favorite 
                          ? 'text-red-500 hover:text-red-700' 
                          : 'text-gray-400 hover:text-red-500'
                      }`}
                    >
                      <svg className="w-5 h-5" fill={item.is_favorite ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleRemoveFromLibrary(item._id)}
                      className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No books in your library yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Upload and process a book, then save it to your library to get started.
              </p>
              <div className="mt-6">
                <a
                  href="/"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Upload a Book
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 