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
      <div @click="toggleTheme" class="theme-toggle" :class="{ 'dark': themeStore.isDarkMode }">
        <transition name="theme-icon" mode="out-in">
          <svg v-if="themeStore.isDarkMode" key="moon" class="main-logo" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21.5 14.0784C20.3003 14.9227 18.8559 15.4051 17.3021 15.4051C13.0399 15.4051 9.58203 11.9472 9.58203 7.68503C9.58203 6.13126 10.0644 4.68683 10.9087 3.48715C7.32868 4.2755 4.58203 7.45178 4.58203 11.3234C4.58203 15.8862 8.28929 19.5935 12.852 19.5935C16.7236 19.5935 19.8999 16.8468 20.6883 13.2668L21.5 14.0784Z" fill="#F5F9F8" stroke="#F5F9F8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M18.5 4.5L19.5 5.5" stroke="#F5F9F8" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M20 8.5H21.5" stroke="#F5F9F8" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M15 2.5V4" stroke="#F5F9F8" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <svg v-else key="sun" class="main-logo" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 17C14.7614 17 17 14.7614 17 12C17 9.23858 14.7614 7 12 7C9.23858 7 7 9.23858 7 12C7 14.7614 9.23858 17 12 17Z" fill="#24222F"/>
            <path d="M12 1V3" stroke="#24222F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 21V23" stroke="#24222F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4.22 4.22L5.64 5.64" stroke="#24222F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M18.36 18.36L19.78 19.78" stroke="#24222F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M1 12H3" stroke="#24222F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M21 12H23" stroke="#24222F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4.22 19.78L5.64 18.36" stroke="#24222F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M18.36 5.64L19.78 4.22" stroke="#24222F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </transition>
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

const toggleTheme = () => {
  // Add class to body for global theme detection
  document.body.classList.toggle('dark-theme', !themeStore.isDarkMode);
  themeStore.toggleTheme();
};

onMounted(async () => {
  // Set initial body class
  document.body.classList.toggle('dark-theme', themeStore.isDarkMode);
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
  transition: background-color 0.5s cubic-bezier(0.22, 1, 0.36, 1), color 0.5s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.5s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

/* .header-section::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(to right, #a094b8, #575667);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.header-section:hover::after {
  transform: scaleX(1);
} */

.header-section.dark-theme {
  background: #2a2a36;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.2);
}

.logo-link {
  text-decoration: none;
  position: relative;
  overflow: hidden;
}

.main-title-text-style {
  margin: 0;
  font: 400 36px Helvetica, Arial, sans-serif;
  color: #24222f;
  transition: color 0.5s cubic-bezier(0.22, 1, 0.36, 1), text-shadow 0.5s ease;
}

.dark-theme .main-title-text-style {
  color: #f5f9f8;
  text-shadow: 0 0 15px rgba(245, 249, 248, 0.3);
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
  transition: color 0.4s ease, transform 0.3s ease;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 100%;
  height: 2px;
  background: #a094b8;
  transform: scaleX(0);
  transform-origin: center;
  transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.nav-link:hover::after {
  transform: scaleX(1);
}

.dark-theme .nav-link {
  color: #f5f9f8;
}

.vertical-divider {
  width: 1px;
  height: 29px;
  background: #24222f;
  transition: background-color 0.5s ease, transform 0.5s ease;
}

.dark-theme .vertical-divider {
  background: #f5f9f8;
}

.main-logo {
  width: 42px;
  height: 40px;
  object-fit: cover;
  transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.1));
}

.dark-theme .main-logo {
  filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.2));
}

.theme-toggle {
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  background: rgba(160, 148, 184, 0.1);
  border-radius: 50%;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  width: 60px;
  height: 60px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
}

.theme-toggle.dark {
  background: rgba(42, 42, 54, 0.7);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(245, 249, 248, 0.2);
}

.theme-toggle::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(160, 148, 184, 0.3) 0%, transparent 70%);
  opacity: 0;
  transform: scale(0);
  transition: opacity 0.4s ease, transform 0.4s ease;
  border-radius: 50%;
}

.theme-toggle:hover::before {
  opacity: 1;
  transform: scale(1.5);
}

.theme-toggle:hover {
  transform: scale(1.1) rotate(15deg);
}

.theme-toggle:active {
  transform: scale(0.95);
}

/* Add hover effects */
.nav-link:hover {
  color: #a094b8;
  transform: translateY(-2px);
}

.dark-theme .nav-link:hover {
  color: #a094b8;
}

/* Theme icon transition */
.theme-icon-enter-active,
.theme-icon-leave-active {
  transition: opacity 0.3s ease, transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.theme-icon-enter-from,
.theme-icon-leave-to {
  opacity: 0;
  transform: scale(0.7) rotate(-30deg);
}

/* Add global styles for images with deep selector */
:deep(img) {
  opacity: 0.85;
  transition: opacity 0.4s ease, filter 0.4s ease;
}

:deep(.dark-theme img) {
  filter: brightness(0.9) contrast(1.05);
}

@keyframes theme-fade {
  0% { opacity: 0; transform: scale(0.96); }
  100% { opacity: 1; transform: scale(1); }
}

.header-section {
  animation: theme-fade 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
</style>