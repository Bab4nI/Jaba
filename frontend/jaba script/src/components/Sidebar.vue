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
      </div>
    </div>
    <button class="logout-button" @click="logout">
      Выйти из аккаунта
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

const store = useStore();
const router = useRouter();

// Получаем активную вкладку из хранилища
const activeTab = computed(() => store.state.userStore.activeTab);

// Получаем роль пользователя
const userRole = computed(() => store.state.userStore.role);

// Функция выхода
const logout = () => {
  store.dispatch('refresh/logout'); // Учитываем namespace модуля
  router.push('/'); // Возвращаем на главную
};

// Функция для переключения вкладки
const setActiveTab = (tab) => {
  store.dispatch('userStore/setActiveTab', tab); // Используем действие из хранилища
};
</script>
  
<style scoped>
  .sidebar-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 20px;
    background: #f5f9f8;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .sidebar-button {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    width: auto;
    min-width: 150px;
    height: 47px;
    padding: 0 20px;
    margin: 10px 0;
    font: 400 20px Raleway, sans-serif;
    color: #24222f;
    background: #f5f9f8;
    border: 2px solid #a094b8;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s ease, color 0.3s ease;
    text-align: left;
    white-space: nowrap;
  }
  
  .sidebar-button:hover {
    background-color: #e0e4e8;
  }
  
  .sidebar-button.active {
    background-color: #a094b8;
    color: #f5f9f8;
    border-color: #a094b8;
  }
  
  .progress-indicator-text-style {
    margin-top: 20px;
    font: 400 16px Raleway, sans-serif;
    color: #da1f38;
    cursor: pointer;
  }

  .logout-button {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    width: auto;
    min-width: 150px;
    height: 47px;
    padding: 0 20px;
    margin: 10px 0;
    font: 400 20px Raleway, sans-serif;
    color: #24222f;
    background: #ff4d4d;
    border: 2px solid #a094b8;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s ease, color 0.3s ease;
    text-align: left;
    white-space: nowrap;
  }

  .logout-button:hover{
    background: #eb2929;
  }
  </style>