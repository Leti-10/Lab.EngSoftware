import { Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Alert } from './ui'
import { Navbar } from './Navbar'

export function Layout() {
  const { user, favoritesError } = useAuth()

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-5 py-10">
        {user && favoritesError && (
          <div className="mb-6">
            <Alert>{favoritesError}</Alert>
          </div>
        )}
        <Outlet />
      </main>
    </div>
  )
}
