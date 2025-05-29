<template>
  <div style="display: inline-block; width: 1505px" data-ignore="used only for top most containter width">
    <div class="main-content-container">
      <div class="login-container1">
        <div class="welcome-message-container">
          <div class="welcome-login-container">
            <div class="login-container">
              <div class="password-prompt-container1">
                <p class="welcome-message">С возвращением!</p>
                <p class="welcome-message1">Войдите, чтобы продолжить</p>
              </div>
              <div class="login-form-container">
                <div class="password-prompt-container1">
                  <div class="fullwidth-container">
                    <div class="input-container">
                      <input
                        v-model="form.email"
                        type="email"
                        class="transparent-input"
                        placeholder="Введите почту"
                      />
                    </div>
                  </div>
                  <div class="password-prompt-container">
                    <div class="password-input-container">
                      <input
                        v-model="form.password"
                        :type="passwordFieldType"
                        class="transparent-input"
                        placeholder="Введите пароль"
                      />
                      <span @click="togglePasswordVisibility" class="password-eye">
                        <svg
                          v-if="isPasswordVisible"
                          :class="['eye-svg', isDarkTheme ? 'dark' : 'light']"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                        >
                          <path
                            d="M1.5 12C3.5 7 8 4 12 4C16 4 20.5 7 22.5 12C20.5 17 16 20 12 20C8 20 3.5 17 1.5 12Z"
                            :stroke="isDarkTheme ? '#fff' : '#222'"
                            stroke-width="2"
                            fill="none"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                          />
                          <circle
                            cx="12"
                            cy="12"
                            r="3"
                            :stroke="isDarkTheme ? '#fff' : '#222'"
                            stroke-width="2"
                            fill="none"
                          />
                          <circle
                            cx="12"
                            cy="12"
                            r="1.2"
                            :fill="isDarkTheme ? '#fff' : '#222'"
                          />
                        </svg>
                        <svg
                          v-else
                          :class="['eye-svg', isDarkTheme ? 'dark' : 'light']"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                        >
                          <path
                            d="M1.5 12C3.5 7 8 4 12 4C16 4 20.5 7 22.5 12C20.5 17 16 20 12 20C8 20 3.5 17 1.5 12Z"
                            :stroke="isDarkTheme ? '#fff' : '#222'"
                            stroke-width="2"
                            fill="none"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                          />
                          <circle
                            cx="12"
                            cy="12"
                            r="3"
                            :stroke="isDarkTheme ? '#fff' : '#222'"
                            stroke-width="2"
                            fill="none"
                          />
                          <line
                            x1="5"
                            y1="19"
                            x2="19"
                            y2="5"
                            :stroke="isDarkTheme ? '#fff' : '#222'"
                            stroke-width="2"
                            stroke-linecap="round"
                          />
                        </svg>
                      </span>
                    </div>
                    <p class="forgot-password-link"><router-link to="/Reset_password">Забыли пароль?</router-link></p>
                  </div>
                </div>
                <button class="login-button" @click="validateForm">Войти</button>
              </div>
            </div>
            <img :src="isDarkTheme ? loginNightImage : loginDayImage" class="hero-image-container" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// views/SignIn
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useRefreshStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/themeStore'

// Иконки для пароля
// Удаляю импорты PNG глазика
// import eyeOpen from '@/assets/images/psswd_open.png';
// import eyeClosed from '@/assets/images/psswd_close.png';
import loginDayImage from '@/assets/images/login_day2.jpg';
import loginNightImage from '@/assets/images/login_night2.jpg';

// Состояния
const route = useRoute();
const router = useRouter();
const refreshStore = useRefreshStore();
const themeStore = useThemeStore();
const isPasswordVisible = ref(false);
const form = ref({
  email: '',
  password: '',
});

// Определение текущей темы
const isDarkTheme = computed(() => themeStore.isDarkMode);

// Заполнение полей из query параметров
onMounted(() => {
  form.value = {
    email: route.query.email || '',
    password: '',
  };

  // Проверка авторизации при загрузке компонента
  checkAuth();
});

// Логика пароля
const passwordFieldType = computed(() => 
  isPasswordVisible.value ? 'text' : 'password'
);

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value;
};

// Валидация формы
const validateForm = () => {
  if (!form.value.email) {
    alert('Поле электронной почты обязательно для заполнения');
    return false;
  }
  if (!form.value.password) {
    alert('Пароль обязателен для заполнения');
    return false;
  }
  login();
  return true;
};

// Проверка авторизации через JWT
const checkAuth = () => {
  const accessToken = localStorage.getItem('access_token');
  if (accessToken) {
    window.location.href = '/profile';
  }
};

