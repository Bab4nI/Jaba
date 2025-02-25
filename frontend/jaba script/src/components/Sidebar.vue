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
            :class="['sidebar-button', { 'active': activeTab === 'Прогресс прохождения курса' }]" 
            @click="setActiveTab('Прогресс прохождения курса')"
          >
            Прогресс прохождения курса
          </button>
          <button 
            :class="['sidebar-button', { 'active': activeTab === 'Статистика' }]" 
            @click="setActiveTab('Статистика')"
          >
            Статистика
          </button>
        </div>
      </div>
      <p class="progress-indicator-text-style">Выйти из аккаунта</p>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const activeTab = ref('Мой профиль');
  
  const setActiveTab = (tab) => {
    activeTab.value = tab;
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
  </style>