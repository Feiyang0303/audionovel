import { Link } from 'react-router-dom'

export function Home() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-white">
      <div className="max-w-3xl mx-auto text-center px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl mb-6">
          Welcome to Children's Audiobook Creator
        </h1>
        <p className="text-xl text-gray-500 mb-12">
          Transform books into engaging audiobooks with AI-powered narration.
        </p>
        <Link
          to="/upload"
          className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 transition-colors duration-200"
        >
          Start Creating
          <svg 
            className="ml-2 -mr-1 w-5 h-5" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M13 7l5 5m0 0l-5 5m5-5H6" 
            />
          </svg>
        </Link>
      </div>
    </div>
  )
} 