<template>
  <div style="display: inline-block; width: 1505px" data-ignore="used only for top most containter width">
    <div class="main-content-container">
      <div class="login-container1">
        <div class="welcome-message-container">
          <div class="welcome-login-container">
            <div class="login-container">
              <div class="password-prompt-container1">
                <p class="welcome-message">Восстановление пароля</p>
                <p class="welcome-message1">Введите email, чтобы получить ссылку для сброса пароля</p>
              </div>
              <div class="login-form-container">
                <div class="password-prompt-container1">
                  <div class="fullwidth-container">
                    <div class="input-container">
                      <input
                        v-model="email"
                        type="email"
                        class="transparent-input"
                        placeholder="Введите вашу почту"
                      />
                    </div>
                  </div>
                </div>
                <button 
                  class="login-button" 
                  @click="sendResetLink"
                  :disabled="loading"
                >
                  {{ loading ? 'Отправка...' : 'Отправить ссылку' }}
                </button>
                <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
                <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
                <p class="back-to-login">
                  <router-link to="/signin">Вернуться к входу</router-link>
                </p>
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
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import loginDayImage from '@/assets/images/login_day2.jpg';
import loginNightImage from '@/assets/images/login_night2.jpg';

const email = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const loading = ref(false);
const router = useRouter();

// Определение текущей темы
const isDarkTheme = computed(() => {
  return document.documentElement.classList.contains('dark-theme');
});

const sendResetLink = async () => {
  errorMessage.value = '';
  successMessage.value = '';
  loading.value = true;

  if (!email.value) {
    errorMessage.value = 'Пожалуйста, введите email';
    loading.value = false;
    return;
  }

  try {
    const response = await axios.post('http://localhost:8000/api/password/reset/', {
      email: email.value
    });

    if (response.status === 200) {
      successMessage.value = 'Если пользователь существует, ссылка будет отправлена';
      email.value = '';
    }
  } catch (error) {
    console.error('Ошибка при отправке запроса:', error);
    if (error.response?.data?.error) {
      errorMessage.value = error.response.data.error;
    } else {
      errorMessage.value = 'Произошла ошибка. Пожалуйста, попробуйте позже.';
    }
  } finally {
    loading.value = false;
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
.login-button {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  height: 56px;
  margin-top: 20px;
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
.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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
.back-to-login {
  text-align: center;
  margin-top: 20px;
  font: 300 14px Raleway, sans-serif;
  color: var(--text-color);
}
.back-to-login a {
  color: var(--accent-color);
  text-decoration: none;
}
.back-to-login a:hover {
  text-decoration: underline;
}
</style>