import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { getApiBaseUrl, getImageBaseUrl } from '../config/api';
import {
  Store,
  Plus,
  Edit,
  Trash2,
  Star,
  TrendingUp,
  Users,
  UtensilsCrossed,
  RefreshCw,
  X,
  Check,
  MapPin,
  Image as ImageIcon,
  Upload,
  Loader2,
  Settings,
} from 'lucide-react';

function MerchantDashboardPage() {
  const { user, token, logout } = useAuthStore();
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);

  // Merchant profile state
  const [merchantProfile, setMerchantProfile] = useState({
    shop_name: '',
    description: '',
    address: '',
    latitude: '',
    longitude: '',
    phone: '',
    opening_hours: '',
    price_range: '',
    cuisine_type: '',
  });

  // Stats
  const [stats, setStats] = useState({
    totalMenus: 0,
    totalRatings: 0,
    averageRating: 0,
    totalViews: 0,
  });

  // Menus
  const [menus, setMenus] = useState([]);

  // Ratings
  const [ratings, setRatings] = useState([]);

  // Add/Edit Menu Modal
  const [showMenuModal, setShowMenuModal] = useState(false);
  const [editingMenu, setEditingMenu] = useState(null);
  const [menuForm, setMenuForm] = useState({
    item_name: '',
    description: '',
    price: '',
    category: 'makanan',
    spice_level: 0,
    sweetness_level: 0,
    savory_level: 0,
    image_url: '',
    is_available: true,
  });

  // Image upload states
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [imagePreview, setImagePreview] = useState('');

  useEffect(() => {
    fetchMerchantStats();
    fetchMenus();
    fetchRatings();
    if (activeTab === 'settings') {
      fetchMerchantProfile();
    }
  }, [activeTab]);

  const fetchMerchantStats = async () => {
    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/merchants/my-stats`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchMenus = async () => {
    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/merchants/my-menus`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMenus(data.menus || []);
      }
    } catch (error) {
      console.error('Error fetching menus:', error);
    }
  };

  const fetchRatings = async () => {
    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/merchants/my-ratings`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setRatings(data.ratings || []);
      }
    } catch (error) {
      console.error('Error fetching ratings:', error);
    }
  };

  const handleAddMenu = () => {
    setEditingMenu(null);
    setMenuForm({
      item_name: '',
      description: '',
      price: '',
      category: 'makanan',
      spice_level: 0,
      sweetness_level: 0,
      savory_level: 0,
      image_url: '',
      is_available: true,
    });
    setSelectedFile(null);
    setImagePreview('');
    setShowMenuModal(true);
  };

  const handleEditMenu = (menu) => {
    setEditingMenu(menu);
    setMenuForm({
      item_name: menu.item_name,
      description: menu.description || '',
      price: menu.price,
      category: menu.category,
      spice_level: menu.spice_level || 0,
      sweetness_level: menu.sweetness_level || 0,
      savory_level: menu.savory_level || 0,
      image_url: menu.image_url || '',
      is_available: menu.is_available,
    });
    setSelectedFile(null);
    const IMAGE_BASE = getImageBaseUrl();
    setImagePreview(menu.image_url ? `${IMAGE_BASE}${menu.image_url}` : '');
    setShowMenuModal(true);
  };

  const handleDeleteMenu = async (menuId) => {
    if (!confirm('Apakah Anda yakin ingin menghapus menu ini?')) return;

    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/merchants/menus/${menuId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        alert('Menu berhasil dihapus');
        fetchMenus();
        fetchMerchantStats();
      }
    } catch (error) {
      console.error('Error deleting menu:', error);
      alert('Gagal menghapus menu');
    }
  };

  const handleSaveMenu = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const API_BASE = getApiBaseUrl();
      const url = editingMenu
        ? `${API_BASE}/merchants/menus/${editingMenu.id}`
        : `${API_BASE}/merchants/menus`;

      const method = editingMenu ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...menuForm,
          price: parseFloat(menuForm.price),
        }),
      });

      if (response.ok) {
        const result = await response.json();
        const menuId = editingMenu ? editingMenu.id : result.id;

        console.log('Menu saved with ID:', menuId);

        // Upload image if file is selected
        if (selectedFile) {
          await handleImageUpload(menuId);
        } else {
          alert(editingMenu ? 'Menu berhasil diupdate' : 'Menu berhasil ditambahkan');
          setShowMenuModal(false);
          fetchMenus(); // Refresh to show updated data
          fetchMerchantStats();
        }
      } else {
        const error = await response.json();
        alert(error.detail || 'Gagal menyimpan menu');
      }
    } catch (error) {
      console.error('Error saving menu:', error);
      alert('Gagal menyimpan menu');
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = async (menuId) => {
    if (!selectedFile) return;

    console.log('Starting image upload for menu:', menuId);
    setUploadingImage(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const API_BASE = getApiBaseUrl();
      const uploadUrl = `${API_BASE}/merchants/menus/${menuId}/upload-image`;
      console.log('Uploading to:', uploadUrl);

      const response = await fetch(uploadUrl, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (response.ok) {
        const result = await response.json();
        console.log('Upload result:', result);
        alert(editingMenu ? 'Menu dan gambar berhasil diupdate' : 'Menu dan gambar berhasil ditambahkan');
        setShowMenuModal(false);
        fetchMenus();
        fetchMerchantStats();
        setSelectedFile(null);
        setImagePreview('');
      } else {
        const error = await response.json();
        console.error('Upload error:', error);
        alert(`Menu berhasil disimpan, tetapi gagal upload gambar:\nStatus: ${response.status}\nError: ${error.detail || 'Unknown error'}`);
        setShowMenuModal(false);
        fetchMenus();
        fetchMerchantStats();
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      alert('Menu berhasil disimpan, tetapi gagal upload gambar:\n' + error.message);
      setShowMenuModal(false);
      fetchMenus();
      fetchMerchantStats();
    } finally {
      setUploadingImage(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Harap pilih file gambar (JPG, PNG, GIF, WebP)');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Ukuran gambar maksimal 5MB');
        return;
      }

      setSelectedFile(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const clearImage = () => {
    setSelectedFile(null);
    setImagePreview('');
    setMenuForm({ ...menuForm, image_url: '' });
  };

  const fetchMerchantProfile = async () => {
    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/merchants/my-profile`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMerchantProfile({
          shop_name: data.shop_name || '',
          description: data.description || '',
          address: data.address || '',
          latitude: data.latitude || '',
          longitude: data.longitude || '',
          phone: data.phone || '',
          opening_hours: data.opening_hours || '',
          price_range: data.price_range || '',
          cuisine_type: data.cuisine_type || '',
        });
      }
    } catch (error) {
      console.error('Error fetching merchant profile:', error);
    }
  };

  const handleSaveMerchantProfile = async (e) => {
    e.preventDefault();
    setIsLoadingProfile(true);

    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/merchants/my-profile`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(merchantProfile),
      });

      if (response.ok) {
        alert('Profil warung berhasil diperbarui!');
        fetchMerchantProfile(); // Refresh profile data
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

  const handleCoordinateChange = (e) => {
    const value = e.target.value;
    // Cek apakah format adalah koordinat dari Google Maps (lat, lng)
    const coordsPattern = /^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/;
    const match = value.match(coordsPattern);

    if (match) {
      // Jika format cocok, parse latitude dan longitude
      const [, lat, lng] = match;
      setMerchantProfile({
        ...merchantProfile,
        latitude: lat,
        longitude: lng,
      });
    } else {
      // Jika format tidak cocok, simpan sebagai latitude (backward compatibility)
      setMerchantProfile({
        ...merchantProfile,
        latitude: value,
      });
    }
  };

  const getCoordinateDisplayValue = () => {
    if (merchantProfile.latitude && merchantProfile.longitude) {
      return `${merchantProfile.latitude}, ${merchantProfile.longitude}`;
    }
    return merchantProfile.latitude || '';
  };

  const handleGetMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setMerchantProfile({
            ...merchantProfile,
            latitude: latitude.toString(),
            longitude: longitude.toString(),
          });
          alert('✅ Lokasi warung berhasil didapatkan!');
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('❌ Gagal mendapatkan lokasi. Pastikan GPS aktif.');
        }
      );
    } else {
      alert('❌ Browser tidak mendukung geolocation');
    }
  };

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="card-glass p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-800">{value}</p>
        </div>
        <div className={`p-4 rounded-full ${color}`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
      </div>
    </div>
  );

  const MenuCard = ({ menu }) => {
    const IMAGE_BASE = getImageBaseUrl();
    return (
    <div className="card-glass overflow-hidden hover:shadow-lg transition-all">
      {/* Menu Image */}
      {menu.image_url && (
        <div className="relative h-48 overflow-hidden bg-gray-100">
          <img
            src={
              menu.image_url.startsWith('data:')
                ? menu.image_url
                : menu.image_url.startsWith('http')
                ? menu.image_url
                : `${IMAGE_BASE}${menu.image_url}`
            }
            alt={menu.item_name}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        </div>
      )}

      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-xl font-bold text-gray-800">{menu.item_name}</h3>
            {menu.is_available ? (
              <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                Tersedia
              </span>
            ) : (
              <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">
                Habis
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600 mb-2">{menu.description || 'Tidak ada deskripsi'}</p>
          <p className="text-sm text-gray-500">Kategori: {menu.category}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gradient">Rp {menu.price.toLocaleString('id-ID')}</p>
          <div className="flex items-center gap-1 mt-2">
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            <span className="text-sm text-gray-600">
              {menu.average_rating || '-'} ({menu.total_ratings || 0} rating)
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
        <span>🌶️ {menu.spice_level || 0}</span>
        <span>🍬 {menu.sweetness_level || 0}</span>
        <span>🧂 {menu.savory_level || 0}</span>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => handleEditMenu(menu)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Edit className="w-4 h-4" />
          Edit
        </button>
        <button
          onClick={() => handleDeleteMenu(menu.id)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          Hapus
        </button>
      </div>
    </div>
    </div>
  );
};

  const RatingRow = ({ rating }) => (
    <div className="card-glass p-4 mb-3">
      <div className="flex justify-between items-start mb-2">
        <div>
          <p className="font-medium text-gray-800">{rating.menu_name}</p>
          <p className="text-sm text-gray-500">
            Oleh: {rating.customer_name} • {new Date(rating.created_at).toLocaleDateString('id-ID')}
          </p>
        </div>
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <Star
              key={star}
              className={`w-5 h-5 ${
                star <= rating.score
                  ? 'text-yellow-400 fill-yellow-400'
                  : 'text-gray-300'
              }`}
            />
          ))}
        </div>
      </div>
      {rating.review_text && (
        <p className="text-sm text-gray-600 italic">"{rating.review_text}"</p>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Merchant Dashboard</h1>
              <p className="text-sm text-gray-600">Kelola menu dan lihat performa warung Anda</p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => {
                  fetchMerchantStats();
                  fetchMenus();
                  fetchRatings();
                }}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              <button
                onClick={logout}
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
            { id: 'overview', label: 'Overview', icon: TrendingUp },
            { id: 'menus', label: 'Menu Saya', icon: UtensilsCrossed },
            { id: 'ratings', label: 'Rating & Review', icon: Star },
            { id: 'settings', label: 'Setting Warung', icon: Settings },
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

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Total Menu"
                value={stats.totalMenus}
                icon={UtensilsCrossed}
                color="bg-gradient-to-br from-blue-500 to-blue-600"
              />
              <StatCard
                title="Total Rating"
                value={stats.totalRatings}
                icon={Star}
                color="bg-gradient-to-br from-yellow-500 to-orange-500"
              />
              <StatCard
                title="Rating Rata-rata"
                value={stats.averageRating.toFixed(1)}
                icon={TrendingUp}
                color="bg-gradient-to-br from-green-500 to-green-600"
              />
              <StatCard
                title="Total Views"
                value={stats.totalViews}
                icon={Users}
                color="bg-gradient-to-br from-purple-500 to-purple-600"
              />
            </div>

            {/* Quick Actions */}
            <div className="card-glass p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Aksi Cepat</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={handleAddMenu}
                  className="flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg transition-all"
                >
                  <Plus className="w-5 h-5" />
                  Tambah Menu Baru
                </button>
                <button
                  onClick={() => setActiveTab('menus')}
                  className="flex items-center justify-center gap-2 px-6 py-4 bg-white border-2 border-blue-500 text-blue-500 rounded-lg hover:bg-blue-50 transition-all"
                >
                  <UtensilsCrossed className="w-5 h-5" />
                  Kelola Menu
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Menus Tab */}
        {activeTab === 'menus' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Menu Saya ({menus.length})</h2>
              <button
                onClick={handleAddMenu}
                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg transition-all"
              >
                <Plus className="w-5 h-5" />
                Tambah Menu
              </button>
            </div>

            {menus.length === 0 ? (
              <div className="card-glass p-12 text-center">
                <UtensilsCrossed className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-medium text-gray-600 mb-2">Belum ada menu</h3>
                <p className="text-gray-500 mb-4">Mulai tambahkan menu untuk warung Anda</p>
                <button
                  onClick={handleAddMenu}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  Tambah Menu Pertama
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {menus.map((menu) => (
                  <MenuCard key={menu.id} menu={menu} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Ratings Tab */}
        {activeTab === 'ratings' && (
          <div>
            <h2 className="text-xl font-bold text-gray-800 mb-6">
              Rating & Review ({ratings.length})
            </h2>

            {ratings.length === 0 ? (
              <div className="card-glass p-12 text-center">
                <Star className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-medium text-gray-600 mb-2">Belum ada rating</h3>
                <p className="text-gray-500">Rating dari customer akan muncul di sini</p>
              </div>
            ) : (
              <div className="space-y-4">
                {ratings.map((rating) => (
                  <RatingRow key={rating.id} rating={rating} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="max-w-3xl mx-auto">
            <div className="card-glass p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                  <Settings className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">Setting Warung</h2>
                  <p className="text-sm text-gray-600">Update informasi warung dan lokasi</p>
                </div>
              </div>

              <form onSubmit={handleSaveMerchantProfile} className="space-y-6">
                {/* Shop Info */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Informasi Warung</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nama Warung *
                      </label>
                      <input
                        type="text"
                        required
                        value={merchantProfile.shop_name}
                        onChange={(e) => setMerchantProfile({ ...merchantProfile, shop_name: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Contoh: Warung Megono Pak Budi"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Deskripsi
                      </label>
                      <textarea
                        value={merchantProfile.description}
                        onChange={(e) => setMerchantProfile({ ...merchantProfile, description: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows="2"
                        placeholder="Deskripsi singkat tentang warung Anda"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Alamat *
                      </label>
                      <textarea
                        required
                        value={merchantProfile.address}
                        onChange={(e) => setMerchantProfile({ ...merchantProfile, address: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows="2"
                        placeholder="Alamat lengkap warung"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Jenis Masakan
                      </label>
                      <input
                        type="text"
                        value={merchantProfile.cuisine_type}
                        onChange={(e) => setMerchantProfile({ ...merchantProfile, cuisine_type: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Contoh: Jawa, Sunda, Padang"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Rentang Harga
                      </label>
                      <select
                        value={merchantProfile.price_range}
                        onChange={(e) => setMerchantProfile({ ...merchantProfile, price_range: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Pilih rentang harga</option>
                        <option value="$">Murah (di bawah Rp 15.000)</option>
                        <option value="$$">Sedang (Rp 15.000 - Rp 30.000)</option>
                        <option value="$$$">Mahal (di atas Rp 30.000)</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Jam Operasional
                      </label>
                      <input
                        type="text"
                        value={merchantProfile.opening_hours}
                        onChange={(e) => setMerchantProfile({ ...merchantProfile, opening_hours: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Contoh: Senin - Jumat, 08:00 - 17:00"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nomor Telepon
                      </label>
                      <input
                        type="tel"
                        value={merchantProfile.phone}
                        onChange={(e) => setMerchantProfile({ ...merchantProfile, phone: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="08xxxxxxxxxx"
                      />
                    </div>
                  </div>
                </div>

                {/* Location */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-red-500" />
                    Lokasi Warung
                  </h3>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Koordinat Lokasi *
                    </label>
                    <input
                      type="text"
                      required
                      value={getCoordinateDisplayValue()}
                      onChange={handleCoordinateChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="-6.951525762557895, 109.64974817723687"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      💡 Paste koordinat dari Google Maps (klik kanan pada lokasi di maps → copy)
                    </p>
                    <button
                      type="button"
                      onClick={handleGetMyLocation}
                      className="mt-2 w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:shadow-lg transition-all text-sm font-medium"
                    >
                      <MapPin className="w-4 h-4" />
                      Gunakan Lokasi Saya
                    </button>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-4 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      fetchMerchantProfile();
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
                    {isLoadingProfile ? 'Menyimpan...' : 'Simpan Perubahan'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>

      {/* Add/Edit Menu Modal */}
      {showMenuModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-800">
                {editingMenu ? 'Edit Menu' : 'Tambah Menu Baru'}
              </h2>
              <button
                onClick={() => setShowMenuModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-6 h-6 text-gray-600" />
              </button>
            </div>

            <form onSubmit={handleSaveMenu} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nama Menu *
                </label>
                <input
                  type="text"
                  required
                  value={menuForm.item_name}
                  onChange={(e) => setMenuForm({ ...menuForm, item_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Contoh: Nasi Goreng Spesial"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Deskripsi
                </label>
                <textarea
                  value={menuForm.description}
                  onChange={(e) => setMenuForm({ ...menuForm, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Deskripsi menu..."
                />
              </div>

              {/* Image Upload Section */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gambar Menu
                  <span className="text-xs text-gray-500 ml-2">(Opsional - Max 5MB)</span>
                </label>
                <div className="space-y-3">
                  {/* Image Preview */}
                  {(imagePreview || menuForm.image_url) && (
                    <div className="relative">
                      <img
                        src={
                          imagePreview ||
                          (menuForm.image_url?.startsWith('data:')
                            ? menuForm.image_url
                            : menuForm.image_url?.startsWith('http')
                            ? menuForm.image_url
                            : `${getImageBaseUrl()}${menuForm.image_url}`)
                        }
                        alt="Preview"
                        className="w-full h-48 object-cover rounded-lg border border-gray-300"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                      <button
                        type="button"
                        onClick={clearImage}
                        className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                        title="Hapus gambar"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  )}

                  {/* Upload Button */}
                  <div className="flex items-center gap-3">
                    <label className="flex-1 flex items-center justify-center gap-2 px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all cursor-pointer">
                      <ImageIcon className="w-5 h-5 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        {selectedFile ? selectedFile.name : 'Pilih Gambar'}
                      </span>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileSelect}
                        className="hidden"
                      />
                    </label>
                    {uploadingImage && (
                      <div className="flex items-center gap-2 text-sm text-blue-600">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Uploading...
                      </div>
                    )}
                  </div>

                  <p className="text-xs text-gray-500">
                    💡 Upload foto menu agar customer bisa melihat tampilan makanan Anda.
                    Format: JPG, PNG, GIF, WebP. Maksimal 5MB.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Harga (Rp) *
                  </label>
                  <input
                    type="number"
                    required
                    min="0"
                    value={menuForm.price}
                    onChange={(e) => setMenuForm({ ...menuForm, price: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="15000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Kategori *
                  </label>
                  <select
                    value={menuForm.category}
                    onChange={(e) => setMenuForm({ ...menuForm, category: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="makanan">Makanan</option>
                    <option value="minuman">Minuman</option>
                    <option value="snack">Snack</option>
                    <option value="dessert">Dessert</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tingkat Rasa (0-5)
                </label>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">🌶️ Pedas</label>
                    <input
                      type="number"
                      min="0"
                      max="5"
                      value={menuForm.spice_level}
                      onChange={(e) =>
                        setMenuForm({ ...menuForm, spice_level: parseInt(e.target.value) })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">🍬 Manis</label>
                    <input
                      type="number"
                      min="0"
                      max="5"
                      value={menuForm.sweetness_level}
                      onChange={(e) =>
                        setMenuForm({ ...menuForm, sweetness_level: parseInt(e.target.value) })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">🧂 Gurih</label>
                    <input
                      type="number"
                      min="0"
                      max="5"
                      value={menuForm.savory_level}
                      onChange={(e) =>
                        setMenuForm({ ...menuForm, savory_level: parseInt(e.target.value) })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL Gambar
                </label>
                <input
                  type="url"
                  value={menuForm.image_url}
                  onChange={(e) => setMenuForm({ ...menuForm, image_url: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://example.com/gambar.jpg"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_available"
                  checked={menuForm.is_available}
                  onChange={(e) => setMenuForm({ ...menuForm, is_available: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <label htmlFor="is_available" className="text-sm text-gray-700">
                  Menu tersedia
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowMenuModal(false)}
                  className="flex-1 px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg disabled:opacity-50"
                >
                  {isLoading ? 'Menyimpan...' : editingMenu ? 'Update' : 'Simpan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default MerchantDashboardPage;
