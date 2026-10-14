import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { getApiBaseUrl, getImageBaseUrl } from '../config/api';
import {
  Search,
  Sliders,
  MapPin,
  Star,
  UtensilsCrossed,
  Filter,
  ChevronDown,
  ChevronUp,
  ExternalLink,
} from 'lucide-react';

function SearchPage() {
  const { token } = useAuthStore();
  const [menus, setMenus] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Filters
  const [filters, setFilters] = useState({
    category: 'all',
    minPrice: '',
    maxPrice: '',
    minRating: '',
    sortBy: 'popularity', // popularity, price_asc, price_desc, rating
  });

  useEffect(() => {
    fetchMenus();
  }, []);

  const fetchMenus = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.category !== 'all') params.append('category', filters.category);

      const API_BASE = getApiBaseUrl();
      const response = await fetch(
        `${API_BASE}/menus?${params.toString()}`
      );
      if (response.ok) {
        const data = await response.json();
        let filteredMenus = data.menus || [];

        // Apply filters
        if (filters.minPrice) {
          filteredMenus = filteredMenus.filter((m) => m.price >= parseFloat(filters.minPrice));
        }
        if (filters.maxPrice) {
          filteredMenus = filteredMenus.filter((m) => m.price <= parseFloat(filters.maxPrice));
        }
        if (filters.minRating) {
          filteredMenus = filteredMenus.filter((m) => m.average_rating >= parseFloat(filters.minRating));
        }

        // Sort
        switch (filters.sortBy) {
          case 'price_asc':
            filteredMenus.sort((a, b) => a.price - b.price);
            break;
          case 'price_desc':
            filteredMenus.sort((a, b) => b.price - a.price);
            break;
          case 'rating':
            filteredMenus.sort((a, b) => b.average_rating - a.average_rating);
            break;
          case 'popularity':
          default:
            filteredMenus.sort((a, b) => (b.total_ratings || 0) - (a.total_ratings || 0));
            break;
        }

        // Apply search
        if (searchQuery) {
          filteredMenus = filteredMenus.filter((m) =>
            m.item_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            m.merchant?.shop_name.toLowerCase().includes(searchQuery.toLowerCase())
          );
        }

        setMenus(filteredMenus);
      }
    } catch (error) {
      console.error('Error fetching menus:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    fetchMenus();
    setShowFilters(false);
  };

  const resetFilters = () => {
    setFilters({
      category: 'all',
      minPrice: '',
      maxPrice: '',
      minRating: '',
      sortBy: 'popularity',
    });
    fetchMenus();
  };

  const MenuCard = ({ menu }) => (
    <Link
      to={`/menu/${menu.id}`}
      className="card-glass block hover:shadow-xl transition-all duration-300"
    >
      <div className="flex gap-4">
        {/* Image */}
        <div className="w-32 h-32 flex-shrink-0 bg-gradient-to-br from-orange-100 to-red-100 rounded-lg flex items-center justify-center">
          {menu.image_url ? (
            <img src={menu.image_url} alt={menu.item_name} className="w-full h-full object-cover rounded-lg" />
          ) : (
            <UtensilsCrossed className="w-12 h-12 text-orange-300" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-800 mb-1 truncate">{menu.item_name}</h3>
          <p className="text-sm text-gray-600 mb-2 truncate">{menu.merchant?.shop_name}</p>

          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <MapPin className="w-3 h-3 flex-shrink-0" />
            <span className="truncate">{menu.merchant?.address}</span>
          </div>

          {/* Taste Tags */}
          <div className="flex flex-wrap gap-1 mb-2">
            {menu.spice_level > 0 && (
              <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded-full text-xs">
                🌶️ {menu.spice_level}
              </span>
            )}
            {menu.sweetness_level > 0 && (
              <span className="px-2 py-0.5 bg-pink-100 text-pink-700 rounded-full text-xs">
                🍬 {menu.sweetness_level}
              </span>
            )}
            {menu.savory_level > 0 && (
              <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded-full text-xs">
                🧂 {menu.savory_level}
              </span>
            )}
          </div>
        </div>

        {/* Price & Rating */}
        <div className="flex flex-col items-end justify-between">
          <p className="text-lg font-bold text-gradient">
            Rp {menu.price.toLocaleString('id-ID')}
          </p>
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            <span className="text-sm text-gray-600">
              {menu.average_rating?.toFixed(1) || '-'}
            </span>
            <span className="text-xs text-gray-500">
              ({menu.total_ratings || 0})
            </span>
          </div>
        </div>
      </div>
    </Link>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Jelajah Menu</h1>

          {/* Search Bar */}
          <div className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && fetchMenus()}
                placeholder="Cari menu atau warung..."
                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-6 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 flex items-center gap-2"
            >
              <Filter className="w-5 h-5 text-gray-600" />
              Filter
              {showFilters ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </button>
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="card-glass p-6 mt-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Kategori</label>
                  <select
                    value={filters.category}
                    onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">Semua Kategori</option>
                    <option value="makanan">Makanan</option>
                    <option value="minuman">Minuman</option>
                    <option value="snack">Snack</option>
                    <option value="dessert">Dessert</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Harga Min (Rp)</label>
                  <input
                    type="number"
                    value={filters.minPrice}
                    onChange={(e) => setFilters({ ...filters, minPrice: e.target.value })}
                    placeholder="0"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Harga Max (Rp)</label>
                  <input
                    type="number"
                    value={filters.maxPrice}
                    onChange={(e) => setFilters({ ...filters, maxPrice: e.target.value })}
                    placeholder="100000"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Rating Min</label>
                  <select
                    value={filters.minRating}
                    onChange={(e) => setFilters({ ...filters, minRating: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Semua Rating</option>
                    <option value="4.5">4.5+ ⭐</option>
                    <option value="4">4.0+ ⭐</option>
                    <option value="3.5">3.5+ ⭐</option>
                    <option value="3">3.0+ ⭐</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Urutkan</label>
                  <select
                    value={filters.sortBy}
                    onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="popularity">Terpopuler</option>
                    <option value="rating">Rating Tertinggi</option>
                    <option value="price_asc">Harga Terendah</option>
                    <option value="price_desc">Harga Tertinggi</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-3 mt-4">
                <button
                  onClick={applyFilters}
                  className="flex-1 px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg"
                >
                  Terapkan Filter
                </button>
                <button
                  onClick={resetFilters}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Reset
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Results Count */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-gray-600">
            Menampilkan <span className="font-semibold">{menus.length}</span> menu
          </p>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Filter className="w-4 h-4" />
            {filters.category !== 'all' && (
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                {filters.category}
              </span>
            )}
            {filters.minRating && (
              <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full">
                {filters.minRating}+ ⭐
              </span>
            )}
          </div>
        </div>

        {/* Menu Grid */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Memuat menu...</p>
          </div>
        ) : menus.length === 0 ? (
          <div className="card-glass p-12 text-center">
            <UtensilsCrossed className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-600 mb-2">Tidak ada menu ditemukan</h3>
            <p className="text-gray-500 mb-4">Coba ubah kata kunci atau filter pencarian</p>
            <button
              onClick={resetFilters}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Reset Filter
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {menus.map((menu) => (
              <MenuCard key={menu.id} menu={menu} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default SearchPage;
