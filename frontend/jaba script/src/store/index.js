// store/index.js
import { createStore } from 'vuex';
import userStore from './userStore';
import refreshStore from './refresh';

export default createStore({
  modules: {
    refresh: refreshStore,
    userStore: userStore,
  },
});