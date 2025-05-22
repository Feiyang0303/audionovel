import { useState } from 'react'

interface UserProfile {
  name: string
  email: string
  profilePic: string
}

interface AudioBook {
  id: string
  title: string
  createdAt: string
  duration: string
}

export function Profile() {
  // Mock user data - in a real app, this would come from an API
  const [user] = useState<UserProfile>({
    name: 'John Doe',
    email: 'john.doe@example.com',
    profilePic: 'https://ui-avatars.com/api/?name=John+Doe&background=6366f1&color=fff'
  })

  // Mock library data - in a real app, this would come from an API
  const [library] = useState<AudioBook[]>([
    {
      id: '1',
      title: 'The Little Prince',
      createdAt: '2024-03-15',
      duration: '45:30'
    },
    {
      id: '2',
      title: 'Alice in Wonderland',
      createdAt: '2024-03-10',
      duration: '1:15:20'
    }
  ])

  return (
    <div className="max-w-3xl mx-auto pt-32 px-4 sm:px-6 lg:px-8">
      <div className="bg-white shadow sm:rounded-lg">
        {/* Profile Section */}
        <div className="px-6 py-8 sm:p-8 border-b border-gray-200">
          <div className="flex items-center space-x-6">
            <img
              src={user.profilePic}
              alt={user.name}
              className="h-24 w-24 rounded-full border-2 border-indigo-100"
            />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{user.name}</h2>
              <p className="text-lg text-gray-600">{user.email}</p>
            </div>
          </div>
        </div>

        {/* Library Section */}
        <div className="px-6 py-8 sm:p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">My Library</h3>
          {library.length > 0 ? (
            <div className="space-y-4">
              {library.map((book) => (
                <div
                  key={book.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
                >
                  <div>
                    <h4 className="text-lg font-medium text-gray-900">{book.title}</h4>
                    <p className="text-sm text-gray-500">
                      Created on {new Date(book.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-500">{book.duration}</span>
                    <button
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                    >
                      Play
                    </button>
                    <button
                      className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      Download
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No audiobooks yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by uploading a book to create your first audiobook.
              </p>
              <div className="mt-6">
                <a
                  href="/upload"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Upload a Book
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 