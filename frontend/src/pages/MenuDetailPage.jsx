import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { API_BASE_URL, IMAGE_BASE_URL } from '../config/api';
import { showSuccess, showError } from '../utils/errorHandler';
import {
  MapPin,
  Star,
  Clock,
  Users,
  ChefHat,
  Heart,
  Share2,
  ArrowLeft,
  Trophy,
  Flame,
  Store,
} from 'lucide-react';

function MenuDetailPage() {
  const { menuId } = useParams();
  const navigate = useNavigate();
  const { token, user } = useAuthStore();
  const [menu, setMenu] = useState(null);
  const [merchant, setMerchant] = useState(null);
  const [ratings, setRatings] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [userRating, setUserRating] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchMenuDetail();
    if (token) {
      fetchUserRating();
    }
  }, [menuId, token]);

  const fetchMenuDetail = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/menus/${menuId}`);
      if (response.ok) {
        const data = await response.json();
        setMenu(data.menu);
        setMerchant(data.merchant);
        setRatings(data.ratings || []);
      }
    } catch (error) {
      console.error('Error fetching menu detail:', error);
      showError('Gagal memuat detail menu');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchUserRating = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/ratings/menu/${menuId}/my-rating`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setUserRating(data.score || 0);
      }
    } catch (error) {
      console.error('Error fetching user rating:', error);
      // Silently fail for user rating fetch
    }
  };

  const handleRate = async (rating) => {
    if (!user) {
      navigate('/login');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/ratings/submit`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          menu_id: menuId,
          score: rating,
          review_text: null,
        }),
      });

      if (response.ok) {
        setUserRating(rating);
        fetchMenuDetail(); // Refresh to update average rating
        showSuccess(`Terima kasih! Rating ${rating} bintang berhasil dikirim.`);
      }
    } catch (error) {
      console.error('Error submitting rating:', error);
      showError('Gagal mengirim rating');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Memuat detail menu...</p>
        </div>
      </div>
    );
  }

  if (!menu) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Menu tidak ditemukan</h2>
          <button
            onClick={() => navigate(-1)}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Kembali
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-5 h-5" />
            Kembali
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Menu Image */}
            <div className="card-glass overflow-hidden">
              {menu.image_url ? (
                <img
                  src={
                    menu.image_url.startsWith('data:')
                      ? menu.image_url
                      : menu.image_url.startsWith('http')
                      ? menu.image_url
                      : `${IMAGE_BASE_URL}${menu.image_url}`
                  }
                  alt={menu.item_name}
                  className="w-full h-96 object-cover"
                  onError={(e) => {
                    // Fallback to placeholder if image fails to load
                    e.target.style.display = 'none';
                    const placeholder = e.target.parentElement.querySelector('.fallback-placeholder');
                    if (placeholder) placeholder.classList.remove('hidden');
                  }}
                />
              ) : null}
              {(!menu.image_url) && (
                <div className="w-full h-96 bg-gradient-to-br from-orange-100 to-red-100 flex items-center justify-center fallback-placeholder">
                  <ChefHat className="w-32 h-32 text-orange-300" />
                </div>
              )}
            </div>

            {/* Menu Info */}
            <div className="card-glass p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h1 className="text-3xl font-bold text-gray-800 mb-2">{menu.item_name}</h1>
                  <p className="text-gray-600">{menu.description || 'Tidak ada deskripsi'}</p>
                </div>
                <div className="flex gap-2">
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                    <Heart className="w-6 h-6 text-red-500" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                    <Share2 className="w-6 h-6 text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Rating & Price */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <Star className="w-6 h-6 text-yellow-400 fill-yellow-400" />
                    <span className="text-2xl font-bold text-gray-800">
                      {menu.average_rating?.toFixed(1) || '-'}
                    </span>
                  </div>
                  <span className="text-gray-500">({menu.total_ratings || 0} rating)</span>
                </div>
                <div className="text-3xl font-bold text-gradient">
                  Rp {menu.price.toLocaleString('id-ID')}
                </div>
              </div>

              {/* Taste Profile */}
              <div className="border-t border-gray-200 pt-6">
                <h3 className="font-semibold text-gray-800 mb-3">Profil Rasa</h3>
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <Flame className="w-5 h-5 text-red-500" />
                    <div>
                      <p className="text-xs text-gray-500">Pedas</p>
                      <p className="font-medium">{menu.spice_level || 0}/5</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-5 h-5 bg-pink-400 rounded-full flex items-center justify-center text-white text-xs">
                      🍬
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Manis</p>
                      <p className="font-medium">{menu.sweetness_level || 0}/5</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-5 h-5 bg-yellow-600 rounded-full flex items-center justify-center text-white text-xs">
                      🧂
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Gurih</p>
                      <p className="font-medium">{menu.savory_level || 0}/5</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* User Rating */}
              {user && user.role === 'customer' && (
                <div className="border-t border-gray-200 pt-6 mt-6">
                  <h3 className="font-semibold text-gray-800 mb-3">Beri Rating</h3>
                  <div className="flex items-center gap-3">
                    <p className="text-sm text-gray-600">Rating Anda:</p>
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <button
                          key={star}
                          onClick={() => !isSubmitting && handleRate(star)}
                          disabled={isSubmitting}
                          className={`transition-transform hover:scale-110 ${
                            isSubmitting ? 'opacity-50 cursor-not-allowed' : ''
                          }`}
                        >
                          {star <= userRating ? (
                            <Star className="w-8 h-8 fill-yellow-400 text-yellow-400" />
                          ) : (
                            <Star className="w-8 h-8 text-gray-300" />
                          )}
                        </button>
                      ))}
                    </div>
                    {userRating > 0 && (
                      <span className="text-sm text-green-600">
                        ✓ {userRating} bintang
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Ratings & Reviews */}
            <div className="card-glass p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">
                Rating & Review ({ratings.length})
              </h2>

              {ratings.length === 0 ? (
                <div className="text-center py-8">
                  <Star className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Belum ada rating</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {ratings.slice(0, 5).map((rating) => (
                    <div key={rating.id} className="border-b border-gray-100 pb-4 last:border-0">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <p className="font-medium text-gray-800">{rating.customer_name}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(rating.created_at).toLocaleDateString('id-ID', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                            })}
                          </p>
                        </div>
                        <div className="flex items-center gap-1">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <Star
                              key={star}
                              className={`w-4 h-4 ${
                                star <= rating.score
                                  ? 'text-yellow-400 fill-yellow-400'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                      {rating.review_text && (
                        <p className="text-gray-600 italic">"{rating.review_text}"</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Merchant Info */}
            {merchant && (
              <div className="card-glass p-6">
                <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Store className="w-5 h-5" />
                  Info Warung
                </h3>
                <div className="space-y-3">
                  <div>
                    <p className="font-medium text-gray-800">{merchant.shop_name}</p>
                    <p className="text-sm text-gray-600">{merchant.description}</p>
                  </div>
                  <div className="flex items-start gap-2 text-sm text-gray-600">
                    <MapPin className="w-4 h-4 mt-1 flex-shrink-0" />
                    <p>{merchant.address}</p>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Clock className="w-4 h-4" />
                    <p>{merchant.opening_hours || 'Jam tidak tersedia'}</p>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Trophy className="w-4 h-4" />
                    <p>{merchant.cuisine_type || '-'}</p>
                  </div>
                  {merchant.price_range && (
                    <div className="text-sm text-gray-600">
                      Harga: {merchant.price_range}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Popularity Badge */}
            {menu.total_ratings > 0 && (
              <div className="card-glass p-6 bg-gradient-to-br from-yellow-50 to-orange-50">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-3 bg-yellow-400 rounded-full">
                    <Trophy className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800">Menu Populer</p>
                    <p className="text-sm text-gray-600">
                      {menu.total_ratings} orang telah mencoba
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Category */}
            <div className="card-glass p-6">
              <h3 className="font-semibold text-gray-800 mb-2">Kategori</h3>
              <span className="inline-block px-4 py-2 bg-blue-100 text-blue-700 rounded-lg font-medium">
                {menu.category}
              </span>
            </div>

            {/* Availability */}
            <div className="card-glass p-6">
              <h3 className="font-semibold text-gray-800 mb-2">Ketersediaan</h3>
              {menu.is_available ? (
                <span className="inline-flex items-center gap-2 text-green-600">
                  <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                  Tersedia
                </span>
              ) : (
                <span className="inline-flex items-center gap-2 text-red-600">
                  <span className="w-3 h-3 bg-red-500 rounded-full"></span>
                  Habis
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MenuDetailPage;
