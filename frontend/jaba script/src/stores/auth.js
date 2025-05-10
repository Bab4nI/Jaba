import { defineStore } from 'pinia';
import axios from 'axios';
import { useUserStore } from '@/stores/user';

// Ключ для сохранения времени последнего обновления токена
const LAST_TOKEN_REFRESH_KEY = 'last_token_refresh';
// Минимальное время между обновлениями токена в миллисекундах (5 минут)
const MIN_REFRESH_INTERVAL = 5 * 60 * 1000;

// Проверка валидности JWT токена
const isValidJWT = (token) => {
  if (!token || token === 'undefined' || token === 'null') {
    console.log('❌ isValidJWT: Токен пустой или невалиден');
    return false;
  }
  
  try {
    // Проверяем тип токена
    if (typeof token !== 'string') {
      console.log(`❌ isValidJWT: Токен имеет неверный тип: ${typeof token}`);
      return false;
    }
    
    // Токен JWT должен состоять из 3 частей, разделенных точками
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.log('❌ isValidJWT: Токен не состоит из 3 частей');
      return false;
    }
    
    // Пытаемся декодировать payload
    const payload = JSON.parse(atob(parts[1]));
    
    // Проверим базовые поля JWT
    if (!payload || typeof payload !== 'object') {
      console.log('❌ isValidJWT: Payload не является объектом');
      return false;
    }
    
    // Проверяем срок действия токена
    if (payload.exp) {
      const expDate = new Date(payload.exp * 1000);
      const now = new Date();
      
      if (now >= expDate) {
        console.log(`❌ isValidJWT: Токен истек (exp: ${expDate.toISOString()}, now: ${now.toISOString()})`);
        return false;
      }
      
      console.log(`✅ isValidJWT: Токен действителен до ${expDate.toISOString()}`);
    } else {
      console.log('⚠️ isValidJWT: Токен не содержит exp, не можем проверить срок действия');
    }
    
    return true;
  } catch (e) {
    console.error('❌ Ошибка при проверке JWT токена:', e);
    return false;
  }
};

