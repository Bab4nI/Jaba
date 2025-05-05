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
          v-if="userRole === 'student'"
          :class="['sidebar-button', { 'active': activeTab === 'Прогресс прохождения курса' }]" 
          @click="setActiveTab('Прогресс прохождения курса')"
        >
          Прогресс прохождения курса
        </button>
        <button 
           v-if="userRole === 'admin'"
          :class="['sidebar-button', { 'active': activeTab === 'Статистика прохождения курса' }]" 
          @click="setActiveTab('Статистика прохождения курса')"
        >
          Статистика прохождения курса
        </button>
        <button 
           v-if="userRole === 'admin'"
          :class="['sidebar-button', { 'active': activeTab === 'Домашние задания' }]" 
          @click="setActiveTab('Домашние задания')"
        >
          Домашние задания
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
import { computed } from 'vue';
import { useUserStore } from '@/stores/user'; // Импортируем userStore
import { useRefreshStore } from '@/stores/auth'; // Импортируем refreshStore
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const refreshStore = useRefreshStore(); // Используем refreshStore
const router = useRouter();

const activeTab = computed(() => userStore.activeTab);
const userRole = computed(() => userStore.role);

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
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: background-color 0.3s ease;
    width: 210px; /* Fixed width for container */
  }
  
  .sidebar-button {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    width: 100%; /* Fill container width */
    height: 47px;
    padding: 0 15px;
    margin: 10px 0;
    font: 400 20px Raleway, sans-serif;
    color: var(--text-color);
    background: var(--form-background);
    border: 2px solid var(--accent-color);
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
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
    height: 47px;
    padding: 0 15px;
    margin: 10px 0;
    font: 400 20px Raleway, sans-serif;
    color: var(--footer-text);
    background: #ff4d4d;
    border: 2px solid var(--accent-color);
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .logout-button:hover{
    background: #eb2929;
  }
</style>