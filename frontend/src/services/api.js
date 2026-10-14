/**
 * API Service for LCious Backend
 */

import { API_BASE_URL, APP_NAME } from '../config/api';

/**
 * Authentication API
 */
export const authAPI = {
  /**
   * Login user
   * @param {string} username
   * @param {string} password
   * @returns {Promise<{access_token: string, token_type: string, user: object}>}
   */
  login: async (username, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  },

  /**
   * Register customer
   * @param {object} data - Registration data
   * @returns {Promise<object>}
   */
  registerCustomer: async (data) => {
    const response = await fetch(`${API_BASE_URL}/auth/register/customer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  },

  /**
   * Get current customer profile
   * @param {string} token
   * @returns {Promise<object>}
   */
  getCustomerProfile: async (token) => {
    const response = await fetch(`${API_BASE_URL}/auth/me/customer`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch profile');
    }

    return response.json();
  },
};

/**
 * Recommendations API
 */
export const recommendationsAPI = {
  /**
   * Get personalized recommendations
   * @param {string} token
   * @param {object} params - Recommendation parameters
   * @returns {Promise<object>}
   */
  getMyRecommendations: async (token, params = {}) => {
    const response = await fetch(`${API_BASE_URL}/recommendations/my-recommendations`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        n: params.n || 20,
        alpha: params.alpha || null,
        k_neighbors: params.k_neighbors || 10,
        adaptive_alpha: params.adaptive_alpha || false,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch recommendations');
    }

    return response.json();
  },
};

/**
 * Axios-like wrapper with token
 */
export const api = {
  get: async (endpoint, token) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('API request failed');
    }

    return response.json();
  },

  post: async (endpoint, data, token) => {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  },
};
