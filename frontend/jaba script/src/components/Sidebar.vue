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
    <button class="logout-button" @click="logout">
      Выйти из аккаунта
    </button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      activeTab: 'Мой профиль',
      refreshTokenInterval: null,
    };
  },
  methods: {
    setActiveTab(tab) {
      this.activeTab = tab;
    },
    async logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      this.$router.push('/signin');
    },
    async refreshToken() {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        this.logout();
        return;
      }

      try {
        const response = await axios.post('/api/token/refresh/', {
          refresh: refreshToken,
        });

        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
      } catch (error) {
        this.logout();
      }
    },
    startTokenRefreshInterval() {
      this.refreshTokenInterval = setInterval(() => {
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
          const tokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
          const expirationTime = tokenPayload.exp * 1000;
          const currentTime = Date.now();

          if (expirationTime - currentTime < 60000) { // Если до истечения токена осталось меньше минуты
            this.refreshToken();
          }
        }
      }, 30000); // Проверяем каждые 30 секунд
    },
  },
  mounted() {
    this.startTokenRefreshInterval();
  },
  beforeDestroy() {
    if (this.refreshTokenInterval) {
      clearInterval(this.refreshTokenInterval);
    }
  },
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