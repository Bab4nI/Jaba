import { createRouter, createWebHistory } from 'vue-router';
import { authRoutes } from './authRoutes';
import { courseRoutes } from './courseRoutes';
import { passwordRoutes } from './passwordRoutes';
import { mainRoutes } from './mainRoutes';

const routes = [
  ...mainRoutes,
  ...authRoutes,
  ...courseRoutes,
  ...passwordRoutes,
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router; 