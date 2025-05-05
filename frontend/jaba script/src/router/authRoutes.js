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
      // Проверяем, есть ли у пользователя действующие токены
      const accessToken = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      
      // Если есть действующие токены, перенаправляем на профиль
      if (accessToken && refreshToken) {
        console.log('Перенаправление: уже авторизован, перенаправляем на профиль');
        return next('/profile');
      }
      
      // Иначе очищаем токены и показываем страницу входа
      refreshStore.clearTokens();
      next();
    },
  },
  { 
    path: '/profile', 
    component: Profile,
    beforeEnter: async (to, from, next) => {
      const refreshStore = useRefreshStore();
      
      // Проверяем наличие токенов
      const accessToken = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!accessToken || !refreshToken) {
        console.log('Перенаправление: нет токенов, перенаправляем на вход');
        return next('/signin');
      }
      
      // Инициализируем токены в store
      try {
        // Инициализируем и проверяем токены
        const isValid = await refreshStore.ready();
        
        if (!isValid) {
          console.log('Перенаправление: невалидные токены, перенаправляем на вход');
          return next('/signin');
        }
        
        // Если токены валидны, продолжаем навигацию к профилю
        return next();
      } catch (error) {
        console.error('Ошибка при проверке токенов:', error);
        return next('/signin');
      }
    }
  },
]; 