import { useState, useEffect, useCallback } from 'react'
import { getProfile, getCurrentUser } from '../services/auth'
import { useAuth } from '../contexts/AuthContext'
import { getUserLibrary, removeFromLibrary, setLibraryItemFavorite, formatDate, formatFileSize, getFileTypeIcon } from '../services/library'
import { generateAudioFromScript } from '../services/audio'
import { AudioPlayer } from '../components/AudioPlayer'
import type { User } from '../services/auth'
import type { LibraryItem, LibraryStats } from '../services/library'
import { useNavigate } from 'react-router-dom'

// Known-good ElevenLabs voice ("George") that works with restricted keys.
// Override with ELEVENLABS_DEFAULT_VOICE_ID on the backend if you want a different one.
const DEFAULT_VOICE_ID = 'JBFqnCBsd6RMkjVDRZzb'

export function Profile() {
  const [user, setUser] = useState<User | null>(null)
  const [libraryStats, setLibraryStats] = useState<LibraryStats | null>(null)
  const [library, setLibrary] = useState<LibraryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [audioFiles, setAudioFiles] = useState<Record<string, string>>({})
  const [audioLoading, setAudioLoading] = useState<Record<string, boolean>>({})
  const [audioErrors, setAudioErrors] = useState<Record<string, string>>({})
  const navigate = useNavigate()
  const { logout, syncSessionUser } = useAuth()

  const loadProfile = useCallback(async () => {
    try {
      setLoading(true)
      const [profileData, libraryData] = await Promise.all([
        getProfile(),
        getUserLibrary()
      ])

      const serverUser = profileData.user as User
      setUser(serverUser)
      syncSessionUser(serverUser)
      setLibraryStats(profileData.library_stats as LibraryStats)
      setLibrary(libraryData.items)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load profile')
      if (err.response?.status === 401) {
        navigate('/login')
      }
    } finally {
      setLoading(false)
    }
  }, [navigate, syncSessionUser])

  useEffect(() => {
    const currentUser = getCurrentUser()
    if (!currentUser) {
      navigate('/login')
      return
    }

    setUser(currentUser)
    void loadProfile()
  }, [navigate, loadProfile])

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const handleRemoveFromLibrary = async (itemId: string) => {
    try {
      await removeFromLibrary(itemId)
      setLibrary(library.filter(item => item._id !== itemId))
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to remove item')
    }
  }

  const handleGenerateAudio = async (item: LibraryItem) => {
    const script = item.processing?.simplified_text?.trim()
    if (!script) {
      setAudioErrors((m) => ({ ...m, [item._id]: 'No simplified script available for this item yet.' }))
      return
    }
    setAudioErrors((m) => ({ ...m, [item._id]: '' }))
    setAudioLoading((m) => ({ ...m, [item._id]: true }))
    try {
      const { audio_file } = await generateAudioFromScript({
        script,
        voice_map: {},
        default_voice_id: DEFAULT_VOICE_ID,
      })
      setAudioFiles((m) => ({ ...m, [item._id]: audio_file }))
    } catch (err: any) {
      const msg =
        err.response?.data?.error ||
        err.message ||
        'Failed to generate audio'
      setAudioErrors((m) => ({ ...m, [item._id]: msg }))
    } finally {
      setAudioLoading((m) => ({ ...m, [item._id]: false }))
    }
  }

  const handleToggleFavorite = async (itemId: string) => {
    const item = library.find((i) => i._id === itemId)
    if (!item) return
    try {
      const result = await setLibraryItemFavorite(itemId, !item.is_favorite)
      setLibrary(library.map((i) =>
        i._id === itemId ? { ...i, ...result.item, is_favorite: result.item.is_favorite } : i
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

  const displayName = (user.name || '').trim() || user.username || 'Your account'
  const avatarSrc =
    user.profile_pic ||
    `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=6366f1&color=fff`

  return (
    <div className="max-w-3xl mx-auto pt-32 px-4 sm:px-6 lg:px-8">
      <div className="bg-white shadow sm:rounded-lg">
        {/* Profile Section — same fields as login/register API user object */}
        <div className="px-6 py-8 sm:p-8 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <img
                src={avatarSrc}
                alt={displayName}
                className="h-24 w-24 rounded-full border-2 border-indigo-100"
              />
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{displayName}</h2>
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
          {libraryStats && (
            <div className="mt-6 flex flex-wrap gap-4 text-sm text-gray-600">
              <span className="rounded-md bg-indigo-50 px-3 py-1 text-indigo-800">
                {libraryStats.total_items} item{libraryStats.total_items !== 1 ? 's' : ''} in library
              </span>
              <span>PDF: {libraryStats.pdf_items}</span>
              <span>Text: {libraryStats.txt_items}</span>
              <span>Added last 30 days: {libraryStats.recent_items}</span>
            </div>
          )}
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
              {library.map((item) => {
                const hasScript = !!item.processing?.simplified_text?.trim()
                const isGenerating = !!audioLoading[item._id]
                const audioFile = audioFiles[item._id]
                const audioError = audioErrors[item._id]
                return (
                  <div
                    key={item._id}
                    className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
                  >
                    <div className="flex items-center justify-between">
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
                          onClick={() => handleGenerateAudio(item)}
                          disabled={!hasScript || isGenerating}
                          title={hasScript ? 'Generate audio with ElevenLabs' : 'No simplified script available yet'}
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                        >
                          {isGenerating ? (
                            <>
                              <svg className="animate-spin h-4 w-4 mr-1" viewBox="0 0 24 24" fill="none">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                              </svg>
                              Generating…
                            </>
                          ) : audioFile ? 'Regenerate audio' : 'Generate audio'}
                        </button>
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
                    {audioError && (
                      <p className="mt-3 text-sm text-red-600">{audioError}</p>
                    )}
                    {audioFile && (
                      <div className="mt-4">
                        <AudioPlayer audioFile={audioFile} title={item.title} />
                      </div>
                    )}
                  </div>
                )
              })}
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