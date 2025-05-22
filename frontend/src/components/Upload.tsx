import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadBook } from '../services/api'

export function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
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

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + 10
        })
      }, 500)

      const response = await uploadBook(file)
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      // Navigate to book view after successful upload
      navigate(`/book/${response.filename}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      setUploadProgress(0)
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
            <p>Upload your children's book in PDF, TXT, EPUB, or MOBI format.</p>
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
                        Uploading
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
        </div>
      </div>
    </div>
  )
} 