// Логин с JWT
const login = async () => {
  try {
    console.log('Отправляем запрос на авторизацию...');
    const response = await axios.post('http://localhost:8000/api/token/', 
      {
        email: form.value.email,
        password: form.value.password,
        timestamp: Date.now(),
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    // Проверяем ответ сервера
    if (!response.data) {
      console.error('Ошибка при входе: ответ сервера пустой');
      alert('Сервер вернул пустой ответ. Попробуйте позже.');
      return;
    }

    if (!response.data.access || !response.data.refresh) {
      console.error('Ошибка при входе: ответ сервера не содержит токены', response.data);
      alert('Сервер вернул неполный ответ. Попробуйте позже.');
      return;
    }

    // Сохраняем токены через refreshStore
    console.log('Получены токены, сохраняем...');
    console.log(`Access token: ${response.data.access.substring(0, 15)}...`);
    console.log(`Refresh token: ${response.data.refresh.substring(0, 15)}...`);
    
    // Убедимся, что токены имеют правильный формат
    if (typeof response.data.access !== 'string' || typeof response.data.refresh !== 'string') {
      console.error('Ошибка при входе: токены имеют неверный формат');
      alert('Получены токены в неверном формате. Попробуйте позже.');
      return;
    }

    refreshStore.setAccessToken(response.data.access);
    refreshStore.setRefreshToken(response.data.refresh);

    // Инициализируем токены в refreshStore
    await refreshStore.ready();

    // Перенаправление на страницу профиля
    console.log('Авторизация успешна, перенаправляем на профиль');
    window.location.href = '/profile';
  } catch (error) {
    console.error('Ошибка при входе:', error);
    if (error.response) {
      console.log('Статус ответа:', error.response.status);
      console.log('Данные ответа:', error.response.data);
    }
    alert('Неверный email или пароль');
  }
};
</script>

<style scoped>

.primary-text-content-style {
    flex: 0 0 auto;
    padding: 0;
    margin: 0;
    font: 400 20px Raleway, sans-serif;
    color: var(--text-color);
}
.primary-text-content-style:hover {
    text-decoration: underline;
    text-underline-offset: 5px;
}

.main-content-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  min-width: 1480px;
  background: var(--background-color);
}
.center-aligned-flex-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
}
.header-section {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  gap: 8px;
  align-items: flex-end;
  justify-content: space-between;
  padding: 30px 29px 40px 99px;
  background: var(--background-color);
}
.main-title-text-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 36px Helvetica;
  color: var(--text-color);
}
.horizontal-flex-container {
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
}
.header-nav {
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  gap: 29.5px;
  align-items: center;
  justify-content: flex-start;
}
.main-heading-text-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: var(--text-color);
}
.vertical-divider {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 1px;
  height: 29px;
  border-left: 1px solid var(--text-color);
}
.vertical-menu-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  width: 54px;
  padding-top: 3.5px;
}
.login-heading-text-style {
  flex: 0 0 auto;
  align-self: center;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: var(--text-color);
}
.main-navigation-icon {
  box-sizing: border-box;
  display: block;
  width: 42px;
  max-width: initial;
  height: 40px;
  margin-left: 56px;
  border: none;
  object-fit: cover;
}
.login-container1 {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
.welcome-message-container {
  box-sizing: border-box;
  min-width: 1280px;
  padding-top: 29px;
  padding-bottom: 70px;
}
.welcome-login-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 29px 30px 30px 62px;
  background: var(--form-background);
  border-radius: 35px;
}
.login-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  min-width: 504px;
}
.password-prompt-container1 {
  flex: 0 0 auto;
}
.welcome-message {
  padding: 0;
  margin: 0;
  font: 700 32px Raleway, sans-serif;
  color: var(--text-color);
}
.welcome-message1 {
  padding: 0;
  margin: 0;
  margin-top: 11px;
  font: 300 16px Raleway, sans-serif;
  color: var(--secondary-text);
}
.login-form-container {
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  margin-top: 29px;
}
.fullwidth-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  width: 100%;
}
.input-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  padding: 15px 19px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}
.password-prompt-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  margin-top: 20px;
}
.password-input-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 15px 19px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}
.transparent-input {
  flex: 1 1 auto;
  min-width: 0;
  width: 100%;
  min-height: 26px;
  height: 100%;
  padding: 0;
  margin: 0;
  font: 400 16px Raleway, sans-serif;
  color: var(--text-color);
  background-color: transparent;
  border: none;
  outline: none;
}
.transparent-input::placeholder {
  color: var(--secondary-text);
  opacity: 0.7;
}
.password-input-icon {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 24px;
  max-width: initial;
  height: 24px;
  margin-left: 12px;
  border: none;
  object-fit: cover;
  cursor: pointer;
}
.forgot-password-link {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  margin-top: 8px;
  margin-right: 8px;
  font: 300 14px Raleway, sans-serif;
  color: var(--text-color);
}
.forgot-password-link a {
  color: var(--accent-color);
  text-decoration: none;
}
.forgot-password-link a:hover {
  text-decoration: underline;
}
.login-button {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  height: 56px;
  margin-top: 20px;
  margin-bottom: 30px;
  padding: 15px 19px;
  font: 500 16px Raleway, sans-serif;
  color: var(--footer-text);
  background: var(--accent-color);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.login-button:hover {
  background: var(--hover-accent);
}
.hero-image-container {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 600px;
  max-width: initial;
  height: 488px;
  border: none;
  border-radius: 35px;
  object-fit: cover;
}

.success-message {
  color: #10b981; /* green */
  font-size: 14px;
  margin-top: 10px;
  text-align: center;
}

.error-message {
  color: var(--error-color);
  font-size: 14px;
  margin-top: 10px;
  text-align: center;
}

.eye-svg {
  cursor: pointer;
  transition: stroke 0.2s;
}
.eye-svg.light {
  stroke: #222;
}
.eye-svg.dark {
  stroke: #fff;
}
.password-eye {
  display: flex;
  align-items: center;
  margin-left: 12px;
}
</style>