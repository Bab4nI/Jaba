<template>
  <div class="header-section" :class="{ 'dark-theme': themeStore.isDarkMode }">
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
      <div @click="themeStore.toggleTheme" class="theme-toggle">
        <svg v-if="!themeStore.isDarkMode" class="main-logo" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21.53 15.93C20.6023 17.2669 19.3537 18.3392 17.9047 19.0499C16.4556 19.7606 14.8523 20.0886 13.2467 20.0006C11.6411 19.9126 10.0855 19.4115 8.72288 18.5469C7.36025 17.6824 6.2351 16.481 5.45308 15.0568C4.67106 13.6327 4.25776 12.0323 4.24935 10.4012C4.24095 8.77014 4.63767 7.16449 5.40464 5.73242C6.17161 4.30035 7.28383 3.08775 8.63748 2.20887C9.99112 1.32999 11.5422 0.814005 13.147 0.710001C12.3644 1.79783 11.9286 3.09325 11.8992 4.43002C11.8698 5.76679 12.2482 7.08009 12.9865 8.19895C13.7248 9.31782 14.7887 10.1866 16.0317 10.6832C17.2747 11.1798 18.6379 11.2835 19.947 10.98C20.5459 12.2573 20.7512 13.6633 20.5344 15.0328C20.3176 16.4022 19.6883 17.6773 18.73 18.7C20.1965 18.0303 21.4499 16.9705 22.35 15.63L21.53 15.93Z" fill="#24222F"/>
        </svg>
        <svg v-else class="main-logo" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="5" stroke="#F5F9F8" stroke-width="2"/>
          <path d="M12 2V4" stroke="#F5F9F8" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 20V22" stroke="#F5F9F8" stroke-width="2" stroke-linecap="round"/>
          <path d="M4 12L2 12" stroke="#F5F9F8" stroke-width="2" stroke-linecap="round"/>
          <path d="M22 12L20 12" stroke="#F5F9F8" stroke-width="2" stroke-linecap="round"/>
          <path d="M19.7782 4.22183L17.6569 6.34315" stroke="#F5F9F8" stroke-width="2" stroke-linecap="round"/>
          <path d="M6.34309 17.6569L4.22177 19.7782" stroke="#F5F9F8" stroke-width="2" stroke-linecap="round"/>
          <path d="M19.7782 19.7782L17.6569 17.6569" stroke="#F5F9F8" stroke-width="2" stroke-linecap="round"/>
          <path d="M6.34309 6.34315L4.22177 4.22183" stroke="#F5F9F8" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRefreshStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/themeStore';
import { header } from '@/config/header.js';

const refreshStore = useRefreshStore();
const themeStore = useThemeStore();
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
  transition: background-color 0.3s ease, color 0.3s ease;
}

.header-section.dark-theme {
  background: #2a2a36;
}

.logo-link {
  text-decoration: none;
}

.main-title-text-style {
  margin: 0;
  font: 400 36px Helvetica, Arial, sans-serif;
  color: #24222f;
  transition: color 0.3s ease;
}

.dark-theme .main-title-text-style {
  color: #f5f9f8;
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
  transition: color 0.3s ease;
}

.dark-theme .nav-link {
  color: #f5f9f8;
}

.vertical-divider {
  width: 1px;
  height: 29px;
  background: #24222f;
  transition: background-color 0.3s ease;
}

.dark-theme .vertical-divider {
  background: #f5f9f8;
}

.main-logo {
  width: 42px;
  height: 40px;
  object-fit: cover;
}

.theme-toggle {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.theme-toggle:hover {
  transform: scale(1.1);
}

/* Add hover effects */
.nav-link:hover {
  color: #a094b8;
  text-decoration: underline;
}

.dark-theme .nav-link:hover {
  color: #a094b8;
}
</style>