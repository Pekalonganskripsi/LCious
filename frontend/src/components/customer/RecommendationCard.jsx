import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getApiBaseUrl, getImageBaseUrl } from '../../config/api';
import {
  MapPin,
  Star,
  TrendingUp,
  Brain,
  Users,
  Clock,
  ChevronDown,
  ChevronUp,
  Check,
  ExternalLink,
} from 'lucide-react';

function RecommendationCard({ recommendation, onRate, token }) {
  const [showDetails, setShowDetails] = useState(false);
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState(null);
  const [isLoadingRating, setIsLoadingRating] = useState(true);

  const { menu, scores, distance_km, explanation, rank } = recommendation;

  // Fetch user rating when component mounts or menu changes
  useEffect(() => {
    const fetchUserRating = async () => {
      setIsLoadingRating(true);
      try {
        const API_BASE = getApiBaseUrl();
        const response = await fetch(
          `${API_BASE}/ratings/menu/${menu.menu_id}/my-rating`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setRating(data.score || 0);
        } else if (response.status === 404) {
          // No rating yet, that's fine
          setRating(0);
        }
      } catch (error) {
        console.error('Error fetching user rating:', error);
      } finally {
        setIsLoadingRating(false);
      }
    };

    fetchUserRating();
  }, [menu.menu_id, token]);

  const handleRate = async (value) => {
    setIsSubmitting(true);
    setSubmitMessage(null);

    try {
      // Call the onRate callback which will use the API
      await onRate(menu.menu_id, value);

      setRating(value);
      setSubmitMessage({ type: 'success', text: `Terima kasih! Rating ${value} bintang berhasil dikirim.` });
    } catch (error) {
      setSubmitMessage({ type: 'error', text: error.message || 'Gagal mengirim rating' });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Calculate score percentages for progress bars
  const fuzzyPercent = (scores.fuzzy_score * 100).toFixed(0);
  const cfPercent = (scores.cf_score * 100).toFixed(0);
  const hybridPercent = (scores.hybrid_score * 100).toFixed(0);

  return (
    <div className="card-glass overflow-hidden hover:shadow-xl transition-all duration-300 relative">
      {/* Rank Badge */}
      <div className="absolute -top-2 -left-2 w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-full flex items-center justify-center text-white font-bold shadow-lg z-10 text-lg border-4 border-white">
        {rank}
      </div>

      {/* Menu Image */}
      {menu.image_url && (
        <div className="relative h-48 overflow-hidden bg-gray-100">
          <img
            src={menu.image_url.startsWith('data:') || menu.image_url.startsWith('http')
              ? menu.image_url
              : `${getImageBaseUrl()}${menu.image_url}`}
            alt={menu.item_name}
            className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              // Fallback if image fails to load
              e.target.style.display = 'none';
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent"></div>
        </div>
      )}

      {/* Header */}
      <div className="p-6 pb-4 pt-8">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1 pr-4 pl-8">
            <Link
              to={`/menu/${menu.menu_id}`}
              className="group block"
            >
              <h3 className="text-xl font-bold text-gray-800 mb-1 group-hover:text-blue-600 transition-colors flex items-center gap-2">
                {menu.item_name}
                <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </h3>
            </Link>
            <p className="text-sm text-gray-600">{menu.shop_name}</p>
            <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              {menu.merchant_address}
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-gradient">
              Rp {(menu.price).toLocaleString('id-ID')}
            </div>
            <p className="text-xs text-gray-500">{menu.category}</p>
          </div>
        </div>

        {/* Taste Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {menu.spice_level > 0 && (
            <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
              🌶️ Pedas {menu.spice_level}
            </span>
          )}
          {menu.sweetness_level > 0 && (
            <span className="px-2 py-1 bg-pink-100 text-pink-700 rounded-full text-xs font-medium">
              🍬 Manis {menu.sweetness_level}
            </span>
          )}
          {menu.savory_level > 0 && (
            <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
              🧂 Gurih {menu.savory_level}
            </span>
          )}
        </div>

        {/* Explanation */}
        <div className="p-3 bg-blue-50/50 backdrop-blur-sm border border-blue-200 rounded-lg mb-4">
          <p className="text-sm text-blue-900">{explanation}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="text-center p-2 bg-white/50 rounded-lg">
            <div className="text-lg font-bold text-gray-800">
              {(scores.predicted_rating).toFixed(1)}
            </div>
            <div className="text-xs text-gray-600">Prediksi Rating</div>
          </div>
          <div className="text-center p-2 bg-white/50 rounded-lg">
            <div className="text-lg font-bold text-gray-800">
              {distance_km < 1 ? `${(distance_km * 1000).toFixed(0)}m` : `${distance_km.toFixed(1)}km`}
            </div>
            <div className="text-xs text-gray-600">Jarak</div>
          </div>
          <div className="text-center p-2 bg-white/50 rounded-lg">
            <div className="text-lg font-bold text-gradient">
              {hybridPercent}%
            </div>
            <div className="text-xs text-gray-600">Match Score</div>
          </div>
        </div>

        {/* Toggle Details Button */}
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full flex items-center justify-center gap-2 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          {showDetails ? (
            <>
              <ChevronUp className="w-4 h-4" />
              Sembunyikan Detail Algoritma
            </>
          ) : (
            <>
              <ChevronDown className="w-4 h-4" />
              Lihat Detail Algoritma
            </>
          )}
        </button>
      </div>

      {/* Algorithm Details (Expandable) */}
      {showDetails && (
        <div className="px-6 pb-6 border-t border-gray-200/50 pt-4">
          <div className="space-y-4">
            {/* Hybrid Score */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-red-500" />
                  Hybrid Score (α = {scores.alpha_used.toFixed(2)})
                </span>
                <span className="text-sm font-bold text-gray-800">{hybridPercent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-red-500 to-orange-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${hybridPercent}%` }}
                />
              </div>
            </div>

            {/* Fuzzy Score */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Brain className="w-4 h-4 text-blue-500" />
                  Fuzzy Logic (Preferensi Pribadi)
                </span>
                <span className="text-sm font-bold text-gray-800">{fuzzyPercent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${fuzzyPercent}%` }}
                />
              </div>

              {/* Fuzzy Breakdown */}
              <div className="mt-2 grid grid-cols-5 gap-1 text-xs">
                <div className="text-center">
                  <div className="font-medium text-gray-700">Harga</div>
                  <div className="text-blue-600">{(scores.breakdown.price_score * 100).toFixed(0)}%</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-gray-700">Jarak</div>
                  <div className="text-blue-600">{(scores.breakdown.distance_score * 100).toFixed(0)}%</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-gray-700">Populer</div>
                  <div className="text-blue-600">{(scores.breakdown.popularity_score * 100).toFixed(0)}%</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-gray-700">Rasa</div>
                  <div className="text-blue-600">{(scores.breakdown.taste_score * 100).toFixed(0)}%</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-gray-700">Masakan</div>
                  <div className="text-blue-600">{(scores.breakdown.cuisine_score * 100).toFixed(0)}%</div>
                </div>
              </div>
            </div>

            {/* Collaborative Filtering Score */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Users className="w-4 h-4 text-purple-500" />
                  Collaborative Filtering (Komunitas)
                </span>
                <span className="text-sm font-bold text-gray-800">{cfPercent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${cfPercent}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Rating Section */}
      <div className="px-6 py-4 bg-gray-50/50 border-t border-gray-200/50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Berikan Rating:</p>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => !isSubmitting && handleRate(star)}
                  onMouseEnter={() => !isSubmitting && setHoveredRating(star)}
                  onMouseLeave={() => setHoveredRating(0)}
                  disabled={isSubmitting}
                  className={`transition-transform hover:scale-110 ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {star <= (hoveredRating || rating) ? (
                    <Star className="w-6 h-6 fill-yellow-400 text-yellow-400" />
                  ) : (
                    <Star className="w-6 h-6 text-gray-300" />
                  )}
                </button>
              ))}
            </div>
          </div>
          <div className="text-right">
            {isSubmitting && (
              <div className="text-sm text-blue-600 font-medium flex items-center gap-1">
                <Clock className="w-4 h-4 animate-spin" />
                Mengirim...
              </div>
            )}
            {submitMessage && (
              <div className={`text-sm font-medium flex items-center gap-1 ${
                submitMessage.type === 'success' ? 'text-green-600' : 'text-red-600'
              }`}>
                {submitMessage.type === 'success' && <Check className="w-4 h-4" />}
                {submitMessage.text}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default RecommendationCard;
