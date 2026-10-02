import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthContext'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { Layout } from './components/Layout'
import { BookFormPage } from './pages/BookFormPage'
import { BookDetailPage } from './pages/BookDetailPage'
import { CatalogPage } from './pages/CatalogPage'
import { HomePage } from './pages/HomePage'
import { ListDetailPage } from './pages/ListDetailPage'
import { ListsPage } from './pages/ListsPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="cadastro" element={<RegisterPage />} />
        <Route path="livros" element={<CatalogPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="livros/novo" element={<BookFormPage />} />
          <Route path="listas" element={<ListsPage />} />
          <Route path="listas/:id" element={<ListDetailPage />} />
        </Route>
        <Route path="livros/:id" element={<BookDetailPage />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
