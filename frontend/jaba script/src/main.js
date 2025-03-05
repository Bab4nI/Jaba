import { createApp } from 'vue';
import App from './App.vue';
import '@/assets/fonts/fonts.css';
import router from '@/router';
import store from './store';
import tokenRefresh from './plugins/tokenRefresh';

const app = createApp(App);

app.config.productionTip = false;

app.use(tokenRefresh, { store });
app.use(store);
app.use(router);

app.mount('#app');