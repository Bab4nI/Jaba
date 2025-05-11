<template>
  <div id="app">
    <Header />
    <router-view></router-view>
  </div>
</template>

<script setup>
import Header from '@/components/Header.vue'; // Импортируем компонент Header
import '@/assets/css/themes.css'; // Import themes CSS
import { useThemeStore } from '@/stores/themeStore';
import { useUserStore } from '@/stores/user';
import { onMounted, onBeforeUnmount } from 'vue';

const themeStore = useThemeStore();
const userStore = useUserStore();

const setupSystemThemeWatcher = () => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  const handleThemeChange = (e) => {
    if (!localStorage.getItem('theme')) {
      themeStore.setTheme(e.matches);
    }
  };
  
  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', handleThemeChange);
  } else if (mediaQuery.addListener) {
    mediaQuery.addListener(handleThemeChange);
  }
  
  return () => {
    if (mediaQuery.removeEventListener) {
      mediaQuery.removeEventListener('change', handleThemeChange);
    } else if (mediaQuery.removeListener) {
      mediaQuery.removeListener(handleThemeChange);
    }
  };
};

let removeSystemThemeWatcher;
onMounted(() => {
  // Set up theme watcher
  removeSystemThemeWatcher = setupSystemThemeWatcher();
  
  // Initialize user profile if we have an access token
  if (localStorage.getItem('access_token')) {
    console.log('App: Initializing user profile on app start');
    // Check if we already have profile data, avoiding duplicate requests
    if (!userStore.user) {
      // Try to load from localStorage first
      const cachedData = localStorage.getItem('user_profile_data');
      if (cachedData) {
        try {
          console.log('App: Using cached profile data');
          // Load cached data - this will update the store but won't trigger API request
          const data = JSON.parse(cachedData);
          userStore.SET_USER_DATA(data);
        } catch (error) {
          console.error('App: Error parsing cached profile data', error);
        }
      }
      
      // Schedule a background refresh of profile data after a short delay
      setTimeout(() => {
        console.log('App: Background refresh of profile data');
        userStore.debouncedFetchProfile();
      }, 3000);
    }
  }
});

onBeforeUnmount(() => {
  if (removeSystemThemeWatcher) {
    removeSystemThemeWatcher();
  }
});
</script>


<style>
* {
  margin: 0px;
  box-sizing: border-box;
}

body {
  background-color: var(--background-color);
  color: var(--text-color);
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Add transitions to commonly used elements */
input, select, textarea, button, 
.card, .modal, .container, .item,
div[class*="background"], div[class*="container"],
div[class*="section"], div[class*="card"],
div[class*="modal"], div[class*="item"],
div[class*="header"], div[class*="footer"] {
  transition: background-color 0.3s ease, 
              color 0.3s ease, 
              border-color 0.3s ease, 
              box-shadow 0.3s ease;
}

a {
  all: unset;
  cursor: pointer;
  transition: color 0.3s ease;
}
</style>