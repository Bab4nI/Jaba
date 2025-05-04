import { useRefreshStore } from '@/stores/auth';
import SignUp from '@/views/SignUp.vue';
import SignIn from '@/views/SignIn.vue';
import Profile from '@/views/Profile.vue';

export const authRoutes = [
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