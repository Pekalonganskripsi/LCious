/**
 * API Configuration for LCious
 *
 * This file contains all API-related configuration.
 */

// Get API base URL at runtime
export const getApiBaseUrl = () => {
  if (typeof window === 'undefined') {
    // Server-side rendering or build time
    return 'http://192.168.100.202:8091/api/v1';
  }

  const hostname = window.location.hostname;

  // Development environments - use direct IP
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.')) {
    return 'http://192.168.100.202:8091/api/v1';
  }

  // Production via Cloudflare Tunnel - use public domain URL
  return 'https://lcious.mygarden.my.id/api/v1';
};

// Export as function for runtime detection
// NOTE: Use this function in your code, not the constant below
export const API_BASE_URL = 'https://lcious.mygarden.my.id/api/v1'; // Default for production

// App Name for notifications and branding
export const APP_NAME = 'LCious';

// Get Image base URL at runtime
export const getImageBaseUrl = () => {
  if (typeof window === 'undefined') {
    return 'http://192.168.100.202:8091';
  }

  const hostname = window.location.hostname;

  // Development environments
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.')) {
    return 'http://192.168.100.202:8091';
  }

  // Production - use public domain
  return 'https://lcious.mygarden.my.id';
};

export const IMAGE_BASE_URL = 'https://lcious.mygarden.my.id'; // Default for production

// Public API URL (for external access through Cloudflare)
export const PUBLIC_API_URL = 'https://lcious.mygarden.my.id/api/v1';

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REGISTER_CUSTOMER: '/auth/register/customer',
  REGISTER_MERCHANT: '/auth/register/merchant',
  ME_CUSTOMER: '/auth/me/customer',
  ME_MERCHANT: '/auth/me/merchant',
  ME_ADMIN: '/auth/me/admin',

  // Menus
  MENUS: '/menus',
  MENU_DETAIL: (id) => `/menus/${id}`,

  // Ratings
  SUBMIT_RATING: '/ratings/submit',
  MY_RATINGS: '/ratings/my-ratings',
  MY_RATING_FOR_MENU: (menuId) => `/ratings/menu/${menuId}/my-rating`,

  // Recommendations
  MY_RECOMMENDATIONS: '/recommendations/my-recommendations',
  RECOMMENDATION_HISTORY: '/recommendations/history',

  // Merchants
  MERCHANT_STATS: '/merchants/my-stats',
  MERCHANT_MENUS: '/merchants/my-menus',
  MERCHANT_MENU: (id) => `/merchants/menus/${id}`,
  MERCHANT_MENU_IMAGE: (id) => `/merchants/menus/${id}/upload-image`,
  MERCHANT_PROFILE: '/merchants/my-profile',
  MERCHANT_RATINGS: '/merchants/my-ratings',

  // Admin
  ADMIN_MERCHANTS: '/admin/merchants',
  ADMIN_SYSTEM_HEALTH: '/admin/evaluation/system-health',
  ADMIN_EVALUATION_RUN: '/admin/evaluation/run',
  ADMIN_EVALUATION_COMPARE: '/admin/evaluation/compare-algorithms',
  ADMIN_EVALUATION_ALPHA_OPT: '/admin/evaluation/alpha-optimization',
  ADMIN_EVALUATION_STATISTICAL: '/admin/evaluation/statistical-test',
  ADMIN_EVALUATION_BASELINES: '/admin/evaluation/baselines',
};

export default {
  API_BASE_URL,
  APP_NAME,
  IMAGE_BASE_URL,
  API_ENDPOINTS,
};
