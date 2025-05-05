// plugins/tokenRefresh.js
import { useRefreshStore } from '@/stores/auth';

// Ключ для сохранения времени последнего обновления токена
const LAST_TOKEN_REFRESH_KEY = 'last_token_refresh';
// Минимальное время между обновлениями токена в миллисекундах (5 минут)
const MIN_REFRESH_INTERVAL = 5 * 60 * 1000;
// Интервал проверки токена (30 секунд)
const CHECK_INTERVAL = 30 * 1000;
// Запас времени перед истечением токена, когда нужно его обновить (1 минута)
const REFRESH_BEFORE_EXPIRY = 60 * 1000;

export default {
  install(app, { pinia }) {
    let refreshTokenInterval = null;
    let isInitialized = false;

    // Проверка валидности refresh token
    const isRefreshTokenValid = (token) => {
      if (!token || token === 'undefined' || token === 'null') {
        console.error('TokenRefresh: Refresh token пустой или невалидный');
        return false;
      }
      
      try {
        // Проверяем тип токена
        if (typeof token !== 'string') {
          console.error(`TokenRefresh: Refresh token имеет неверный тип: ${typeof token}`);
          return false;
        }
        
        // Пытаемся декодировать JWT (если возможно)
        // Это простая проверка формата, а не срока действия
        const parts = token.split('.');
        if (parts.length !== 3) {
          console.error(`TokenRefresh: Refresh token имеет неверный формат (parts: ${parts.length})`);
          return false;
        }
        
        // Проверка формата JWT (должно быть 3 части)
        const payload = JSON.parse(atob(parts[1]));
        console.log('TokenRefresh: Успешно декодирован JWT payload', payload);
        return true;
      } catch (e) {
        console.error('TokenRefresh: Ошибка при проверке refresh token:', e);
        return false;
      }
    };

    // Проверяем время последнего обновления токена и решаем, нужно ли его обновлять
    const shouldRefreshToken = () => {
      const lastRefresh = parseInt(localStorage.getItem(LAST_TOKEN_REFRESH_KEY)) || 0;
      const now = Date.now();
      const timeSinceLastRefresh = now - lastRefresh;
      console.log(`TokenRefresh: Последнее обновление токена было ${Math.round(timeSinceLastRefresh/1000)} секунд назад`);
      return timeSinceLastRefresh > MIN_REFRESH_INTERVAL;
    };

    // Проверяем, истекает ли токен скоро
    const isTokenExpiringSoon = (accessToken) => {
      try {
        if (!accessToken || accessToken === 'undefined' || accessToken === 'null') {
          console.error('TokenRefresh: Access token пустой или невалидный');
          return false;
        }
        
        if (typeof accessToken !== 'string') {
          console.error(`TokenRefresh: Access token имеет неверный тип: ${typeof accessToken}`);
          return false;
        }
        
        const parts = accessToken.split('.');
        if (parts.length !== 3) {
          console.error(`TokenRefresh: Access token имеет неверный формат (parts: ${parts.length})`);
          return false;
        }
        
        const tokenPayload = JSON.parse(atob(parts[1]));
        const expirationTime = tokenPayload.exp * 1000; // Время истечения в миллисекундах
        const currentTime = Date.now();
        
        // Проверяем срок действия токена
        if (expirationTime < currentTime) {
          console.log('TokenRefresh: Токен уже истек');
          return true;
        }
        
        const timeToExpiry = expirationTime - currentTime;
        console.log(`TokenRefresh: До истечения токена осталось ${Math.round(timeToExpiry/1000)} секунд`);
        
        return timeToExpiry < REFRESH_BEFORE_EXPIRY;
      } catch (error) {
        console.error('TokenRefresh: Ошибка при разборе accessToken:', error);
        // В случае ошибки при разборе токена считаем его невалидным
        return false;
      }
    };

    // Обновляем токен и сохраняем время обновления
    const refreshToken = async (refreshStore) => {
      // Проверка валидности refresh token
      if (!isRefreshTokenValid(refreshStore.refreshToken)) {
        console.log('TokenRefresh: Refresh token невалиден, очищаем токены');
        refreshStore.clearTokens();
        return;
      }
      
      if (shouldRefreshToken()) {
        console.log('TokenRefresh: Обновляем токен...');
        await refreshStore.refreshToken();
        localStorage.setItem(LAST_TOKEN_REFRESH_KEY, Date.now().toString());
      } else {
        console.log('TokenRefresh: Токен был недавно обновлен, пропускаем обновление');
      }
    };

    const checkAndInitTokens = async () => {
      const refreshStore = useRefreshStore(pinia);
      console.log('TokenRefresh: Инициализация токенов...');
      
      // Проверяем наличие токенов
      const accessToken = refreshStore.accessToken || localStorage.getItem('access_token');
      const refreshToken = refreshStore.refreshToken || localStorage.getItem('refresh_token');
      
      console.log('TokenRefresh: Проверка наличия токенов', {
        accessToken: accessToken ? `${accessToken.substring(0, 15)}...` : null,
        refreshToken: refreshToken ? `${refreshToken.substring(0, 15)}...` : null
      });
      
      if (!accessToken || !refreshToken) {
        console.log('TokenRefresh: Токены отсутствуют, очищаем данные аутентификации');
        refreshStore.clearTokens();
        return;
      }
      
      // Проверяем валидность токенов
      if (!isRefreshTokenValid(refreshToken)) {
        console.log('TokenRefresh: Refresh token невалиден, очищаем токены');
        refreshStore.clearTokens();
        return;
      }
      
      // Если токены найдены и валидны, инициализируем их через store
      if (accessToken && refreshToken) {
        refreshStore.setAccessToken(accessToken);
        refreshStore.setRefreshToken(refreshToken);
        console.log('TokenRefresh: Токены успешно инициализированы');
      }
      
      // Проверяем нужно ли обновление
      if (isTokenExpiringSoon(accessToken) && shouldRefreshToken()) {
        console.log('TokenRefresh: Токен скоро истекает, обновляем');
        await refreshToken(refreshStore);
      }
    };

    const startTokenRefreshInterval = () => {
      // Предотвращаем многократное создание интервала
      if (isInitialized) return;
      isInitialized = true;
      
      console.log('TokenRefresh: Запуск интервала проверки токенов');
      
      // При старте приложения проверяем токен однократно
      // Запускаем начальную проверку с небольшой задержкой 
      // чтобы дать другим компонентам инициализироваться
      setTimeout(() => {
        checkAndInitTokens();
      }, 500);

      // Устанавливаем интервал для регулярных проверок
      refreshTokenInterval = setInterval(async () => {
        const refreshStore = useRefreshStore(pinia);
        const accessToken = refreshStore.accessToken;
        const refreshToken = refreshStore.refreshToken;

        // Проверяем наличие токенов
        if (!accessToken || !refreshToken) return;
        
        // Проверяем валидность токенов
        if (!isRefreshTokenValid(refreshToken)) {
          console.log('TokenRefresh: Refresh token невалиден, очищаем токены');
          refreshStore.clearTokens();
          return;
        }

        if (isTokenExpiringSoon(accessToken) && shouldRefreshToken()) {
          await refreshToken(refreshStore);
        }
      }, CHECK_INTERVAL);
    };

    const stopTokenRefreshInterval = () => {
      if (refreshTokenInterval) {
        clearInterval(refreshTokenInterval);
        isInitialized = false;
        console.log('TokenRefresh: Интервал проверки токенов остановлен');
      }
    };

    // Создаем глобальную функцию проверки и обновления токена
    app.config.globalProperties.$refreshTokenIfNeeded = async () => {
      const refreshStore = useRefreshStore(pinia);
      const accessToken = refreshStore.accessToken;
      const refreshToken = refreshStore.refreshToken;
      
      // Проверяем валидность токенов перед попыткой обновления
      if (!accessToken || !refreshToken || !isRefreshTokenValid(refreshToken)) {
        console.log('TokenRefresh: Токены отсутствуют или невалидны, очищаем данные аутентификации');
        refreshStore.clearTokens();
        return;
      }
      
      if (isTokenExpiringSoon(accessToken) && shouldRefreshToken()) {
        await refreshToken(refreshStore);
      }
    };
    
    // Добавляем глобальную функцию для ручной инициализации токенов
    app.config.globalProperties.$initializeTokens = async () => {
      await checkAndInitTokens();
    };

    app.mixin({ 
      mounted() {
        if (this.$options.name === 'App') {
          console.log('TokenRefresh: Интервал обновления токена запущен');
          startTokenRefreshInterval();
        }
      },
      beforeUnmount() {
        if (this.$options.name === 'App') {
          console.log('TokenRefresh: Интервал обновления токена остановлен');
          stopTokenRefreshInterval();
        }
      },
    });
  },
};