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
                      <img
                        :src="eyeIcon"
                        class="password-input-icon"
                        @click="togglePasswordVisibility"
                      />
                    </div>
                    <p class="forgot-password-link">Забыли пароль?</p>
                  </div>
                </div>
                <button class="login-button" @click="validateForm">Войти</button>
              </div>
            </div>
            <img src="@/assets/images/login_day2.jpg" class="hero-image-container" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

// Иконки для пароля
import eyeOpen from '@/assets/images/psswd_open.png';
import eyeClosed from '@/assets/images/psswd_close.png';

// Состояния
const route = useRoute();
const router = useRouter();
const isPasswordVisible = ref(false);
const form = ref({
  email: '',
  password: '',
});

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

const eyeIcon = computed(() => 
  isPasswordVisible.value ? eyeOpen : eyeClosed
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
    window.location.href = 'http://localhost:5173/profile';
  }
};

// Логин с JWT
const login = async () => {
  try {
    const response = await axios.post('http://localhost:8000/api/token/', {
      email: form.value.email,
      password: form.value.password,
    });

    // Сохраняем токены в localStorage
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);

    // Перенаправление на страницу профиля
    window.location.href = 'http://localhost:5173/profile';
  } catch (error) {
    console.error('Ошибка при входе:', error);
    alert('Неверный email или пароль');
  }
};


// Получение заголовка с токеном
const getAuthHeader = () => {
  const accessToken = localStorage.getItem('access_token');
  return {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  };
};

// Обновление токена
const refreshToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await axios.post('http://localhost:8000/api/token/refresh/', {
      refresh: refreshToken,
    });

    // Сохраняем новый access токен
    localStorage.setItem('access_token', response.data.access);
  } catch (error) {
    console.error('Ошибка при обновлении токена:', error);
    logout();
  }
};
</script>

<style scoped>

.primary-text-content-style {
    flex: 0 0 auto;
    padding: 0;
    margin: 0;
    font: 400 20px Raleway, sans-serif;
    color: #24222f;
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
  background: #f5f9f8;
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
  background: #f5f9f8;
}
.main-title-text-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 36px Helvetica;
  color: #24222f;
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
  color: #24222f;
}
.vertical-divider {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 1px;
  height: 29px;
  border-left: 1px solid #24222f;
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
  color: #24222f;
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
  background: #ebefef;
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
  color: #24222f;
}
.welcome-message1 {
  padding: 0;
  margin: 0;
  margin-top: 11px;
  font: 300 16px Raleway, sans-serif;
  color: black;
}
.login-form-container {
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  margin-top: 80px;
}
.fullwidth-container {
  box-sizing: border-box;
  width: 100%;
}
.input-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: start;
  width: 100%;
  height: 44px;
  padding-left: 21px;
  font: 100 20px Raleway, sans-serif;
  color: black;
  background: #f5f9f8;
  border: none;
  border-radius: 20px;
}
.transparent-input {
  box-sizing: border-box;
  width: 100%;
  font: 100 20px Raleway, sans-serif;
  background: transparent;
  border: none;
  outline: none;
}
.input-style-571bd002::placeholder {
  color: black;
}
.password-prompt-container {
  box-sizing: border-box;
  width: 100%;
  margin-top: 27px;
}
.password-input-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 44px;
  padding-right: 13px;
  padding-left: 21px;
  background: #f5f9f8;
  border-radius: 20px;
}
.password-input-label {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 100 20px Raleway, sans-serif;
  color: black;
}
.password-input-icon {
  box-sizing: border-box;
  display: block;
  cursor: pointer;
  width: 24px;
  max-width: initial;
  height: 24px;
  border: none;
  object-fit: cover;
}
.forgot-password-link {
  padding: 0;
  padding-right: 22px;
  padding-left: 22px;
  margin: 0;
  margin-top: 19px;
  font: 300 16px Raleway, sans-serif;
  color: #a094b8;
  text-decoration-line: underline;
}
.login-button {
  box-sizing: border-box;
  display: block;
  flex: 0 0 auto;
  align-self: center;
  width: 286px;
  min-width: 286px;
  height: 51px;
  margin-top: 36px;
  font: 400 20px Raleway, sans-serif;
  color: #f5f9f8;
  cursor: pointer;
  background: #a094b8;
  border: none;
  border-radius: 20px;
}
.login-button:hover {
  background: #7c54ca;
  transition: 0.5s ease;
}
.hero-image-container {
  box-sizing: border-box;
  display: block;
  width: 407px;
  max-width: initial;
  height: 723px;
  border: none;
  border-radius: 35px;
  object-fit: cover;
}
</style>