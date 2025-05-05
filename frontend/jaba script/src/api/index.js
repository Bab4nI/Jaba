// src/api/index.js
import axios from 'axios'
import cache from './cache'

// Настройки времени кэширования (в минутах)
const CACHE_SETTINGS = {
  default: 5,
  profile: 30,
  courses: 30,
  modules: 30,
  lessons: 15,
  contents: 10,
  refreshToken: 5 // Минимальное время между обновлениями токена
}

// Ключ для сохранения времени последнего обновления токена
const LAST_TOKEN_REFRESH_KEY = 'last_token_refresh';

// Последнее обновление токена
let lastTokenRefresh = parseInt(localStorage.getItem(LAST_TOKEN_REFRESH_KEY)) || 0;

// Флаг для отслеживания текущего обновления токена
let isRefreshingToken = false;
// Пендинг запросы, ожидающие обновления токена
let refreshSubscribers = [];

// Получаем базовый URL для API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Проверка валидности JWT токена
const isValidJWT = (token) => {
  if (!token || token === 'undefined' || token === 'null') {
    console.log('❌ API.isValidJWT: Токен пустой или невалиден');
    return false;
  }
  
  try {
    // Проверяем тип токена
    if (typeof token !== 'string') {
      console.log(`❌ API.isValidJWT: Токен имеет неверный тип: ${typeof token}`);
      return false;
    }
    
    // Токен JWT должен состоять из 3 частей, разделенных точками
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.log('❌ API.isValidJWT: Токен не состоит из 3 частей');
      return false;
    }
    
    // Пытаемся декодировать payload
    const payload = JSON.parse(atob(parts[1]));
    
    // Проверяем срок действия токена
    if (payload.exp) {
      const expDate = new Date(payload.exp * 1000);
      const now = new Date();
      
      if (now >= expDate) {
        console.log(`❌ API.isValidJWT: Токен истек (exp: ${expDate.toISOString()}, now: ${now.toISOString()})`);
        return false;
      }
      
      // Добавим вывод времени до истечения токена
      const timeToExpiry = Math.round((expDate - now) / 1000 / 60);
      console.log(`✅ API.isValidJWT: Токен действителен еще ${timeToExpiry} минут`);
    }
    
    return true;
  } catch (e) {
    console.error('❌ API.isValidJWT: Ошибка при проверке JWT токена:', e);
    return false;
  }
};

// Функция для оповещения пендинг запросов о новом токене
const onTokenRefreshed = (newToken) => {
  console.log(`🔄 API: Оповещаем ${refreshSubscribers.length} ожидающих запросов о новом токене`);
  refreshSubscribers.forEach(callback => callback(newToken));
  refreshSubscribers = [];
};

// Функция для добавления пендинг запроса в очередь
const addRefreshSubscriber = (callback) => {
  console.log('🔄 API: Добавляем запрос в очередь ожидания токена');
  refreshSubscribers.push(callback);
};

// Создаем axios инстанс с базовыми настройками
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Подключаем кэширование
cache.setupAxiosCaching(api);

