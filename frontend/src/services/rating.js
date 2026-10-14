/**
 * Rating API Service
 */

import { API_BASE_URL, APP_NAME } from '../config/api';

export const ratingAPI = {
  /**
   * Submit rating for a menu
   * @param {string} token - Auth token
   * @param {object} ratingData - Rating data
   * @returns {Promise<object>}
   */
  submitRating: async (token, ratingData) => {
    const response = await fetch(`${API_BASE_URL}/ratings/submit`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(ratingData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Gagal mengirim rating di ${APP_NAME}`);
    }

    return response.json();
  },

  /**
   * Get user's rating history
   * @param {string} token - Auth token
   * @param {number} limit - Limit results
   * @param {number} offset - Offset for pagination
   * @returns {Promise<object>}
   */
  getMyRatings: async (token, limit = 20, offset = 0) => {
    const response = await fetch(
      `${API_BASE_URL}/ratings/my-ratings?limit=${limit}&offset=${offset}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Gagal mengambil rating dari ${APP_NAME}`);
    }

    return response.json();
  },

  /**
   * Get user's rating for a specific menu
   * @param {string} token - Auth token
   * @param {string} menuId - Menu ID
   * @returns {Promise<object>}
   */
  getMyRatingForMenu: async (token, menuId) => {
    const response = await fetch(
      `${API_BASE_URL}/ratings/menu/${menuId}/my-rating`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      if (response.status === 404) {
        return null; // No rating yet
      }
      throw new Error(`Gagal mengambil rating dari ${APP_NAME}`);
    }

    return response.json();
  },
};
