import { Link } from 'react-router-dom'

export function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-blue-100">
      {/* Enhanced gradient background */}
      <div className="absolute inset-0">
        {/* Base gradient layers */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(120,119,198,0.15),rgba(255,255,255,0))]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_0%_0%,rgba(147,197,253,0.12),rgba(255,255,255,0))]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_0%,rgba(129,140,248,0.12),rgba(255,255,255,0))]"></div>
        
        {/* Animated gradient layers */}
        <div className="absolute inset-0 animate-gradient-shift bg-[length:400%_400%] bg-gradient-to-r from-blue-100/15 via-indigo-100/15 to-blue-200/15"></div>
        <div className="absolute inset-0 animate-gradient-shift-reverse bg-[length:400%_400%] bg-gradient-to-br from-indigo-100/10 via-blue-100/10 to-indigo-200/10"></div>
        <div className="absolute inset-0 animate-gradient-shift bg-[length:300%_300%] bg-gradient-to-bl from-blue-50/10 via-indigo-50/10 to-blue-100/10"></div>
        
        {/* Dark blue particles */}
        <div className="absolute inset-0">
          {[...Array(80)].map((_, i) => (
            <div
              key={i}
              className={`absolute w-[3px] h-[3px] rounded-full bg-blue-900/70 animate-float-${i % 3 + 1}`}
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                transform: `scale(${0.5 + Math.random() * 0.5})`,
              }}
            />
          ))}
        </div>

        {/* Smaller particles */}
        <div className="absolute inset-0">
          {[...Array(120)].map((_, i) => (
            <div
              key={`tiny-${i}`}
              className={`absolute w-[2px] h-[2px] rounded-full bg-blue-800/60 animate-float-${i % 3 + 1}`}
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 7}s`,
                transform: `scale(${0.3 + Math.random() * 0.4})`,
              }}
            />
          ))}
        </div>

        {/* Soft glowing orbs */}
        <div className="absolute inset-0">
          {[...Array(5)].map((_, i) => (
            <div
              key={`orb-${i}`}
              className={`absolute w-[40rem] h-[40rem] rounded-full bg-gradient-to-r from-blue-200/8 to-indigo-200/8 blur-[120px] animate-orb-${i + 1}`}
              style={{
                left: `${10 + i * 20}%`,
                top: `${15 + i * 10}%`,
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
        </div>
      </div>
    </div>
  )
} 