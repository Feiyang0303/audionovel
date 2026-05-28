import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { uploadBook, getStatus } from '../services/api'
import { addToLibrary } from '../services/library'
import { useAuth } from '../contexts/AuthContext'
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
  const [processingComplete, setProcessingComplete] = useState(false)
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
        if (status.file_id != null && status.file_id !== '') {
          setCurrentFileId(String(status.file_id))
        }

        if (status.status === 'completed') {
          if (pollingRef.current) clearInterval(pollingRef.current)
          setUploadProgress(100)
          setCurrentStage('Processing complete!')
          setProcessingComplete(true)
          setCurrentFilename(filename)
          if (status.analysis) {
            setAnalysis(status.analysis)
            const text = status.analysis.simplified_text
            if (text) setLivePreview(text)
          }
        }
        if (status.status === 'error') {
          if (pollingRef.current) clearInterval(pollingRef.current)
          setCurrentStage('Processing failed')
          setError(
            typeof status.message === 'string'
              ? status.message
              : 'Processing failed — you can try uploading again.'
          )
        }
        if (status.analysis?.simplified_text) {
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
    setLivePreview(null)
    setProcessingComplete(false)
    setCurrentFileId(null)
    setCurrentFilename(null)
    setSavedToLibrary(false)
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

  const previewSnippet =
    analysis?.simplified_text?.trim() ||
    livePreview?.trim() ||
    ''

  const handleSaveToLibrary = async () => {
    if (!isAuthenticated) {
      setError('Please log in to save results to your profile library')
      return
    }

    if (!currentFileId) {
      setError('Missing file id — wait until processing finishes, then try again.')
      return
    }

    if (!processingComplete) {
      setError('Processing is not finished yet.')
      return
    }

    setIsSavingToLibrary(true)
    setError(null)

    try {
      const desc =
        previewSnippet.length > 0
          ? `AudioNovel processed script — ${previewSnippet.slice(0, 280)}${previewSnippet.length > 280 ? '…' : ''}`
          : 'Saved from AudioNovel upload (processing complete).'

      await addToLibrary({
        file_id: String(currentFileId),
        title: file?.name?.replace(/\.[^/.]+$/, '') || currentFilename || 'My book',
        description: desc,
        tags: ['upload', 'processed'],
      })

      setSavedToLibrary(true)
      setTimeout(() => setSavedToLibrary(false), 5000)
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const msg =
          (err.response?.data as { error?: string })?.error ||
          err.message
        setError(
          err.response?.status === 409
            ? 'This book is already in your library — open Profile to view it.'
            : msg || 'Failed to save to library'
        )
      } else {
        setError(err instanceof Error ? err.message : 'Failed to save to library')
      }
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

          {/* Save results to profile (library) — same data as Profile → My Library */}
          {processingComplete && currentFileId && (
            <div className="mt-8 p-4 border-2 border-indigo-200 bg-indigo-50/80 rounded-lg">
              <h4 className="text-lg font-semibold text-gray-900">Save to your profile</h4>
              <p className="mt-1 text-sm text-gray-600">
                Add this processed book to <strong>Profile → My Library</strong> so you can open it anytime.
              </p>
              {isAuthenticated ? (
                <div className="mt-4 flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    onClick={handleSaveToLibrary}
                    disabled={isSavingToLibrary || savedToLibrary}
                    className={`inline-flex items-center px-4 py-2 text-sm font-medium rounded-md shadow-sm text-white 
                      ${isSavingToLibrary || savedToLibrary
                        ? 'bg-green-500 cursor-not-allowed'
                        : 'bg-green-600 hover:bg-green-700'}`}
                  >
                    {isSavingToLibrary
                      ? 'Saving…'
                      : savedToLibrary
                        ? 'Saved to library'
                        : 'Save to my library'}
                  </button>
                  {savedToLibrary && (
                    <Link
                      to="/profile"
                      className="text-sm font-medium text-indigo-600 hover:text-indigo-800 underline"
                    >
                      View in Profile
                    </Link>
                  )}
                </div>
              ) : (
                <div className="mt-4 p-3 bg-white border border-indigo-100 rounded-md">
                  <p className="text-sm text-gray-700">
                    <strong>Log in</strong> to save this result to your library.{' '}
                    <button
                      type="button"
                      onClick={() => navigate('/login')}
                      className="text-indigo-600 hover:text-indigo-800 underline font-medium"
                    >
                      Log in
                    </button>{' '}
                    or{' '}
                    <button
                      type="button"
                      onClick={() => navigate('/register')}
                      className="text-indigo-600 hover:text-indigo-800 underline font-medium"
                    >
                      Create account
                    </button>
                    .
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Script Preview Box */}
          {(livePreview || analysis?.simplified_text) ? (
            <div className="mt-8 p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-lg font-medium text-gray-900">
                  {processingComplete ? 'Script preview' : 'Script preview (live)'}
                </h4>
              </div>
              <div className="prose max-w-none">
                <div className="text-gray-600 whitespace-pre-wrap">
                  {livePreview || analysis?.simplified_text || ''}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
} 