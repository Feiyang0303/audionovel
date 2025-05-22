import { Link, useLocation } from 'react-router-dom'

export function Navbar() {
  const location = useLocation()
  const isActive = (path: string) => location.pathname === path

  return (
    <nav className="fixed top-0 right-0 w-full bg-white/80 backdrop-blur-sm shadow-sm z-50 h-[8vh] min-h-[3rem] max-h-[5rem] transition-all duration-300">
      <div className="flex justify-end h-full px-4 sm:px-6 md:px-8 lg:px-12">
        <div className="flex items-center space-x-6 sm:space-x-12 md:space-x-24 lg:space-x-32 h-full">
          <Link
            to="/"
            className={`text-base sm:text-base md:text-base font-medium transition-colors duration-200 hover:text-indigo-600 px-2 h-full flex items-center ${
              isActive('/') ? 'text-indigo-600' : 'text-gray-500'
            }`}
          >
            Home
          </Link>
          <Link
            to="/upload"
            className={`text-base sm:text-base md:text-base font-medium transition-colors duration-200 hover:text-indigo-600 px-2 h-full flex items-center ${
              isActive('/upload') ? 'text-indigo-600' : 'text-gray-500'
            }`}
          >
            Upload
          </Link>
          <Link
            to="/profile"
            className={`text-base sm:text-base md:text-base font-medium transition-colors duration-200 hover:text-indigo-600 px-2 h-full flex items-center ${
              isActive('/profile') ? 'text-indigo-600' : 'text-gray-500'
            }`}
          >
            Profile
          </Link>
        </div>
      </div>
    </nav>
  )
}