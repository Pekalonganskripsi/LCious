/**
 * Authentication Store using Zustand
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { getApiBaseUrl } from '../config/api';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      // Actions
      login: async (username, password) => {
        set({ isLoading: true, error: null });
        try {
          const API_BASE = getApiBaseUrl();
          const data = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
          }).then(res => {
            if (!res.ok) {
              return res.json().then(err => {
                throw new Error(err.detail || 'Login gagal');
              });
            }
            return res.json();
          });

          set({
            user: data.user,
            token: data.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

          return { success: true, user: data.user };
        } catch (error) {
          set({
            isLoading: false,
            error: error.message,
          });
          return { success: false, error: error.message };
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const API_BASE = getApiBaseUrl();
          const data = await fetch(`${API_BASE}/auth/register/customer`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
          }).then(res => {
            if (!res.ok) {
              return res.json().then(err => {
                throw new Error(err.detail || 'Registrasi gagal');
              });
            }
            return res.json();
          });

          // Auto login after registration
          const loginResult = await get().login(userData.username, userData.password);

          set({ isLoading: false });

          return { success: true, ...loginResult };
        } catch (error) {
          set({
            isLoading: false,
            error: error.message,
          });
          return { success: false, error: error.message };
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      updateUser: (userData) => {
        set({ user: { ...get().user, ...userData } });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'lcious-auth', // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
