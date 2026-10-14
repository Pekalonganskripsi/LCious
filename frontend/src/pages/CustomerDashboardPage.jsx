import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { useRecommendations } from '../hooks/useRecommendations';
import RecommendationCard from '../components/customer/RecommendationCard';
import { ratingAPI } from '../services/rating';
import { getApiBaseUrl } from '../config/api';
import {
  LogOut,
  Loader2,
  SlidersHorizontal,
  RefreshCw,
  Sparkles,
  Filter,
  ChevronDown,
  ChevronUp,
  User,
  MapPin,
  UtensilsCrossed,
} from 'lucide-react';

function CustomerDashboardPage() {
  const { user, logout, token } = useAuthStore();
  const [activeTab, setActiveTab] = useState('recommendations');
  const [showFilters, setShowFilters] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);

  // Filters for recommendations
  const [filters, setFilters] = useState({
    n: 10,
    alpha: null,
    k_neighbors: 10,
    adaptive_alpha: false,  // Changed to false to allow manual alpha control
  });

  // Profile data
  const [profileData, setProfileData] = useState({
    full_name: '',
    phone: '',
    address: '',
    latitude: '',
    longitude: '',
  });

  const [preferences, setPreferences] = useState({
    pref_price_sensitivity: 'medium',
    pref_max_distance_km: 10,
    pref_spice_level: 0,
    pref_sweetness_level: 0,
    pref_savory_level: 0,
  });

  const { recommendations, isLoading, error, metadata, refetch } = useRecommendations(filters);

  // Fetch customer profile on mount
  useEffect(() => {
    if (activeTab === 'profile') {
      fetchCustomerProfile();
    }
  }, [activeTab]);

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  const fetchCustomerProfile = async () => {
    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/customers/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProfileData({
          full_name: data.customer.full_name || '',
          phone: data.customer.phone || '',
          address: data.customer.address || '',
          latitude: data.customer.latitude || '',
          longitude: data.customer.longitude || '',
        });

        if (data.preferences) {
          setPreferences({
            pref_price_sensitivity: data.preferences.pref_price_sensitivity || 'medium',
            pref_max_distance_km: data.preferences.pref_max_distance_km || 10,
            pref_spice_level: data.preferences.pref_spice_level || 0,
            pref_sweetness_level: data.preferences.pref_sweetness_level || 0,
            pref_savory_level: data.preferences.pref_savory_level || 0,
          });
        }
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setIsLoadingProfile(true);

    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/customers/me`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...profileData,
          preferences: preferences,
        }),
      });

      if (response.ok) {
        alert('Profil berhasil diperbarui!');
        setShowProfileModal(false);
        refetch(); // Refresh recommendations with new location/preferences
      } else {
        const error = await response.json();
        alert(error.detail || 'Gagal memperbarui profil');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Gagal memperbarui profil');
    } finally {
      setIsLoadingProfile(false);
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setProfileData(prev => ({
            ...prev,
            latitude: position.coords.latitude.toString(),
            longitude: position.coords.longitude.toString(),
          }));
          alert('✅ Lokasi berhasil didapatkan!');
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
      setProfileData(prev => ({
        ...prev,
        latitude: lat,
        longitude: lng,
      }));
    } else {
      // Jika format tidak cocok, simpan sebagai latitude (backward compatibility)
      setProfileData(prev => ({
        ...prev,
        latitude: value,
      }));
    }
  };

  const getCoordinateDisplayValue = () => {
    if (profileData.latitude && profileData.longitude) {
      return `${profileData.latitude}, ${profileData.longitude}`;
    }
    return profileData.latitude || '';
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleApplyFilters = () => {
    // Pass current filters to refetch
    refetch(filters);
    setShowFilters(false);
  };

  const handleRate = async (menuId, ratingValue) => {
    try {
      await ratingAPI.submitRating(token, {
        menu_id: menuId,
        score: ratingValue,
        review_text: null,
      });
      return true;
    } catch (error) {
      console.error('Failed to submit rating:', error);
      throw error;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Customer Dashboard</h1>
              <p className="text-sm text-gray-600">Kelola profil dan dapatkan rekomendasi kuliner</p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => {
                  if (activeTab === 'recommendations') refetch();
                  else if (activeTab === 'profile') fetchCustomerProfile();
                }}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                Keluar
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto">
          {[
            { id: 'recommendations', label: 'Rekomendasi', icon: Sparkles },
            { id: 'profile', label: 'Edit Profil', icon: User },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Recommendations Tab */}
        {activeTab === 'recommendations' && (
          <div>
            {/* Welcome */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                👋 Selamat Datang, {user?.full_name || 'Customer'}!
              </h2>
              <p className="text-gray-600">
                Berikut rekomendasi kuliner personal untuk Anda
              </p>
            </div>

            {/* Algorithm Info Banner */}
            {metadata && (
              <div className="card-glass p-4 mb-6 border-l-4 border-red-500">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center">
                      <Sparkles className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-800">Hybrid Fuzzy-Collaborative Filtering</h3>
                      <p className="text-sm text-gray-600">
                        Menggabungkan preferensi pribadi dengan pola komunitas
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 text-sm">
                    <div className="text-center">
                      <div className="font-bold text-gray-800">{metadata.total_recommendations}</div>
                      <div className="text-gray-600">Rekomendasi</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-gray-800">{metadata.alpha_used.toFixed(2)}</div>
                      <div className="text-gray-600">α Weight</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-gray-800">{metadata.adaptive_used ? 'Ya' : 'Tidak'}</div>
                      <div className="text-gray-600">Adaptive</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Filters Section */}
            <div className="card-glass p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                  <SlidersHorizontal className="w-5 h-5 text-red-500" />
                  Pengaturan Rekomendasi
                </h3>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
                >
                  {showFilters ? (
                    <>
                      <ChevronUp className="w-4 h-4" />
                      Sembunyikan
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-4 h-4" />
                      Tampilkan
                    </>
                  )}
                </button>
              </div>

              {showFilters && (
                <div className="space-y-4">
                  {/* Alpha Slider */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Alpha (α) - Bobot Hybrid: {filters.alpha !== null ? filters.alpha : 'Default (Adaptive)'}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={filters.alpha !== null ? filters.alpha : 0.5}
                      onChange={(e) => handleFilterChange('alpha', parseFloat(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>100% Komunitas</span>
                      <span>Balanced</span>
                      <span>100% Selera Anda</span>
                    </div>
                  </div>

                  {/* K Neighbors */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      K Neighbors (Tetangga Terdekat): {filters.k_neighbors}
                    </label>
                    <input
                      type="range"
                      min="5"
                      max="50"
                      step="5"
                      value={filters.k_neighbors}
                      onChange={(e) => handleFilterChange('k_neighbors', parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>5</span>
                      <span>25</span>
                      <span>50</span>
                    </div>
                  </div>

                  {/* Adaptive Alpha */}
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="adaptive_alpha"
                      checked={filters.adaptive_alpha}
                      onChange={(e) => handleFilterChange('adaptive_alpha', e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                    <label htmlFor="adaptive_alpha" className="text-sm text-gray-700">
                      Adaptive Alpha (Otomatis sesuaikan berdasarkan rating Anda)
                    </label>
                  </div>

                  <button
                    onClick={handleApplyFilters}
                    className="w-full py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg transition-all"
                  >
                    Terapkan Pengaturan
                  </button>
                </div>
              )}
            </div>

            {/* Recommendations Grid */}
            {isLoading ? (
              <div className="flex justify-center items-center py-20">
                <div className="text-center">
                  <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
                  <p className="text-gray-600">Memuat rekomendasi...</p>
                </div>
              </div>
            ) : error ? (
              <div className="card-glass p-12 text-center">
                <p className="text-red-600">{error}</p>
              </div>
            ) : recommendations && recommendations.length > 0 ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {recommendations.map((rec) => (
                  <RecommendationCard
                    key={rec.menu.menu_id}
                    recommendation={rec}
                    onRate={handleRate}
                    token={token}
                  />
                ))}
              </div>
            ) : (
              <div className="card-glass p-12 text-center">
                <UtensilsCrossed className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-medium text-gray-600 mb-2">Belum ada rekomendasi</h3>
                <p className="text-gray-500">Coba sesuaikan pengaturan rekomendasi Anda</p>
              </div>
            )}
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="max-w-3xl mx-auto">
            <div className="card-glass p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">Edit Profil</h2>
                  <p className="text-sm text-gray-600">Update lokasi dan preferensi rasa Anda</p>
                </div>
              </div>

              <form onSubmit={handleSaveProfile} className="space-y-6">
                {/* Personal Info */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Informasi Pribadi</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nama Lengkap
                      </label>
                      <input
                        type="text"
                        value={profileData.full_name}
                        onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Nama lengkap Anda"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nomor Telepon
                      </label>
                      <input
                        type="tel"
                        value={profileData.phone}
                        onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="08xxxxxxxxxx"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Alamat
                      </label>
                      <textarea
                        value={profileData.address}
                        onChange={(e) => setProfileData({ ...profileData, address: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows="2"
                        placeholder="Alamat lengkap Anda"
                      />
                    </div>
                  </div>
                </div>

                {/* Location */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-red-500" />
                    Lokasi (untuk rekomendasi berbasis jarak)
                  </h3>
                  <div>
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
                    />
                    <p className="text-xs text-gray-500 mt-2">
                      💡 Paste koordinat dari Google Maps (klik kanan pada lokasi di maps → copy)
                    </p>
                  </div>
                </div>

                {/* Taste Preferences */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <UtensilsCrossed className="w-5 h-5 text-orange-500" />
                    Preferensi Rasa
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        🌶️ Tingkat Pedas (0-5): {preferences.pref_spice_level}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="5"
                        value={preferences.pref_spice_level}
                        onChange={(e) => setPreferences({ ...preferences, pref_spice_level: parseInt(e.target.value) })}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>Tidak Pedas</span>
                        <span>Sangat Pedas</span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        🍬 Tingkat Manis (0-5): {preferences.pref_sweetness_level}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="5"
                        value={preferences.pref_sweetness_level}
                        onChange={(e) => setPreferences({ ...preferences, pref_sweetness_level: parseInt(e.target.value) })}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>Tidak Manis</span>
                        <span>Sangat Manis</span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        🧂 Tingkat Gurih (0-5): {preferences.pref_savory_level}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="5"
                        value={preferences.pref_savory_level}
                        onChange={(e) => setPreferences({ ...preferences, pref_savory_level: parseInt(e.target.value) })}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>Tidak Gurih</span>
                        <span>Sangat Gurih</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional Preferences */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Preferensi Lainnya</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Preferensi Harga
                      </label>
                      <select
                        value={preferences.pref_price_sensitivity}
                        onChange={(e) => setPreferences({ ...preferences, pref_price_sensitivity: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="cheap">Murah (di bawah Rp 15.000)</option>
                        <option value="medium">Sedang (Rp 10.000 - Rp 30.000)</option>
                        <option value="expensive_flexible">Fleksibel</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Jarak Maksimum (km): {preferences.pref_max_distance_km} km
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="20"
                        value={preferences.pref_max_distance_km}
                        onChange={(e) => setPreferences({ ...preferences, pref_max_distance_km: parseInt(e.target.value) })}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>1 km</span>
                        <span>10 km</span>
                        <span>20 km</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-4 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      fetchCustomerProfile();
                    }}
                    className="flex-1 px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Reset
                  </button>
                  <button
                    type="submit"
                    disabled={isLoadingProfile}
                    className="flex-1 px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg disabled:opacity-50"
                  >
                    {isLoadingProfile ? 'Menyimpan...' : 'Simpan Profil'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CustomerDashboardPage;
