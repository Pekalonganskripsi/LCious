/**
 * Global Error Handler for LCious
 *
 * Provides consistent error handling across the application
 * and ensures error messages don't expose internal URLs
 */

import { APP_NAME } from '../config/api';

/**
 * Handle API errors and return user-friendly messages
 * @param {Error} error - The error object
 * @param {string} defaultMessage - Default message if error can't be parsed
 * @returns {string} User-friendly error message
 */
export const handleApiError = (error, defaultMessage = 'Terjadi kesalahan') => {
  // Don't expose URLs or internal paths in error messages
  const errorMessage = error?.message || '';

  // Remove URLs from error messages
  const cleanedMessage = errorMessage.replace(/https?:\/\/[^\s]+/g, APP_NAME);
  cleanedMessage.replace(/192\.168\.[0-9]+\.[0-9]+:[0-9]+/g, APP_NAME);

  if (cleanedMessage) {
    return cleanedMessage;
  }

  return defaultMessage;
};

/**
 * Show error notification to user
 * @param {string} message - Error message to display
 * @param {string} type - Error type (error, warning, info)
 */
export const showError = (message, type = 'error') => {
  // Remove any URLs or IP addresses from the message
  const cleanMessage = message
    .replace(/https?:\/\/[^\s]+/g, APP_NAME)
    .replace(/192\.168\.[0-9]+\.[0-9]+:[0-9]+/g, APP_NAME);

  // Use browser alert as fallback (can be replaced with toast notification)
  alert(cleanMessage);

  // Also log to console for debugging
  if (type === 'error') {
    console.error(`[${APP_NAME}] Error:`, message);
  } else {
    console.log(`[${APP_NAME}] ${type}:`, message);
  }
};

/**
 * Show success notification to user
 * @param {string} message - Success message to display
 */
export const showSuccess = (message) => {
  alert(`✓ ${message}`);
  console.log(`[${APP_NAME}] Success:`, message);
};

/**
 * Wrap API calls with error handling
 * @param {Function} apiCall - The API function to call
 * @param {string} errorMessage - Custom error message
 * @returns {Promise} Promise that resolves with data or rejects with error
 */
export const withErrorHandling = async (apiCall, errorMessage = null) => {
  try {
    const response = await apiCall();
    return response;
  } catch (error) {
    const message = errorMessage || handleApiError(error);
    showError(message);
    throw error;
  }
};

export default {
  handleApiError,
  showError,
  showSuccess,
  withErrorHandling,
};