export const useRefreshStore = defineStore('refresh', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isRefreshingToken: false,
    isAuthenticated: !!localStorage.getItem('access_token'),
    // Время последнего обновления токена
    lastTokenRefresh: parseInt(localStorage.getItem(LAST_TOKEN_REFRESH_KEY)) || 0,
  }),

  actions: {
    setAccessToken(accessToken) {
      if (!accessToken) {
        console.error('❌ Попытка установить пустой access token');
        return;
      }
      
      if (typeof accessToken !== 'string') {
        console.error(`❌ Попытка установить access token неверного типа: ${typeof accessToken}`);
        return;
      }
      
      this.accessToken = accessToken;
      localStorage.setItem('access_token', accessToken);
      this.isAuthenticated = true;
      console.log(`✅ Новый access token сохранён: ${accessToken.substring(0, 15)}...`);

      // ✅ Синхронизация с userStore
      try {
        const userStore = useUserStore();
        userStore.setAccessToken(accessToken);
      } catch (error) {
        console.error('❌ Ошибка при синхронизации с userStore:', error);
      }
    },

    setRefreshToken(refreshToken) {
      if (!refreshToken) {
        console.error('❌ Попытка установить пустой refresh token');
        return;
      }
      
      if (typeof refreshToken !== 'string') {
        console.error(`❌ Попытка установить refresh token неверного типа: ${typeof refreshToken}`);
        return;
      }
      
      this.refreshToken = refreshToken;
      localStorage.setItem('refresh_token', refreshToken);
      console.log(`✅ Новый refresh token сохранён: ${refreshToken.substring(0, 15)}...`);
    },

    clearTokens() {
      console.warn('⚠️ Токены удалены из localStorage');
      this.accessToken = null;
      this.refreshToken = null;
      this.isAuthenticated = false;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem(LAST_TOKEN_REFRESH_KEY);
      this.lastTokenRefresh = 0;
    },

    // Метод для проверки, можно ли обновить токен (чтобы избежать частых обновлений)
    canRefreshToken() {
      const now = Date.now();
      return now - this.lastTokenRefresh > MIN_REFRESH_INTERVAL;
    },

    async refreshToken() {
      // Если уже идет обновление, просто возвращаем
      if (this.isRefreshingToken) {
        console.log('⏳ Уже идет обновление токена, пропускаем повторный запрос');
        return;
      }

      // Проверяем валидность refresh токена
      if (!this.refreshToken) {
        console.warn('❌ Refresh token отсутствует — удаляем токены');
        this.clearTokens();
        return;
      }

      // Проверяем тип токена
      if (typeof this.refreshToken !== 'string') {
        console.warn(`❌ Refresh token имеет неверный тип: ${typeof this.refreshToken}`);
        this.clearTokens();
        return;
      }
      
      if (!isValidJWT(this.refreshToken)) {
        console.warn('❌ Refresh token невалиден — удаляем токены');
        this.clearTokens();
        return;
      }

      // Проверяем, прошло ли достаточно времени с последнего обновления
      if (!this.canRefreshToken()) {
        console.log('⏳ Токен недавно обновлялся, пропускаем обновление');
        return;
      }

      try {
        this.isRefreshingToken = true;
        const now = Date.now();

        console.log('🔄 Отправляем запрос на обновление токена...');
        console.log(`Используем refresh token: ${this.refreshToken.substring(0, 15)}...`);
        
        // Используем правильный URL для обновления токена
        const apiUrl = 'http://localhost:8000/api/token/refresh/';
        
        console.log(`Отправляем запрос на URL: ${apiUrl}`);
        
        const response = await axios.post(
          apiUrl, 
          { refresh: this.refreshToken },
          {
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        // Проверяем ответ сервера
        if (!response.data) {
          console.warn('⚠️ Сервер вернул пустой ответ');
          this.isRefreshingToken = false;
          return;
        }

        if (!response.data.access) {
          console.warn('⚠️ Сервер вернул ответ, но без access токена');
          console.log('Ответ сервера:', response.data);
          this.isRefreshingToken = false;
          return;
        }

        // Проверяем тип и формат полученного токена
        if (typeof response.data.access !== 'string') {
          console.warn(`⚠️ Получен access token неверного типа: ${typeof response.data.access}`);
          this.isRefreshingToken = false;
          return;
        }

        console.log('✅ Токен успешно обновлен');
        this.setAccessToken(response.data.access);
        this.lastTokenRefresh = now;
        localStorage.setItem(LAST_TOKEN_REFRESH_KEY, now.toString());
        
        this.isRefreshingToken = false;
        return true;
      } catch (error) {
        console.error('❌ Ошибка при обновлении токена:', error);
        console.log('Детали запроса: refresh token =', this.refreshToken ? this.refreshToken.substring(0, 15) + '...' : 'null');
        if (error.response) {
          console.log('Статус ответа:', error.response.status);
          console.log('Данные ответа:', error.response.data);
        }
        // Если сервер ответил 400 или 401, значит токен недействителен
        if (error.response && (error.response.status === 400 || error.response.status === 401)) {
          this.clearTokens();
        }
        this.isRefreshingToken = false;
        return false;
      }
    },

    logout() {
      // Clear the user profile cache when logging out
      try {
        const userStore = useUserStore();
        if (userStore.clearProfileCache) {
          userStore.clearProfileCache();
        }
      } catch (error) {
        console.error('❌ Ошибка при очистке кэша профиля:', error);
      }
      
      this.clearTokens();
    },

    async ready() {
      console.log('🔄 Инициализация токенов в auth store');
      
      // Проверяем наличие токенов
      if (!this.accessToken || !this.refreshToken) {
        console.log('❌ Токены отсутствуют в store, проверяем localStorage');
        
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (!accessToken || !refreshToken) {
          console.log('❌ Токены отсутствуют в localStorage');
          this.clearTokens();
          return false;
        }
        
        // Устанавливаем токены из localStorage
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
        this.isAuthenticated = true;
        console.log('✅ Токены загружены из localStorage');
      }
      
      // Проверяем валидность токенов
      if (!isValidJWT(this.accessToken)) {
        console.log('❌ Access token отсутствует или невалиден');
        
        // Пробуем обновить токен, если refresh token валиден
        if (isValidJWT(this.refreshToken)) {
          console.log('🔄 Пробуем обновить токен при инициализации');
          const refreshed = await this.refreshToken();
          return refreshed;
        } else {
          this.clearTokens();
          return false;
        }
      }
      
      // Если оба токена валидны и не требуется обновление, просто возвращаем true
      console.log('✅ Токены инициализированы успешно');
      return true;
    },
  },
});
