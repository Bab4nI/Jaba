// store/user.js
import { defineStore } from 'pinia';
import axios from 'axios';
import { useRefreshStore } from '@/stores/auth';
import cacheUtils from '@/api/cache';
import api from '@/api';

// Cache keys
const PROFILE_CACHE_KEY = 'user_profile_data';
const PROFILE_LAST_FETCH_KEY = 'user_profile_last_fetch';
const PROFILE_CACHE_DURATION = 30 * 60 * 1000; // 30 минут

// Время ожидания между попытками загрузки профиля при ошибках (5 секунд)
const RETRY_DELAY = 5000;
// Флаг, чтобы избежать множественных одновременных запросов
let isLoading = false;
// Время последней попытки загрузки (для предотвращения частых запросов)
let lastAttempt = 0;

export const useUserStore = defineStore('user', {
  state: () => ({
    first_name: '',
    last_name: '',
    middle_name: '',
    email: '',
    newEmail: '',
    group: '',
    avatarBase64: '',
    role: '',
    activeTab: 'Мой профиль',
    accessToken: localStorage.getItem('access_token') || null,
    lastProfileFetch: parseInt(localStorage.getItem(PROFILE_LAST_FETCH_KEY)) || null,
    profileCacheDuration: PROFILE_CACHE_DURATION,
    department: '',
    level: '',
    course: '',
    // Добавляем состояние загрузки для UI индикаторов
    loading: false,
    // Добавляем состояние пользователя
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken && !!state.user,
    fullName: (state) => {
      if (state.last_name && state.first_name) {
        return `${state.last_name} ${state.first_name}`;
      }
      return state.email || 'Пользователь';
    },
    // Добавляем геттер для проверки наличия данных профиля
    hasProfile: (state) => !!state.first_name && !!state.last_name
  },
  actions: {
    setAccessToken(accessToken) {
      this.accessToken = accessToken;
    },
    SET_USER_DATA(data) {
      this.first_name = data.first_name;
      this.last_name = data.last_name;
      this.middle_name = data.middle_name;
      this.email = data.email;
      this.group = data.group;
      this.avatarBase64 = data.avatar_base64;
      this.role = data.role;
      this.department = data.department || '';
      this.level = data.level || '';
      this.course = data.course || '';
      // Устанавливаем данные пользователя
      this.user = data;
      
      // Update cache time
      const now = Date.now();
      this.lastProfileFetch = now;
      localStorage.setItem(PROFILE_LAST_FETCH_KEY, now.toString());
      
      // Cache the profile data
      try {
        localStorage.setItem(PROFILE_CACHE_KEY, JSON.stringify(data));
      } catch (error) {
        console.error('Error caching profile data:', error);
      }
    },
    async fetchUserProfile(force = false) {
      // Предотвращаем одновременные запросы
      const now = Date.now();
      if (isLoading || (!force && now - lastAttempt < RETRY_DELAY)) {
        console.log('⏳ Другой запрос профиля в процессе или слишком частые запросы');
        return;
      }
      
      isLoading = true;
      lastAttempt = now;
      this.loading = true;
      
      try {
        const token = this.accessToken;
        if (!token) {
          console.error('❌ Отсутствует токен доступа');
          isLoading = false;
          this.loading = false;
          return;
        }

        // Check if we can use cached data
        if (!force && this.lastProfileFetch && (now - this.lastProfileFetch) < this.profileCacheDuration) {
          // Try to load from localStorage if state is empty
          if (!this.first_name || !this.user) {
            try {
              const cachedData = localStorage.getItem(PROFILE_CACHE_KEY);
              if (cachedData) {
                const data = JSON.parse(cachedData);
                console.log('✅ Загружены кэшированные данные профиля из localStorage');
                this.SET_USER_DATA(data);
              }
            } catch (error) {
              console.error('Ошибка при загрузке кэшированных данных профиля:', error);
            }
          }
          console.log('✅ Используем кэшированные данные профиля');
          isLoading = false;
          this.loading = false;
          return;
        }

        console.log('🔄 Загружаем свежие данные профиля');
        
        // Используем основной API вместо отдельного экземпляра axios
        // для унификации кэширования запросов
        const response = await api.get('/profile/', {
          // Skip cache if force refresh is requested
          skipCache: force
        });
        
        this.SET_USER_DATA(response.data);
        isLoading = false;
        this.loading = false;
      } catch (error) {
        console.error('❌ Ошибка при загрузке данных профиля:', error);
        if (error.response && error.response.status === 401) {
          try {
            const refreshStore = useRefreshStore();
            await refreshStore.refreshToken();

            if (refreshStore.accessToken) {
              this.setAccessToken(refreshStore.accessToken);
              // Повторяем запрос после обновления токена
              await this.fetchUserProfile(true);
            }
          } catch (refreshError) {
            console.error('Ошибка обновления токена при загрузке профиля:', refreshError);
          }
        }
        isLoading = false;
        this.loading = false;
      }
    },
    async forceFetchProfile() {
      await this.fetchUserProfile(true);
    },
    async updateAvatar(base64) {
      try {
        this.loading = true;
        await api.patch(
          '/profile/',
          { avatar_base64: base64 }
        );

        this.avatarBase64 = base64;
        
        // Update the cache after successful avatar update
        try {
          const cachedData = localStorage.getItem(PROFILE_CACHE_KEY);
          if (cachedData) {
            const data = JSON.parse(cachedData);
            data.avatar_base64 = base64;
            localStorage.setItem(PROFILE_CACHE_KEY, JSON.stringify(data));
          }
          
          // Инвалидируем кэш профиля через API
          api.invalidateProfileCache();
        } catch (error) {
          console.error('Ошибка при обновлении кэша аватара:', error);
        }
        this.loading = false;
      } catch (error) {
        console.error('❌ Ошибка при обновлении аватарки:', error);
        this.loading = false;
      }
    },
    async saveEmail() {
      try {
        this.loading = true;
        await api.patch(
          '/profile/',
          { email: this.newEmail }
        );

        this.email = this.newEmail;
        
        // Update the cache after successful email update
        try {
          const cachedData = localStorage.getItem(PROFILE_CACHE_KEY);
          if (cachedData) {
            const data = JSON.parse(cachedData);
            data.email = this.newEmail;
            localStorage.setItem(PROFILE_CACHE_KEY, JSON.stringify(data));
          }
          
          // Инвалидируем кэш профиля через API
          api.invalidateProfileCache();
        } catch (error) {
          console.error('Ошибка при обновлении кэша email:', error);
        }
        this.loading = false;
      } catch (error) {
        console.error('❌ Ошибка при обновлении email:', error);
        this.loading = false;
      }
    },
    toggleEditEmail() {
      this.isEditingEmail = !this.isEditingEmail;
      if (this.isEditingEmail) {
        this.newEmail = this.email;
      }
      this.emailError = '';
    },
    cancelEdit() {
      this.newEmail = this.email;
    },
    setActiveTab(tab) {
      this.activeTab = tab;
    },
    // Clear user profile cache
    clearProfileCache() {
      localStorage.removeItem(PROFILE_CACHE_KEY);
      localStorage.removeItem(PROFILE_LAST_FETCH_KEY);
      this.lastProfileFetch = null;
      
      // Инвалидируем кэш профиля через API
      api.invalidateProfileCache();
    },
  },
});
