import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import SignUp from '@/views/SignUp.vue';
import SignIn from '@/views/SignIn.vue';
import Profile from '@/views/Profile.vue';
import store from '@/store'; // Импортируйте хранилище Vuex

const routes = [
  { path: '/', component: Home, },
  {
    path: '/signup',
    name: 'SignUp',
    component: SignUp,
    beforeEnter: (to, from, next) => {
      store.dispatch('refresh/logout'); // Удаляем токены
      next();
    },
  },
  {
    path: '/signin',
    name: 'SignIn',
    component: SignIn ,
    beforeEnter: (to, from, next) => {
      store.dispatch('refresh/logout'); // Удаляем токены
      next();
    },
  },
  { path: '/profile', component: Profile },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;