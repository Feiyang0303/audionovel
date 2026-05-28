import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export function Home() {
  const { isAuthenticated } = useAuth()
  
  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-blue-100">
      {/* Gradient background */}
      <div className="absolute inset-0">
        {/* Base gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"></div>
        
        {/* Animated gradient layers */}
        <div className="absolute inset-0 animate-gradient-shift bg-[length:400%_400%] bg-gradient-to-r from-blue-100/20 via-indigo-100/20 to-purple-100/20"></div>
        <div className="absolute inset-0 animate-gradient-shift-reverse bg-[length:400%_400%] bg-gradient-to-br from-indigo-100/15 via-purple-100/15 to-blue-100/15"></div>
        
        {/* Soft glowing orbs */}
        <div className="absolute inset-0">
          {[...Array(3)].map((_, i) => (
            <div
              key={`orb-${i}`}
              className={`absolute w-[50rem] h-[50rem] rounded-full bg-gradient-to-r from-blue-200/10 to-indigo-200/10 blur-[150px] animate-orb-${i + 1}`}
              style={{
                left: `${20 + i * 30}%`,
                top: `${20 + i * 20}%`,
              }}
            />
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="relative min-h-screen flex flex-col items-center justify-center pt-24">
        <div className="text-center max-w-5xl">
          <h1 className="text-6xl sm:text-7xl font-bold text-gray-900 mb-8 drop-shadow-sm">
            Welcome to AudioNovel
          </h1>
          <p className="text-2xl sm:text-3xl text-gray-700 mb-12 drop-shadow-sm">
            Transform your books into engaging audiobooks with AI-powered narration
          </p>
          {isAuthenticated ? (
            <Link
              to="/upload"
              className="inline-flex items-center px-8 py-4 text-xl font-medium rounded-lg shadow-lg text-white bg-indigo-600/90 hover:bg-indigo-700 transition-all duration-200 hover:scale-105 hover:shadow-xl"
            >
              Start Creating
              <svg
                className="ml-3 w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                />
              </svg>
            </Link>
          ) : (
            <Link
              to="/login"
              className="inline-flex items-center px-8 py-4 text-xl font-medium rounded-lg shadow-lg text-white bg-indigo-600/90 hover:bg-indigo-700 transition-all duration-200 hover:scale-105 hover:shadow-xl"
            >
              Login / Sign Up
              <svg
                className="ml-3 w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
                />
              </svg>
            </Link>
          )}
        </div>
      </div>
    </div>
  )
} 