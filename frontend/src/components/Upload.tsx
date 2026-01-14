import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadBook, getStatus } from '../services/api'
import { addToLibrary } from '../services/library'
import { useAuth } from '../App'
import type { UploadResponse } from '../services/api'

const PROCESSING_STAGES = [
  { name: 'Starting upload', progress: 5 },
  { name: 'Uploading file', progress: 15 },
  { name: 'Subject Research', progress: 25 },
  { name: 'Subject Review', progress: 35 },
  { name: 'Case Analysis', progress: 45 },
  { name: 'Argument Analysis', progress: 55 },
  { name: 'Development Analysis', progress: 65 },
  { name: 'Content Aggregation', progress: 75 },
  { name: 'Content Moderation', progress: 85 },
  { name: 'Language Analysis', progress: 95 },
  { name: 'Final Review', progress: 100 },
]

export function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState<string>('')
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<UploadResponse['analysis'] | null>(null)
  const [livePreview, setLivePreview] = useState<string | null>(null)
  const [isSavingToLibrary, setIsSavingToLibrary] = useState(false)
  const [savedToLibrary, setSavedToLibrary] = useState(false)
  const [currentFilename, setCurrentFilename] = useState<string | null>(null)
  const [currentFileId, setCurrentFileId] = useState<string | null>(null)
  const navigate = useNavigate()
  const pollingRef = useRef<NodeJS.Timeout | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [])

  const pollStatus = async (filename: string) => {
    try {
      const poll = async () => {
        const status = await getStatus(filename)
        const steps = status.processing_steps || []
        const totalSteps = 10 // Number of expert roles
        let completedSteps = 0
        let lastCompletedRole = ''
        steps.forEach((step: any) => {
          if (step.status === 'completed') {
            completedSteps++
            lastCompletedRole = step.role
          }
        })
        const progress = totalSteps > 0 ? 5 + Math.round((completedSteps / totalSteps) * 95) : 100
        setUploadProgress(progress)
        setCurrentStage(lastCompletedRole ? `Completed: ${lastCompletedRole}` : 'Processing...')
        if (status.status === 'completed') {
          // Stop polling
          if (pollingRef.current) clearInterval(pollingRef.current)
          setUploadProgress(100)
          setCurrentStage('Processing complete!')
          setAnalysis(status.analysis)
          setCurrentFilename(filename)
          if (status.file_id) {
            setCurrentFileId(status.file_id)
          }
          // navigate(`/book/${filename}`, { state: { analysis: status.analysis } })
        }
        if (!currentFileId && status.file_id) {
          setCurrentFileId(status.file_id)
        }
        if (status.analysis && status.analysis.simplified_text) {
          setLivePreview(status.analysis.simplified_text)
        }
      }
      pollingRef.current = setInterval(poll, 2000)
      // Run immediately for instant feedback
      poll()
    } catch (err) {
      setError('Failed to poll status')
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      setFile(event.dataTransfer.files[0])
      setError(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)
    setError(null)
    setAnalysis(null)
    setCurrentStage('Starting upload...')

    try {
      setUploadProgress(5)
      setCurrentStage('Uploading file...')
      const response = await uploadBook(file)
      // Start polling for status updates
      pollStatus(response.filename)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      setUploadProgress(0)
      setCurrentStage('')
    } finally {
      setIsUploading(false)
    }
  }

  const handleSaveToLibrary = async () => {
    if (!isAuthenticated) {
      setError('Please login to save to library')
      return
    }

    if (!analysis || !currentFileId) {
      setError('No processed content to save (missing file id)')
      return
    }

    setIsSavingToLibrary(true)
    setError(null)

    try {
      await addToLibrary({
        file_id: currentFileId,
        title: file?.name || 'Untitled Book',
        description: 'Processed with AudioNovel - Simplified text available'
      })
      
      setSavedToLibrary(true)
      setTimeout(() => setSavedToLibrary(false), 3000) // Reset after 3 seconds
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save to library')
    } finally {
      setIsSavingToLibrary(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto pt-32 px-4 sm:px-6 lg:px-8">
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-6 py-8 sm:p-8">
          <h3 className="text-2xl font-medium leading-6 text-gray-900 mb-4">
            Upload Your Book
          </h3>
          <div className="mt-4 max-w-2xl text-lg text-gray-500">
            <p>Upload your children's book in PDF or TXT format. EPUB and MOBI support coming soon!</p>
          </div>
          
          <div className="mt-8">
            <div
              className="flex items-center justify-center w-full"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <label
                className="flex flex-col items-center justify-center w-full h-40 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
                onClick={() => fileInputRef.current?.click()}
                htmlFor="file-upload"
              >
                <div className="flex flex-col items-center justify-center pt-6 pb-8">
                  <svg className="w-12 h-12 mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="mb-2 text-base text-gray-500">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-sm text-gray-500">PDF, TXT, EPUB, or MOBI</p>
                </div>
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  accept=".pdf,.txt,.epub,.mobi"
                  onChange={handleFileChange}
                  disabled={isUploading}
                  ref={fileInputRef}
                />
              </label>
            </div>

            {file && (
              <div className="mt-6 text-base text-gray-600">
                Selected file: {file.name}
              </div>
            )}

            {error && (
              <div className="mt-6 text-base text-red-600">
                {error}
              </div>
            )}

            {(isUploading || uploadProgress > 0) && (
              <div className="mt-6">
                <div className="relative pt-1">
                  <div className="flex mb-3 items-center justify-between">
                    <div>
                      <span className="text-sm font-semibold inline-block py-1 px-3 uppercase rounded-full text-indigo-600 bg-indigo-200">
                        {currentStage}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-semibold inline-block text-indigo-600">
                        {uploadProgress}%
                      </span>
                    </div>
                  </div>
                  <div className="overflow-hidden h-3 mb-4 text-xs flex rounded bg-indigo-200">
                    <div
                      style={{ width: `${uploadProgress}%` }}
                      className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500 transition-all duration-500"
                    ></div>
                  </div>
                  {uploadProgress < 100 && (
                    <p className="text-sm text-gray-500 mt-2">
                      This may take a few minutes as we analyze your text through multiple expert roles...
                    </p>
                  )}
                </div>
              </div>
            )}

            <div className="mt-8">
              <button
                type="button"
                onClick={handleUpload}
                disabled={!file || isUploading}
                className={`inline-flex items-center px-6 py-3 text-base font-medium rounded-md shadow-sm text-white 
                  ${!file || isUploading 
                    ? 'bg-indigo-300 cursor-not-allowed' 
                    : 'bg-indigo-600 hover:bg-indigo-700'}`}
              >
                {isUploading ? 'Uploading...' : 'Upload Book'}
              </button>
            </div>
          </div>

          {/* Script Preview Box */}
          {analysis && analysis.simplified_text ? (
            <div className="mt-8 p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-lg font-medium text-gray-900">Script Preview</h4>
                {isAuthenticated && (
                  <button
                    onClick={handleSaveToLibrary}
                    disabled={isSavingToLibrary || savedToLibrary}
                    className={`inline-flex items-center px-4 py-2 text-sm font-medium rounded-md shadow-sm text-white 
                      ${isSavingToLibrary || savedToLibrary
                        ? 'bg-green-400 cursor-not-allowed' 
                        : 'bg-green-600 hover:bg-green-700'}`}
                  >
                    {isSavingToLibrary ? 'Saving...' : savedToLibrary ? 'Saved!' : 'Save to Library'}
                  </button>
                )}
              </div>
              <div className="prose max-w-none">
                <div className="text-gray-600 whitespace-pre-wrap">
                  {analysis.simplified_text}
                </div>
              </div>
              {!isAuthenticated && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <p className="text-sm text-blue-700">
                    💡 <strong>Want to save this to your library?</strong> Please{' '}
                    <button 
                      onClick={() => navigate('/login')}
                      className="text-blue-600 hover:text-blue-800 underline font-medium"
                    >
                      login
                    </button>{' '}
                    or{' '}
                    <button 
                      onClick={() => navigate('/register')}
                      className="text-blue-600 hover:text-blue-800 underline font-medium"
                    >
                      sign up
                    </button>{' '}
                    to save your processed books.
                  </p>
                </div>
              )}
            </div>
          ) : livePreview ? (
            <div className="mt-8 p-4 bg-gray-50 rounded-lg">
              <h4 className="text-lg font-medium text-gray-900 mb-4">Script Preview (Live)</h4>
              <div className="prose max-w-none">
                <div className="text-gray-600 whitespace-pre-wrap">
                  {livePreview}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
} 