import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { UtensilsCrossed, Menu, X } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    setMobileMenuOpen(false)
  }

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen)
  }

  const closeMobileMenu = () => {
    setMobileMenuOpen(false)
  }

  return (
    <nav className="sticky top-0 z-50 glass border-b border-white/20">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group" onClick={closeMobileMenu}>
            <img
              src="/LClogo.png"
              alt="LCious Logo"
              className="w-10 h-10 rounded-xl object-contain group-hover:scale-110 transition-transform"
            />
            <div>
              <h1 className="text-2xl font-bold text-gradient"><span className="font-handwriting">LCious</span></h1>
              <p className="text-xs text-gray-600">Local Culinary & Delicious</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            {/* Auth Buttons */}
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-600">
                  Halo, <span className="font-medium">{user?.username}</span>
                  {user?.role === 'superadmin' && (
                    <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                      Admin
                    </span>
                  )}
                  {user?.role === 'merchant' && (
                    <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                      Merchant
                    </span>
                  )}
                </span>
                {user?.role === 'customer' && (
                  <Link to="/dashboard" className="btn-secondary text-sm py-2">
                    Dashboard
                  </Link>
                )}
                {user?.role === 'merchant' && (
                  <Link to="/merchant" className="btn-secondary text-sm py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white hover:shadow-lg">
                    Merchant Panel
                  </Link>
                )}
                {user?.role === 'superadmin' && (
                  <Link to="/admin" className="btn-secondary text-sm py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-lg">
                    Admin Panel
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="text-sm text-red-600 hover:text-red-700 font-medium"
                >
                  Keluar
                </button>
              </div>
            ) : (
              <div className="flex gap-3">
                <Link to="/login" className="btn-secondary text-sm py-2">
                  Masuk
                </Link>
                <Link to="/register" className="btn-primary text-sm py-2">
                  Daftar
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMobileMenu}
            className="md:hidden p-2 rounded-lg hover:bg-white/20 transition-colors"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 py-4 border-t border-gray-200 animate-fadeIn">
            {isAuthenticated ? (
              <div className="flex flex-col gap-3">
                <div className="px-4 py-2 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    Halo, <span className="font-medium">{user?.username}</span>
                  </p>
                  <div className="mt-1 flex gap-2">
                    {user?.role === 'superadmin' && (
                      <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                        Admin
                      </span>
                    )}
                    {user?.role === 'merchant' && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                        Merchant
                      </span>
                    )}
                    {user?.role === 'customer' && (
                      <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                        Customer
                      </span>
                    )}
                  </div>
                </div>

                {user?.role === 'customer' && (
                  <Link
                    to="/dashboard"
                    onClick={closeMobileMenu}
                    className="px-4 py-3 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-200"
                  >
                    Dashboard
                  </Link>
                )}
                {user?.role === 'merchant' && (
                  <Link
                    to="/merchant"
                    onClick={closeMobileMenu}
                    className="px-4 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:shadow-lg transition-all"
                  >
                    Merchant Panel
                  </Link>
                )}
                {user?.role === 'superadmin' && (
                  <Link
                    to="/admin"
                    onClick={closeMobileMenu}
                    className="px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:shadow-lg transition-all"
                  >
                    Admin Panel
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors text-left font-medium"
                >
                  Keluar
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                <Link
                  to="/login"
                  onClick={closeMobileMenu}
                  className="px-4 py-3 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-200 text-center font-medium"
                >
                  Masuk
                </Link>
                <Link
                  to="/register"
                  onClick={closeMobileMenu}
                  className="px-4 py-3 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-lg hover:shadow-lg transition-all text-center font-medium"
                >
                  Daftar
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar
