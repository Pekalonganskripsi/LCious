import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Brain, Loader2, User, Mail, Lock, MapPin, Phone } from 'lucide-react';

function RegisterPage() {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();

  const [formData, setFormData] = useState({
    // User info
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    // Customer profile
    full_name: '',
    phone: '',
    address: '',
    latitude: '',
    longitude: '',
    // Preferences
    pref_price_sensitivity: 'medium',
    pref_max_distance_km: 10,
    pref_spice_level: 2,
    pref_sweetness_level: 2,
    pref_savory_level: 3,
  });

  const [passwordError, setPasswordError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) clearError();
    if (passwordError) setPasswordError('');
  };

  const validatePassword = () => {
    if (formData.password !== formData.confirmPassword) {
      setPasswordError('Password tidak cocok');
      return false;
    }
    if (formData.password.length < 6) {
      setPasswordError('Password minimal 6 karakter');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validatePassword()) {
      return;
    }

    const registrationData = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
      full_name: formData.full_name,
      phone: formData.phone || '08123456789',
      address: formData.address || 'Jawa Tengah',
      latitude: formData.latitude || '-6.8889',
      longitude: formData.longitude || '109.6756',
      preferences: {
        pref_price_importance: 0.7,
        pref_price_sensitivity: formData.pref_price_sensitivity,
        pref_distance_importance: 0.5,
        pref_max_distance_km: parseInt(formData.pref_max_distance_km),
        pref_popularity_importance: 0.3,
        pref_spice_level: parseInt(formData.pref_spice_level),
        pref_sweetness_level: parseInt(formData.pref_sweetness_level),
        pref_savory_level: parseInt(formData.pref_savory_level),
        pref_cuisines: 'indonesian',
      },
    };

    const result = await register(registrationData);

    if (result.success) {
      navigate('/dashboard');
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            latitude: position.coords.latitude.toString(),
            longitude: position.coords.longitude.toString(),
          }));
        },
        (error) => {
          console.error('Geolocation error:', error);
          alert('Tidak bisa mendapatkan lokasi. Mohon isi manual.');
        }
      );
    } else {
      alert('Browser tidak mendukung geolocation');
    }
  };

  const handleCoordinateChange = (e) => {
    const value = e.target.value;
    // Cek apakah format adalah koordinat dari Google Maps (lat, lng)
    const coordsPattern = /^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/;
    const match = value.match(coordsPattern);

    if (match) {
      // Jika format cocok, parse latitude dan longitude
      const [, lat, lng] = match;
      setFormData(prev => ({
        ...prev,
        latitude: lat,
        longitude: lng,
      }));
    } else {
      // Jika format tidak cocok, simpan sebagai latitude (backward compatibility)
      setFormData(prev => ({
        ...prev,
        latitude: value,
      }));
    }
  };

  const getCoordinateDisplayValue = () => {
    if (formData.latitude && formData.longitude) {
      return `${formData.latitude}, ${formData.longitude}`;
    }
    return formData.latitude || '';
  };

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 via-orange-500/5 to-yellow-500/5"></div>
      <div className="absolute top-20 left-10 w-96 h-96 bg-red-400/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-orange-400/10 rounded-full blur-3xl"></div>

      <div className="max-w-3xl mx-auto relative">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <img
              src="/LClogo.png"
              alt="LCious Logo"
              className="w-16 h-16 rounded-2xl object-contain shadow-lg"
            />
          </div>
          <h2 className="text-3xl font-bold text-gray-800">
            Daftar Akun <span className="text-gradient">LCious</span>
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Dapatkan rekomendasi kuliner personal sesuai selera Anda
          </p>
        </div>

        {/* Registration Form */}
        <div className="card-glass p-8">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Error Messages */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}
            {passwordError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{passwordError}</p>
              </div>
            )}

            {/* Section: Account Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <User className="w-5 h-5 text-red-500" />
                Informasi Akun
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {/* Username */}
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                    Username *
                  </label>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    required
                    value={formData.username}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all bg-white/50 backdrop-blur-sm"
                    placeholder="username"
                    disabled={isLoading}
                  />
                </div>

                {/* Email */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all bg-white/50 backdrop-blur-sm"
                      placeholder="email@example.com"
                      disabled={isLoading}
                    />
                  </div>
                </div>

                {/* Password */}
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    Password *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      id="password"
                      name="password"
                      type="password"
                      required
                      value={formData.password}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all bg-white/50 backdrop-blur-sm"
                      placeholder="Minimal 6 karakter"
                      disabled={isLoading}
                    />
                  </div>
                </div>

                {/* Confirm Password */}
                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                    Konfirmasi Password *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type="password"
                      required
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all bg-white/50 backdrop-blur-sm"
                      placeholder="Ulangi password"
                      disabled={isLoading}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Section: Personal Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <MapPin className="w-5 h-5 text-red-500" />
                Informasi Pribadi
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {/* Full Name */}
                <div>
                  <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                    Nama Lengkap *
                  </label>
                  <input
                    id="full_name"
                    name="full_name"
                    type="text"
                    required
                    value={formData.full_name}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all bg-white/50 backdrop-blur-sm"
                    placeholder="Nama lengkap"
                    disabled={isLoading}
                  />
                </div>

                {/* Phone */}
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                    No. HP
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all bg-white/50 backdrop-blur-sm"
                      placeholder="08xxxxxxxxxx"
                      disabled={isLoading}
                    />
                  </div>
                </div>

                {/* Address */}
                <div className="md:col-span-2">
                  <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
                    Alamat
                  </label>
                  <input
                    id="address"
                    name="address"
                    type="text"
                    value={formData.address}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all bg-white/50 backdrop-blur-sm"
                    placeholder="Alamat lengkap"
                    disabled={isLoading}
                  />
                </div>

                {/* Location */}
                <div className="md:col-span-2">
                  <div className="flex items-center gap-2 mb-2">
                    <label htmlFor="coordinates" className="block text-sm font-medium text-gray-700">
                      Lokasi (Koordinat)
                    </label>
                    <button
                      type="button"
                      onClick={getCurrentLocation}
                      className="text-xs px-3 py-1 bg-red-100 text-red-700 rounded-full hover:bg-red-200 transition-colors"
                    >
                      📍 Gunakan Lokasi Saya
                    </button>
                  </div>
                  <input
                    id="coordinates"
                    name="coordinates"
                    type="text"
                    value={getCoordinateDisplayValue()}
                    onChange={handleCoordinateChange}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all bg-white/50 backdrop-blur-sm"
                    placeholder="-6.951525762557895, 109.64974817723687"
                    disabled={isLoading}
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    💡 Paste koordinat dari Google Maps (klik kanan pada lokasi di maps → copy)
                  </p>
                </div>
              </div>
            </div>

            {/* Section: Taste Preferences */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                🍽️ Preferensi Rasa
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                {/* Spice Level */}
                <div>
                  <label htmlFor="pref_spice_level" className="block text-sm font-medium text-gray-700 mb-2">
                    Level Pedas (1-5)
                  </label>
                  <input
                    id="pref_spice_level"
                    name="pref_spice_level"
                    type="range"
                    min="1"
                    max="5"
                    value={formData.pref_spice_level}
                    onChange={handleChange}
                    className="w-full"
                    disabled={isLoading}
                  />
                  <div className="text-center text-sm text-gray-600">{formData.pref_spice_level}</div>
                </div>

                {/* Sweetness Level */}
                <div>
                  <label htmlFor="pref_sweetness_level" className="block text-sm font-medium text-gray-700 mb-2">
                    Level Manis (1-5)
                  </label>
                  <input
                    id="pref_sweetness_level"
                    name="pref_sweetness_level"
                    type="range"
                    min="1"
                    max="5"
                    value={formData.pref_sweetness_level}
                    onChange={handleChange}
                    className="w-full"
                    disabled={isLoading}
                  />
                  <div className="text-center text-sm text-gray-600">{formData.pref_sweetness_level}</div>
                </div>

                {/* Savory Level */}
                <div>
                  <label htmlFor="pref_savory_level" className="block text-sm font-medium text-gray-700 mb-2">
                    Level Gurih (1-5)
                  </label>
                  <input
                    id="pref_savory_level"
                    name="pref_savory_level"
                    type="range"
                    min="1"
                    max="5"
                    value={formData.pref_savory_level}
                    onChange={handleChange}
                    className="w-full"
                    disabled={isLoading}
                  />
                  <div className="text-center text-sm text-gray-600">{formData.pref_savory_level}</div>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary flex items-center justify-center gap-2 py-3"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Mendaftar...</span>
                </>
              ) : (
                <>
                  <span>Daftar Sekarang</span>
                </>
              )}
            </button>

            {/* Login Link */}
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Sudah punya akun?{' '}
                <Link to="/login" className="font-medium text-red-600 hover:text-red-700 transition-colors">
                  Masuk
                </Link>
              </p>
            </div>
          </form>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-6">
          <Link
            to="/"
            className="text-sm text-gray-600 hover:text-gray-800 transition-colors inline-flex items-center gap-1"
          >
            ← Kembali ke Beranda
          </Link>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
