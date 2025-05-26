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

// Увеличиваем время ожидания между попытками загрузки профиля при ошибках (10 секунд)
const RETRY_DELAY = 10000;
// Флаг, чтобы избежать множественных одновременных запросов
let isLoading = false;
// Время последней попытки загрузки (для предотвращения частых запросов)
let lastAttempt = 0;
// Debounce timer for profile requests
let profileDebounceTimer = null;
// Pending profile request promise
let pendingProfileRequest = null;
// Global event bus for profile updates
const PROFILE_UPDATED_EVENT = 'profile-updated';

// Try to get initial user data from cache
let initialUserData = null;
try {
  const cachedData = localStorage.getItem(PROFILE_CACHE_KEY);
  if (cachedData) {
    initialUserData = JSON.parse(cachedData);
    console.log('✅ UserStore: Loaded initial data from cache');
  }
} catch (error) {
  console.error('Error loading cached profile data:', error);
}

// Create a central event emitter for profile updates
const createEventEmitter = () => {
  const listeners = {};
  
  return {
    on(event, callback) {
      if (!listeners[event]) {
        listeners[event] = [];
      }
      listeners[event].push(callback);
      
      // Return unsubscribe function
      return () => {
        listeners[event] = listeners[event].filter(cb => cb !== callback);
      };
    },
    
    emit(event, data) {
      if (listeners[event]) {
        listeners[event].forEach(callback => callback(data));
      }
    }
  };
};

// Create global event emitter instance
const eventEmitter = createEventEmitter();

export const useUserStore = defineStore('user', {
  state: () => ({
    first_name: initialUserData?.first_name || '',
    last_name: initialUserData?.last_name || '',
    middle_name: initialUserData?.middle_name || '',
    email: initialUserData?.email || '',
    newEmail: '',
    group: initialUserData?.group || '',
    avatarBase64: initialUserData?.avatar_base64 || '',
    role: initialUserData?.role || '',
    activeTab: 'Мой профиль',
    accessToken: localStorage.getItem('access_token') || null,
    lastProfileFetch: parseInt(localStorage.getItem(PROFILE_LAST_FETCH_KEY)) || null,
    profileCacheDuration: PROFILE_CACHE_DURATION,
    department: initialUserData?.department || '',
    level: initialUserData?.level || '',
    course: initialUserData?.course || '',
    // Добавляем состояние загрузки для UI индикаторов
    loading: false,
    // Добавляем состояние пользователя
    user: initialUserData || null,
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
    // Subscribe to profile updates
    onProfileUpdated(callback) {
      return eventEmitter.on(PROFILE_UPDATED_EVENT, callback);
    },
    
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
      console.log('Setting user role from API response:', data.role);
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
      
      // Emit profile updated event
      eventEmitter.emit(PROFILE_UPDATED_EVENT, data);
    },
    
    // Debounced version of fetchUserProfile
    debouncedFetchProfile(force = false) {
      // If there's a pending request, return that promise
      if (pendingProfileRequest) {
        console.log('⏳ Возвращаем ожидающий запрос профиля');
        return pendingProfileRequest;
      }
      
      // Clear any existing timer
      if (profileDebounceTimer) {
        clearTimeout(profileDebounceTimer);
      }
      
      // Create a new promise
      pendingProfileRequest = new Promise((resolve) => {
        profileDebounceTimer = setTimeout(async () => {
          try {
            await this.fetchUserProfile(force);
            resolve(this.user);
          } catch (error) {
            console.error('Error in debounced profile fetch:', error);
            resolve(null);
          } finally {
            pendingProfileRequest = null;
          }
        }, 300); // 300ms debounce time
      });
      
      return pendingProfileRequest;
    },
    
    async fetchUserProfile(force = false) {
      // Предотвращаем одновременные запросы
      const now = Date.now();
      if (isLoading || (!force && now - lastAttempt < RETRY_DELAY)) {
        console.log('⏳ Другой запрос профиля в процессе или слишком частые запросы');
        return this.user; // Return current user data
      }
      
      // Check if we have cached data that's still valid
      if (!force && this.user && this.lastProfileFetch && (now - this.lastProfileFetch) < this.profileCacheDuration) {
        console.log('✅ Используем кэшированные данные профиля (в памяти)');
        return this.user;
      }
      
      // Try to load from localStorage if available
      try {
        if (!force && !this.user) {
          const cachedData = localStorage.getItem(PROFILE_CACHE_KEY);
          const lastFetch = parseInt(localStorage.getItem(PROFILE_LAST_FETCH_KEY)) || 0;
          
          if (cachedData && (now - lastFetch) < this.profileCacheDuration) {
            const data = JSON.parse(cachedData);
            console.log('✅ Загружены кэшированные данные профиля из localStorage');
            this.SET_USER_DATA(data);
            return this.user;
          }
        }
      } catch (error) {
        console.error('Ошибка при загрузке кэшированных данных профиля:', error);
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
          return null;
        }

        console.log('🔄 Загружаем свежие данные профиля');
        
        // Используем основной API вместо отдельного экземпляра axios
        // для унификации кэширования запросов
        const response = await api.get('/profile/', {
          // Skip cache if force refresh is requested
          skipCache: force,
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        this.SET_USER_DATA(response.data);
        isLoading = false;
        this.loading = false;
        return this.user;
      } catch (error) {
        console.error('❌ Ошибка при загрузке данных профиля:', error);
        if (error.response && error.response.status === 401) {
          try {
            const refreshStore = useRefreshStore();
            const newToken = await refreshStore.refreshToken();

            if (newToken) {
              this.setAccessToken(newToken);
              // Повторяем запрос после обновления токена
              return await this.fetchUserProfile(true);
            } else {
              // If refresh failed, clear user data and redirect to login
              this.clearProfileCache();
              localStorage.removeItem('access_token');
              window.location.href = '/login';
            }
          } catch (refreshError) {
            console.error('Ошибка обновления токена при загрузке профиля:', refreshError);
            // If refresh failed, clear user data and redirect to login
            this.clearProfileCache();
            localStorage.removeItem('access_token');
            window.location.href = '/login';
          }
        }
        isLoading = false;
        this.loading = false;
        return null;
      }
    },
    
    async forceFetchProfile() {
      // Clear existing cache
      this.clearProfileCache();
      console.log('Forcing fresh profile fetch, bypassing cache');
      return await this.fetchUserProfile(true);
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
