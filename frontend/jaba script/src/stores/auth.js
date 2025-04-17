import { defineStore } from 'pinia';
import axios from 'axios';
import { useUserStore } from '@/stores/user';

export const useRefreshStore = defineStore('refresh', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isRefreshingToken: false,
    isAuthenticated: !!localStorage.getItem('access_token'),
  }),

  actions: {

    setAccessToken(accessToken) {
      this.accessToken = accessToken;
      localStorage.setItem('access_token', accessToken);
      this.isAuthenticated = true;
      console.log('✅ Новый access token сохранён:', accessToken);

      // ✅ Синхронизация с userStore
      const userStore = useUserStore();
      userStore.setAccessToken(accessToken);
    },

    setRefreshToken(refreshToken) {
      this.refreshToken = refreshToken;
      localStorage.setItem('refresh_token', refreshToken);
    },

    clearTokens() {
      console.warn('⚠️ Токены удалены из localStorage');
      this.accessToken = null;
      this.refreshToken = null;
      this.isAuthenticated = false;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },

    async refreshToken() {
      if (this.isRefreshingToken) return;

      if (!this.refreshToken) {
        console.warn('❌ Refresh token отсутствует — удаляем токены');
        this.clearTokens();
        return;
      }

      try {
        this.isRefreshingToken = true;

        const response = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: localStorage.getItem('refresh_token'),
        });

        if (response.data.access) {
          this.setAccessToken(response.data.access);
        }
      } catch (error) {
        console.error('❌ Ошибка при обновлении токена:', error);
        if (error.response?.status === 401) {
          this.clearTokens();
        }
      } finally {
        this.isRefreshingToken = false;
      }
    },
    logout() {
      this.clearTokens();
    },
    async ready() {
      if (!this.accessToken) {
        this.clearTokens();
        return;
      }
      try {
        await this.refreshToken();
      } catch (error) {
        console.error('❌ Не удалось инициализировать токен:', error);
        this.clearTokens();
      }
    },
  },
});
