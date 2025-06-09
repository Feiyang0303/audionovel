import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadBook } from '../services/api'
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
      // Start with initial progress
      setUploadProgress(5)
      setCurrentStage('Starting upload...')

      // Start the progress updates immediately with a shorter interval
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          // Find the next stage that's higher than current progress
          const nextStage = PROCESSING_STAGES.find(stage => stage.progress > prev)
          if (nextStage) {
            setCurrentStage(nextStage.name)
            return nextStage.progress
          }
          // If we're at the last stage, stay there
          return prev >= 95 ? 95 : prev
        })
      }, 20000) // Update every 20 seconds instead of 40

      // Make the API call
      const response = await uploadBook(file)
      
      // Clear the interval and set final progress
      clearInterval(progressInterval)
      setUploadProgress(100)
      setCurrentStage('Processing complete!')
      setAnalysis(response.analysis)
      
      // Navigate to book view after successful upload
      navigate(`/book/${response.filename}`, { state: { analysis: response.analysis } })
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

            {isUploading && (
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

          {analysis && (
            <div className="mt-8 p-4 bg-gray-50 rounded-lg">
              <h4 className="text-lg font-medium text-gray-900 mb-4">Analysis Preview</h4>
              <div className="prose max-w-none">
                <h5 className="text-md font-medium text-gray-700 mb-2">Simplified Text:</h5>
                <div className="text-gray-600 whitespace-pre-wrap">
                  {analysis.simplified_text}
                </div>
                
                <h5 className="text-md font-medium text-gray-700 mt-4 mb-2">Characters:</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis.characters.map((char, index) => (
                    <div key={index} className="bg-white p-3 rounded shadow-sm">
                      <p className="font-medium">{char.name}</p>
                      <p className="text-sm text-gray-500">Appears {char.dialogue_count} times</p>
                      <p className="text-sm text-gray-600 mt-1 italic">"{char.sample_dialogue}"</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 