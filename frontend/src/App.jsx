import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/layout/Navbar'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CustomerDashboardPage from './pages/CustomerDashboardPage'
import AdminDashboardPage from './pages/AdminDashboardPage'
import AdminEvaluationPage from './pages/AdminEvaluationPage'
import MerchantDashboardPage from './pages/MerchantDashboardPage'
import MerchantRegistrationPage from './pages/MerchantRegistrationPage'
import MenuDetailPage from './pages/MenuDetailPage'
import UserProfilePage from './pages/UserProfilePage'
import SearchPage from './pages/SearchPage'
import AboutPage from './pages/AboutPage'
import ProtectedRoute from './components/auth/ProtectedRoute'

function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/register/merchant" element={<MerchantRegistrationPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/about" element={<AboutPage />} />

          {/* Protected Customer Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute allowedRoles={['customer']}>
                <CustomerDashboardPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute allowedRoles={['customer']}>
                <UserProfilePage />
              </ProtectedRoute>
            }
          />

          {/* Protected Admin Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['superadmin']}>
                <AdminDashboardPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin-evaluation"
            element={
              <ProtectedRoute allowedRoles={['superadmin']}>
                <AdminEvaluationPage />
              </ProtectedRoute>
            }
          />

          {/* Protected Merchant Routes */}
          <Route
            path="/merchant"
            element={
              <ProtectedRoute allowedRoles={['merchant']}>
                <MerchantDashboardPage />
              </ProtectedRoute>
            }
          />

          {/* Public Routes - Menu Detail */}
          <Route path="/menu/:menuId" element={<MenuDetailPage />} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
