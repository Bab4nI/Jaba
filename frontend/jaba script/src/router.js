import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import SignUp from '@/views/SignUp.vue';
import SignIn from '@/views/SignIn.vue';
import Profile from '@/views/Profile.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/signup', component: SignUp },
  { path: '/signin', component: SignIn },
  { path: '/profile', component: Profile },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;