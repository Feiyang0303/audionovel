import { Link, useLocation } from 'react-router-dom'

export function Navbar() {
  const location = useLocation()
  const isActive = (path: string) => location.pathname === path

  return (
    <nav className="fixed top-0 right-0 left-0 bg-white shadow-sm z-50">
      <div className="flex justify-end py-6 px-12">
        <div className="flex items-center gap-x-16">
          <Link
            to="/"
            className={`text-sm font-medium transition-colors duration-200 hover:text-indigo-600 px-2 ${
              isActive('/') ? 'text-indigo-600' : 'text-gray-500'
            }`}
          >
            Home
          </Link>
          <Link
            to="/upload"
            className={`text-sm font-medium transition-colors duration-200 hover:text-indigo-600 px-2 ${
              isActive('/upload') ? 'text-indigo-600' : 'text-gray-500'
            }`}
          >
            Upload
          </Link>
        </div>
      </div>
    </nav>
  )
}