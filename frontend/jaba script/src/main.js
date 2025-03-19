//main.js
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import '@/assets/fonts/fonts.css';
import router from '@/router';
import tokenRefresh from './plugins/tokenRefresh';

const app = createApp(App);
const pinia = createPinia();

app.config.productionTip = false;

app.use(pinia);
app.use(tokenRefresh, { pinia });
app.use(router);

app.mount('#app');