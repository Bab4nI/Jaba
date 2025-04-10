import { createRouter, createWebHistory } from 'vue-router';
import { useRefreshStore } from '@/stores/auth';
import Home from '@/views/Home.vue';
import SignUp from '@/views/SignUp.vue';
import SignIn from '@/views/SignIn.vue';
import Profile from '@/views/Profile.vue';
import Reset_password from './views/Reset_password.vue';
import New_password from './views/New_password.vue';
import Course from './views/Course.vue';

const routes = [
  { path: '/', component: Home },

  { path: '/New_password', component: New_password },

  { path: '/Reset_password', component: Reset_password },

  { path: '/Course', component: Course },
  
  {
    path: '/signup',
    name: 'SignUp',
    component: SignUp,
    beforeEnter: (to, from, next) => {
      const refreshStore = useRefreshStore();
      refreshStore.logout();
      next();
    },
  },

  {
    path: '/signin',
    name: 'SignIn',
    component: SignIn,
    beforeEnter: (to, from, next) => {
      const refreshStore = useRefreshStore();
      refreshStore.logout();
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