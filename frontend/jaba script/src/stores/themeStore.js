import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

// Ключ для хранения в localStorage
const THEME_STORAGE_KEY = 'theme';

export const useThemeStore = defineStore('theme', () => {
  // Get theme from localStorage or default to light
  const isDarkMode = ref(localStorage.getItem(THEME_STORAGE_KEY) === 'dark')
  
  // Функция применения темы к документу
  const applyTheme = (isDark) => {
    if (isDark) {
      document.documentElement.classList.add('dark-theme')
    } else {
      document.documentElement.classList.remove('dark-theme')
    }
  }
  
  // Apply theme on store initialization
  applyTheme(isDarkMode.value)
  
  // Наблюдаем за изменениями темы и сохраняем в localStorage
  watch(isDarkMode, (newValue) => {
    localStorage.setItem(THEME_STORAGE_KEY, newValue ? 'dark' : 'light')
    applyTheme(newValue)
  })
  
  // Function to toggle theme
  function toggleTheme() {
    isDarkMode.value = !isDarkMode.value
  }
  
  // Функция для явной установки темы
  function setTheme(isDark) {
    isDarkMode.value = isDark
  }
  
  // Функция для добавления слушателя событий изменения темы из других вкладок
  function setupStorageListener() {
    window.addEventListener('storage', (event) => {
      if (event.key === THEME_STORAGE_KEY) {
        const newTheme = event.newValue === 'dark'
        if (isDarkMode.value !== newTheme) {
          isDarkMode.value = newTheme
        }
      }
    })
  }
  
  // Инициализация слушателя при создании хранилища
  setupStorageListener()
  
  return {
    isDarkMode,
    toggleTheme,
    setTheme
  }
}) 