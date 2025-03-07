// plugins/tokenRefresh.js
export default {
  install(app, { store }) {
    let refreshTokenInterval = null;

    const startTokenRefreshInterval = () => {
      refreshTokenInterval = setInterval(async () => {
        const accessToken = store.state.refresh.accessToken;

        if (accessToken) {
          try {
            const tokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
            const expirationTime = tokenPayload.exp * 1000;
            const currentTime = Date.now();

            if (expirationTime - currentTime < 60000) {
              console.log('Access Token скоро истечёт, обновляем...');
              await store.dispatch('refresh/refreshToken');
            }
          } catch (error) {
            console.error('Ошибка при разборе accessToken:', error);
            store.dispatch('refresh/logout');
          }
        }
      }, 30000);
    };

    const stopTokenRefreshInterval = () => {
      if (refreshTokenInterval) {
        clearInterval(refreshTokenInterval);
      }
    };

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