// Интерцептор запросов - добавляет токен к каждому запросу
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    
    if (token) {
      // Добавляем проверку токена перед отправкой
      if (isValidJWT(token)) {
        console.log(`🔄 API: Добавляем токен авторизации к запросу ${config.url}`);
        config.headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn(`⚠️ API: Невалидный токен при запросе на ${config.url}, не добавляем заголовок`);
        // Не добавляем заголовок если токен невалиден
        // Это вызовет 401 и запустит обновление токена
      }
    } else {
      console.log(`🔄 API: Запрос на ${config.url} без токена авторизации`);
    }
    
    // Кэширование для GET запросов
    if (config.method === 'get') {
      // Определяем подходящее время кэширования по URL
      let cacheTime = CACHE_SETTINGS.default;
      
      if (config.url.includes('/profile')) {
        cacheTime = CACHE_SETTINGS.profile;
      } else if (config.url.includes('/contents')) {
        cacheTime = CACHE_SETTINGS.contents;
      } else if (config.url.includes('/lessons')) {
        cacheTime = CACHE_SETTINGS.lessons;
      } else if (config.url.includes('/modules')) {
        cacheTime = CACHE_SETTINGS.modules;
      } else if (config.url.includes('/courses')) {
        cacheTime = CACHE_SETTINGS.courses;
      }
      
      // Настраиваем кэширование
      config.cache = {
        maxAge: cacheTime * 60 * 1000 // в миллисекундах
      };
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Интерцептор ответов - обрабатывает ошибки и обновляет токен при необходимости
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Обрабатываем 401 ошибки (неавторизован)
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log(`🔄 API: Получен 401 при запросе на ${originalRequest.url}, пробуем обновить токен`);
      
      // Если запрос уже обновляет токен
      if (isRefreshingToken) {
        console.log('🔄 API: Уже идет обновление токена, добавляем запрос в очередь');
        // Возвращаем Promise, который будет разрешен, когда токен обновится
        return new Promise((resolve) => {
          addRefreshSubscriber((newToken) => {
            console.log(`🔄 API: Повторяем запрос на ${originalRequest.url} с новым токеном`);
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            resolve(api(originalRequest));
          });
        });
      }
      
      // Проверяем наличие и валидность refresh токена
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        console.log('❌ API: Refresh token отсутствует');
        clearAuthTokens();
        return Promise.reject(error);
      }
      
      if (!isValidJWT(refreshToken)) {
        console.log('❌ API: Refresh token невалиден');
        clearAuthTokens();
        return Promise.reject(error);
      }
      
      // Предотвращаем множественные запросы на обновление токена
      const currentTime = Date.now();
      const timeSinceLastRefresh = currentTime - lastTokenRefresh;
      console.log(`🔄 API: Последнее обновление токена было ${Math.round(timeSinceLastRefresh / 1000)} секунд назад`);
      
      if (timeSinceLastRefresh < CACHE_SETTINGS.refreshToken * 60 * 1000) {
        // Если был недавний запрос на обновление токена, используем существующий токен
        const newToken = localStorage.getItem('access_token');
        if (newToken && isValidJWT(newToken)) {
          console.log(`🔄 API: Используем существующий токен для запроса на ${originalRequest.url}`);
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          return api(originalRequest);
        }
      }

      originalRequest._retry = true;
      isRefreshingToken = true;
      
      try {
        console.log('🔄 API: Отправляем запрос на обновление токена');
        lastTokenRefresh = Date.now();
        localStorage.setItem(LAST_TOKEN_REFRESH_KEY, lastTokenRefresh.toString());
        
        // Проверяем тип и структуру токена
        if (typeof refreshToken !== 'string') {
          console.error(`❌ API: Refresh token имеет неверный тип: ${typeof refreshToken}`);
          clearAuthTokens();
          return Promise.reject(new Error('Invalid refresh token type'));
        }
        
        if (refreshToken.length < 20) {
          console.error(`❌ API: Refresh token слишком короткий: ${refreshToken.length} символов`);
          clearAuthTokens();
          return Promise.reject(new Error('Invalid refresh token length'));
        }
        
        console.log(`🔄 API: Используем refresh token: ${refreshToken.substring(0, 15)}...`);
        
        const response = await axios.post(
          `${API_BASE_URL}/token/refresh/`,
          { refresh: refreshToken },
          {
            headers: {
              'Content-Type': 'application/json'
            }
          }
        )
        
        if (!response.data || !response.data.access) {
          console.error('❌ API: Сервер вернул ответ, но без access токена', response.data);
          throw new Error('No access token in response');
        }
        
        const newAccessToken = response.data.access;
        
        // Проверяем тип и валидность полученного токена
        if (typeof newAccessToken !== 'string') {
          console.error(`❌ API: Получен access token неверного типа: ${typeof newAccessToken}`);
          throw new Error('Invalid access token type in response');
        }
        
        if (!isValidJWT(newAccessToken)) {
          console.error('❌ API: Получен невалидный access token');
          throw new Error('Invalid access token in response');
        }
        
        console.log('✅ API: Токен успешно обновлен, новый токен:', newAccessToken.substring(0, 15) + '...');
        localStorage.setItem('access_token', newAccessToken);
        
        // Устанавливаем новый токен для текущего запроса
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        
        // Оповещаем всех подписчиков о новом токене
        onTokenRefreshed(newAccessToken);
        
        isRefreshingToken = false;
        return api(originalRequest);
      } catch (refreshError) {
        console.error('❌ API: Ошибка при обновлении токена:', refreshError);
        console.log('Детали запроса: refresh token =', refreshToken ? refreshToken.substring(0, 15) + '...' : 'null');
        if (refreshError.response) {
          console.log('Статус ответа:', refreshError.response.status);
          console.log('Данные ответа:', refreshError.response.data);
        }
        clearAuthTokens();
        isRefreshingToken = false;
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
)

// Функция для очистки токенов аутентификации
const clearAuthTokens = () => {
  console.warn('⚠️ API: Очищаем токены авторизации');
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem(LAST_TOKEN_REFRESH_KEY);
};

// Метод для принудительного сброса кэша
api.invalidateCache = (pattern = null) => {
  if (pattern) {
    // Удаляем кэш по шаблону URL
    const keys = Object.keys(localStorage)
      .filter(key => key.startsWith('api_cache_') && key.includes(pattern));
    
    console.log(`🔄 API: Инвалидация кэша по шаблону "${pattern}", найдено ${keys.length} ключей`);
    keys.forEach(key => localStorage.removeItem(key));
  } else {
    // Сбрасываем весь кэш
    console.log('🔄 API: Полная инвалидация кэша');
    cache.clear();
  }
}

// Метод для инвалидации кэша профиля
api.invalidateProfileCache = () => {
  console.log('🔄 API: Инвалидация кэша профиля');
  api.invalidateCache('/profile');
}

export default api;