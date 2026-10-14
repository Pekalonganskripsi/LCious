/**
 * Custom hook for fetching recommendations
 */
import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../store/authStore';
import { getApiBaseUrl } from '../config/api';

export function useRecommendations(initialParams = {}) {
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState(null);

  // Use ref to store latest params
  const paramsRef = useRef(initialParams);

  const { token } = useAuthStore();

  const fetchRecommendations = async (customParams = {}) => {
    if (!token) {
      setError('Authentication required');
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const API_BASE = getApiBaseUrl();

      // Use customParams if provided, otherwise use paramsRef.current
      const requestParams = Object.keys(customParams).length > 0 ? customParams : paramsRef.current;

      // Debug logging
      console.log('🔍 [useRecommendations] Request params:', requestParams);
      console.log('🔍 [useRecommendations] Request body:', {
        n: requestParams.n || 20,
        alpha: requestParams.alpha !== undefined ? requestParams.alpha : null,
        k_neighbors: requestParams.k_neighbors || 10,
        adaptive_alpha: requestParams.adaptive_alpha !== undefined ? requestParams.adaptive_alpha : false,
      });

      const response = await fetch(`${API_BASE}/recommendations/my-recommendations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          n: requestParams.n || 20,
          alpha: requestParams.alpha !== undefined ? requestParams.alpha : null,
          k_neighbors: requestParams.k_neighbors || 10,
          adaptive_alpha: requestParams.adaptive_alpha !== undefined ? requestParams.adaptive_alpha : false,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch recommendations');
      }

      const data = await response.json();
      setRecommendations(data.recommendations || []);
      setMetadata({
        customer_id: data.customer_id,
        total_recommendations: data.total_recommendations,
        alpha_used: data.alpha_used,
        adaptive_used: data.adaptive_used,
        generated_at: data.generated_at,
      });
    } catch (err) {
      setError(err.message);
      console.error('Error fetching recommendations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Update params ref when initialParams changes
  useEffect(() => {
    paramsRef.current = initialParams;
  }, [initialParams]);

  useEffect(() => {
    fetchRecommendations();
  }, [token]); // Re-fetch when token changes

  return {
    recommendations,
    isLoading,
    error,
    metadata,
    refetch: fetchRecommendations,
  };
}
