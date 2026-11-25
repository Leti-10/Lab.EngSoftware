import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthContext'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { Layout } from './components/Layout'
import { BookFormPage } from './pages/BookFormPage'
import { BookDetailPage } from './pages/BookDetailPage'
import { FavoritesPage } from './pages/FavoritesPage'
import { CatalogPage } from './pages/CatalogPage'
import { HomePage } from './pages/HomePage'
import { ListDetailPage } from './pages/ListDetailPage'
import { ListsPage } from './pages/ListsPage'
import { LoginPage } from './pages/LoginPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { EditProfilePage } from './pages/EditProfilePage'
import { FeedPage } from './pages/FeedPage'
import { NotificationsPage } from './pages/NotificationsPage'
import { RecommendationsPage } from './pages/RecommendationsPage'
import { UserPage } from './pages/UserPage'
import { ProfilePage } from './pages/ProfilePage'
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
          <Route path="livros/:id/editar" element={<BookFormPage />} />
          <Route path="perfil" element={<ProfilePage />} />
          <Route path="perfil/editar" element={<EditProfilePage />} />
          <Route path="listas" element={<ListsPage />} />
          <Route path="listas/:id" element={<ListDetailPage />} />
          <Route path="favoritos" element={<FavoritesPage />} />
          <Route path="feed" element={<FeedPage />} />
          <Route path="notificacoes" element={<NotificationsPage />} />
          <Route path="recomendacoes" element={<RecommendationsPage />} />
        </Route>
        <Route path="livros/:id" element={<BookDetailPage />} />
        <Route path="usuarios/:id" element={<UserPage />} />
        <Route path="*" element={<NotFoundPage />} />
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
