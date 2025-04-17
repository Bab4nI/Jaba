<template>
  <div class="header-section">
    <router-link :to="header.home.link" class="logo-link">
      <p class="main-title-text-style">NetLab AI</p>
    </router-link>
    <div class="header-nav-container">
      <nav class="navigation-bar">
        <div class="main-nav-container">
          <router-link :to="header.home.link" class="nav-link">
            {{ header.home.title }}
          </router-link>
        </div>
        <div class="vertical-divider"></div>
        <router-link :to="header.courses.link" class="nav-link">
          {{ header.courses.title }}
        </router-link>
        <div class="vertical-divider"></div>
        <router-link :to="authLink.link" class="nav-link">
          {{ authLink.title }}
        </router-link>
      </nav>
      <img src="@/assets/images/moon_5370735.png" class="main-logo" alt="Theme toggle" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRefreshStore } from '@/stores/auth'; // Убедитесь, что путь правильный
import { header } from '@/config/header.js';

const refreshStore = useRefreshStore();
const isAuthenticated = computed(() => refreshStore.isAuthenticated);

const authLink = computed(() => {
  return isAuthenticated.value
    ? { title: 'Профиль', link: '/profile' }
    : { title: 'Войти', link: '/SignIn' };
});

onMounted(async () => {
  console.log('🔍 Инициализация заголовка: Проверка состояния авторизации');
  await refreshStore.ready();
  console.log('✅ Состояние авторизации после инициализации:', refreshStore.isAuthenticated);
});
</script>

<style scoped>
.header-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30px 29px 40px 99px;
  background: #f5f9f8;
}

.logo-link {
  text-decoration: none;
}

.main-title-text-style {
  margin: 0;
  font: 400 36px Helvetica, Arial, sans-serif;
  color: #24222f;
}

.header-nav-container {
  display: flex;
  align-items: center;
  gap: 58px;
}

.navigation-bar {
  display: flex;
  align-items: center;
  gap: 29.5px;
}

.nav-link {
  font: 400 20px 'Raleway', sans-serif;
  color: #24222f;
  text-decoration: none;
  padding: 3.5px 0 0;
}

.vertical-divider {
  width: 1px;
  height: 29px;
  background: #24222f;
}

.main-logo {
  width: 42px;
  height: 40px;
  object-fit: cover;
}

/* Add hover effects */
.nav-link:hover {
  color: #3a7bd5;
  text-decoration: underline;
}
</style>