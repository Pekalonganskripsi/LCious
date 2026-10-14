import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Store, MapPin, Clock, UtensilsCrossed, ArrowLeft, Check } from 'lucide-react';

function MerchantRegistrationPage() {
  const navigate = useNavigate();
  const { register } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const [formData, setFormData] = useState({
    // User Account
    username: '',
    email: '',
    password: '',
    confirmPassword: '',

    // Shop Info
    shop_name: '',
    description: '',
    address: '',
    phone: '',

    // Location
    latitude: '',
    longitude: '',

    // Business Details
    opening_hours: '',
    price_range: '$$',
    cuisine_type: '',

    // Agreement
    agreeTerms: false,
  });

  const cuisineOptions = [
    'Indonesian',
    'Javanese',
    'Sundanese',
    'Padang',
    'Chinese',
    'Western',
    'Arab',
    'Indian',
    'Thai',
    'Japanese',
    'Korean',
    'Other',
  ];

  const priceRangeOptions = [
    { value: '$', label: 'Murah (Rp 5k - 15k)' },
    { value: '$$', label: 'Sedang (Rp 15k - 30k)' },
    { value: '$$$', label: 'Mahal (Rp 30k - 50k)' },
    { value: '$$$$', label: 'Premium (Rp 50k+)' },
  ];

  const validateForm = () => {
    const newErrors = {};

    // User validation
    if (!formData.username || formData.username.length < 3) {
      newErrors.username = 'Username minimal 3 karakter';
    }
    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email tidak valid';
    }
    if (!formData.password || formData.password.length < 6) {
      newErrors.password = 'Password minimal 6 karakter';
    }
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Password tidak cocok';
    }

    // Shop validation
    if (!formData.shop_name) {
      newErrors.shop_name = 'Nama warung wajib diisi';
    }
    if (!formData.address) {
      newErrors.address = 'Alamat wajib diisi';
    }
    if (!formData.phone) {
      newErrors.phone = 'No. telepon wajib diisi';
    }
    if (!formData.cuisine_type) {
      newErrors.cuisine_type = 'Tipe masakan wajib dipilih';
    }
    if (!formData.agreeTerms) {
      newErrors.agreeTerms = 'Anda harus menyetujui syarat & ketentuan';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      const result = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.shop_name,
        phone: formData.phone,
        // Merchant specific fields
        merchant_data: {
          shop_name: formData.shop_name,
          description: formData.description,
          address: formData.address,
          latitude: formData.latitude || '-6.8889',
          longitude: formData.longitude || '109.6756',
          phone: formData.phone,
          opening_hours: formData.opening_hours,
          price_range: formData.price_range,
          cuisine_type: formData.cuisine_type,
        },
      });

      if (result.success) {
        navigate('/merchant');
      } else {
        setErrors({ submit: result.error || 'Registrasi gagal' });
      }
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ submit: 'Terjadi kesalahan. Silakan coba lagi.' });
    } finally {
      setIsLoading(false);
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData({
            ...formData,
            latitude: position.coords.latitude.toString(),
            longitude: position.coords.longitude.toString(),
          });
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('Gagal mendapatkan lokasi. Silakan isi manual.');
        }
      );
    } else {
      alert('Geolocation tidak didukung di browser ini.');
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
      setFormData({
        ...formData,
        latitude: lat,
        longitude: lng,
      });
    } else {
      // Jika format tidak cocok, simpan sebagai latitude (backward compatibility)
      setFormData({
        ...formData,
        latitude: value,
      });
    }
  };

  const getCoordinateDisplayValue = () => {
    if (formData.latitude && formData.longitude) {
      return `${formData.latitude}, ${formData.longitude}`;
    }
    return formData.latitude || '';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Kembali
          </button>
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl mb-4 shadow-lg">
              <Store className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              Registrasi Merchant
            </h1>
            <p className="text-gray-600">
              Daftarkan warung/UMKM Anda ke LCious dan jangkau lebih banyak pelanggan
            </p>
          </div>
        </div>

        {/* Registration Form */}
        <div className="card-glass p-8">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Account Information */}
            <div>
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <span className="flex items-center justify-center w-8 h-8 bg-blue-500 text-white rounded-full text-sm font-bold">
                  1
                </span>
                Informasi Akun
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username *
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                      errors.username ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                    }`}
                    placeholder="contoh: warung_nasi_001"
                  />
                  {errors.username && (
                    <p className="text-sm text-red-600 mt-1">{errors.username}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                      errors.email ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                    }`}
                    placeholder="email@contoh.com"
                  />
                  {errors.email && <p className="text-sm text-red-600 mt-1">{errors.email}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password *
                  </label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                      errors.password ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                    }`}
                    placeholder="Minimal 6 karakter"
                  />
                  {errors.password && <p className="text-sm text-red-600 mt-1">{errors.password}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Konfirmasi Password *
                  </label>
                  <input
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                      errors.confirmPassword ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                    }`}
                    placeholder="Ulangi password"
                  />
                  {errors.confirmPassword && (
                    <p className="text-sm text-red-600 mt-1">{errors.confirmPassword}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Shop Information */}
            <div>
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <span className="flex items-center justify-center w-8 h-8 bg-purple-500 text-white rounded-full text-sm font-bold">
                  2
                </span>
                Informasi Warung
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nama Warung *
                  </label>
                  <input
                    type="text"
                    value={formData.shop_name}
                    onChange={(e) => setFormData({ ...formData, shop_name: e.target.value })}
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                      errors.shop_name ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                    }`}
                    placeholder="Contoh: Warung Nasi Uduk Gourmet"
                  />
                  {errors.shop_name && <p className="text-sm text-red-600 mt-1">{errors.shop_name}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Deskripsi Warung
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="3"
                    placeholder="Ceritakan sedikit tentang warung Anda..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Alamat Lengkap *
                  </label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                      errors.address ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                    }`}
                    placeholder="Jl. Contoh No. 123, Kelurahan, Kecamatan, Kota"
                  />
                  {errors.address && <p className="text-sm text-red-600 mt-1">{errors.address}</p>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      No. Telepon *
                    </label>
                    <input
                      type="text"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                        errors.phone ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                      }`}
                      placeholder="08123456789"
                    />
                    {errors.phone && <p className="text-sm text-red-600 mt-1">{errors.phone}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Jam Operasional
                    </label>
                    <input
                      type="text"
                      value={formData.opening_hours}
                      onChange={(e) => setFormData({ ...formData, opening_hours: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Senin-Jumat: 08:00-20:00"
                    />
                  </div>
                </div>

                {/* Location */}
                <div className="card-glass p-4 bg-blue-50">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-5 h-5 text-blue-600" />
                      <span className="font-medium text-gray-800">Lokasi Warung</span>
                    </div>
                    <button
                      type="button"
                      onClick={getCurrentLocation}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      📍 Gunakan Lokasi Saya
                    </button>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Koordinat Lokasi
                    </label>
                    <input
                      type="text"
                      value={getCoordinateDisplayValue()}
                      onChange={handleCoordinateChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="-6.951525762557895, 109.64974817723687"
                    />
                    <p className="text-xs text-gray-500 mt-2">
                      💡 Paste koordinat dari Google Maps (klik kanan pada lokasi di maps → copy). Koordinat diperlukan untuk menghitung jarak ke customer.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Rentang Harga *
                    </label>
                    <select
                      value={formData.price_range}
                      onChange={(e) => setFormData({ ...formData, price_range: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {priceRangeOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tipe Masakan *
                    </label>
                    <select
                      value={formData.cuisine_type}
                      onChange={(e) => setFormData({ ...formData, cuisine_type: e.target.value })}
                      className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                        errors.cuisine_type ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                      }`}
                    >
                      <option value="">Pilih tipe masakan</option>
                      {cuisineOptions.map((cuisine) => (
                        <option key={cuisine} value={cuisine}>
                          {cuisine}
                        </option>
                      ))}
                    </select>
                    {errors.cuisine_type && (
                      <p className="text-sm text-red-600 mt-1">{errors.cuisine_type}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Agreement */}
            <div>
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.agreeTerms}
                  onChange={(e) => setFormData({ ...formData, agreeTerms: e.target.checked })}
                  className={`mt-1 w-5 h-5 rounded ${
                    errors.agreeTerms ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                <span className="text-sm text-gray-600">
                  Saya menyetujui{' '}
                  <Link to="/terms" className="text-blue-600 hover:underline">
                    Syarat & Ketentuan
                  </Link>{' '}
                  serta{' '}
                  <Link to="/privacy" className="text-blue-600 hover:underline">
                    Kebijakan Privasi
                  </Link>{' '}
                  LCious
                </span>
              </label>
              {errors.agreeTerms && <p className="text-sm text-red-600 mt-1">{errors.agreeTerms}</p>}
            </div>

            {/* Submit Button */}
            <div className="flex flex-col gap-4">
              {errors.submit && (
                <div className="p-4 bg-red-100 text-red-700 rounded-lg">
                  {errors.submit}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold text-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Memproses...
                  </>
                ) : (
                  <>
                    <Store className="w-5 h-5" />
                    Daftar Sebagai Merchant
                  </>
                )}
              </button>

              <p className="text-center text-sm text-gray-600">
                Sudah punya akun?{' '}
                <Link to="/login" className="text-blue-600 hover:underline font-medium">
                  Login disini
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default MerchantRegistrationPage;
