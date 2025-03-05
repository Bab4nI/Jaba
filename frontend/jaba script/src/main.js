import { createApp } from 'vue';
import App from './App.vue';
import '@/assets/fonts/fonts.css';
import router from '@/router';
import store from './store'; // Хранилище Vuex
import tokenRefresh from './plugins/tokenRefresh'; // Плагин для обновления токена

const app = createApp(App);

// Отключаем production tip
app.config.productionTip = false;

// Используем плагин tokenRefresh
app.use(tokenRefresh, { store });
app.use(store);
app.use(router);

// Монтируем приложение
app.mount('#app');