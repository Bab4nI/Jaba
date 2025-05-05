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
import { onMounted, onBeforeUnmount } from 'vue';

const themeStore = useThemeStore();

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
  removeSystemThemeWatcher = setupSystemThemeWatcher();
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