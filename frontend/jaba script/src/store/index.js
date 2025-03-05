import { createStore } from 'vuex';
import userStore from './userStore'; // Импортируем модуль userStore
import refresh from './refresh';

export default createStore({
  modules: {
    refresh,
    user: userStore, // Регистрируем модуль user
  },
});