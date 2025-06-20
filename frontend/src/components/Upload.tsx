import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadBook, getStatus } from '../services/api'
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
  const navigate = useNavigate()
  const pollingRef = useRef<NodeJS.Timeout | null>(null)

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
        if (status.status === 'complete') {
          // Stop polling
          if (pollingRef.current) clearInterval(pollingRef.current)
          setUploadProgress(100)
          setCurrentStage('Processing complete!')
          setAnalysis(status.analysis)
          navigate(`/book/${filename}`, { state: { analysis: status.analysis } })
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
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-40 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
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
                  type="file"
                  className="hidden"
                  accept=".pdf,.txt,.epub,.mobi"
                  onChange={handleFileChange}
                  disabled={isUploading}
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
          {analysis && analysis.simplified_text && (
            <div className="mt-8 p-4 bg-gray-50 rounded-lg">
              <h4 className="text-lg font-medium text-gray-900 mb-4">Script Preview</h4>
              <div className="prose max-w-none">
                <div className="text-gray-600 whitespace-pre-wrap">
                  {analysis.simplified_text}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 