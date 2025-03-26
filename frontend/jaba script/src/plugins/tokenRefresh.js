// plugins/tokenRefresh.js
import { useRefreshStore } from '@/stores/auth';

export default {
  install(app, { pinia }) {
    let refreshTokenInterval = null;

    const startTokenRefreshInterval = () => {
      refreshTokenInterval = setInterval(async () => {
        const refreshStore = useRefreshStore(pinia);
        const accessToken = refreshStore.accessToken;
        const refreshToken = refreshStore.refreshToken;

        if (accessToken) {
          try {
            const tokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
            const expirationTime = tokenPayload.exp * 1000; // Время истечения в миллисекундах
            const currentTime = Date.now();

            console.log('Текущее время:', currentTime);
            console.log('Время истечения токена:', expirationTime);

            if (expirationTime - currentTime < 60000) { // Если до истечения меньше 60 секунд
              console.log('Access Token скоро истечёт, обновляем...');
              await refreshStore.refreshToken();
            }
          } catch (error) {
            console.error('Ошибка при разборе accessToken:', error);
            if (!refreshToken) {
              refreshStore.logout();
            }
          }
        }
      }, 30000); // Проверка каждые 30 секунд
    };

    const stopTokenRefreshInterval = () => {
      if (refreshTokenInterval) {
        clearInterval(refreshTokenInterval);
      }
    };

    app.mixin({ 
      mounted() {
        console.log('Интервал обновления токена запущен');
        startTokenRefreshInterval();
      },
      beforeUnmount() {
        console.log('Интервал обновления токена остановлен');
        stopTokenRefreshInterval();
      },
    });
  },
};