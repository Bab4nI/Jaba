export default {
    install(app, { store }) {
      let refreshTokenInterval = null;
  
      const startTokenRefreshInterval = () => {
        refreshTokenInterval = setInterval(async () => {
          const accessToken = store.state.refresh.accessToken;
          if (accessToken) {
            const tokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
            const expirationTime = tokenPayload.exp * 1000;
            const currentTime = Date.now();
  
            if (expirationTime - currentTime < 60000) { // Если до истечения меньше 1 минуты
              await store.dispatch('refreshToken'); // Обновляем токен
            }
          }
        }, 30000); // Проверяем каждые 30 секунд
      };
  
      const stopTokenRefreshInterval = () => {
        if (refreshTokenInterval) {
          clearInterval(refreshTokenInterval);
        }
      };
  
      // Запускаем интервал при монтировании приложения
      app.mixin({
        mounted() {
          startTokenRefreshInterval();
        },
        beforeUnmount() {
          stopTokenRefreshInterval();
        },
      });
    },
  };