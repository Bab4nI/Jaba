<template>
  <div class="sidebar-container">
    <div class="course-progress-stats-container">
      <div class="course-progress-container">
        <button
          :class="['sidebar-button', { 'active': activeTab === 'Мой профиль' }]" 
          @click="setActiveTab('Мой профиль')"
        >
          Мой профиль
        </button>
        <button 
          :class="['sidebar-button', { 'active': activeTab === 'Статистика прохождения курса' }]" 
          @click="setActiveTab('Статистика прохождения курса')"
        >
          Статистика прохождения курса
        </button>
        <button 
          v-if="userRole === 'admin'"
          :class="['sidebar-button', { 'active': activeTab === 'Пригласить пользователя' }]" 
          @click="setActiveTab('Пригласить пользователя')"
        >
          Пригласить пользователя
        </button>
        <button 
           v-if="userRole === 'admin'"
          :class="['sidebar-button', { 'active': activeTab === 'Управление новостями' }]" 
          @click="setActiveTab('Управление новостями')"
        >
          Управление новостями
        </button>
      </div>
    </div>
    <button class="logout-button" @click="logout">
      Выйти из аккаунта
    </button>
  </div>
</template>

<script setup>
// components/Sidebar.vue
import { computed, onMounted } from 'vue'; // Импортируем userStore
import { useRefreshStore } from '@/stores/auth'; // Импортируем refreshStore
import { useRouter } from 'vue-router';

import { useUserStore } from '@/stores/user';
const userStore = useUserStore();
const userRole = computed(() => {
  const role = userStore.role;
  console.log('Current user role in Sidebar:', role);
  return role;
});

const activeTab = computed(() => userStore.activeTab);
const refreshStore = useRefreshStore(); // Используем refreshStore
const router = useRouter();

// Use the debounced version to prevent multiple requests, but only if needed
onMounted(() => {
  // Only fetch if we don't already have user data with role
  if (!userStore.user || !userStore.role) {
    console.log('Sidebar: No cached user data, fetching profile');
    userStore.debouncedFetchProfile();
  } else {
    console.log('Sidebar: Using cached user data, role:', userStore.role);
  }
});

const logout = () => {
  refreshStore.logout(); // Используем logout из refreshStore
  router.push('/');
};

const setActiveTab = (tab) => {
  userStore.setActiveTab(tab);
};
</script>
  
<style scoped>
  .sidebar-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 20px;
    background: var(--form-background);
    border-radius: 15px;
    box-shadow: none;
    border: none;
    transition: background-color 0.3s ease;
    width: 240px; /* Slightly wider for long text */
  }
  
  .sidebar-button {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    width: 100%; /* Fill container width */
    height: auto;
    min-height: 47px;
    padding: 0 15px;
    margin: 10px 0;
    font: 400 16px Raleway, sans-serif;
    color: var(--text-color);
    background: var(--form-background);
    border: 2px solid var(--accent-color);
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
    text-align: left;
    white-space: normal;
    word-break: break-word;
    overflow: visible;
  }
  
  .sidebar-button:hover {
    background-color: var(--hover-background);
  }
  
  .sidebar-button.active {
    background-color: var(--accent-color);
    color: var(--footer-text);
    border-color: var(--accent-color);
  }
  
  .progress-indicator-text-style {
    margin-top: 20px;
    font: 400 16px Raleway, sans-serif;
    color: var(--error-color);
    cursor: pointer;
    transition: color 0.3s ease;
  }

  .logout-button {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    width: 100%; /* Fill container width */
    min-height: 47px;
    height: auto;
    padding: 0 15px;
    margin: 10px 0;
    font: 400 16px Raleway, sans-serif;
    color: var(--footer-text);
    background: #ff4d4d;
    border: 2px solid var(--accent-color);
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
    text-align: left;
    white-space: normal;
    word-break: break-word;
    overflow: visible;
  }

  .logout-button:hover{
    background: #eb2929;
  }
</style>