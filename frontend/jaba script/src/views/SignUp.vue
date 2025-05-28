<template>
  <div style="display: inline-block; width: 1505px" data-ignore="used only for top most containter width">
    <div class="main-content-container">
      <div class="account-creation-form-container">
        <div class="registration-form-container">
          <div class="account-creation-section">
            <div class="account-creation-form">
              <div class="welcome-message-container">
                <p class="welcome-message-style">Welcome!</p>
                <p class="welcome-message-text-style">Создайте аккаунт, чтобы продолжить</p>
              </div>
              <form @submit.prevent="handleSubmit">
              <div class="input-section">
                <div class="input-row">
                  <div class="input-container">
                    <input 
                      type="text" 
                      placeholder="Фамилия" 
                      class="input-style" 
                      v-model="form.lastName"
                      readonly
                    />
                  </div>
                  <div class="input-container">
                    <input 
                      type="text" 
                      placeholder="Имя" 
                      class="input-style"
                      v-model="form.firstName"
                      readonly
                    />
                  </div>
                </div>
                <div class="input-row">
                  <div class="input-container">
                    <input 
                      type="email" 
                      placeholder="E-mail" 
                      class="input-style"
                      v-model="form.email"
                      readonly
                    />
                  </div>
                  <div class="input-container">
                    <input 
                      type="text" 
                      placeholder="Группа" 
                      class="input-style"
                      v-model="form.group"
                      readonly
                    />
                  </div>
                </div>
              </div>
              <div class="password-input-section">
                  <div class="password-input-container">
                    <input 
                      :type="passwordFieldType" 
                      placeholder="Придумайте пароль" 
                      class="input-style"
                      v-model="form.password"
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
                  <div class="password-input-container">
                    <input 
                      :type="passwordFieldType" 
                      placeholder="Подтвердите пароль" 
                      class="input-style"
                      v-model="form.confirmPassword"
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
              </div>
              <div class="account-creation-button-container">
                <button type="submit" class="account-creation-button">Создать учётную запись</button>
              </div>
              </form>
            </div>
            <img :src="isDarkTheme ? loginNightImage : loginDayImage" class="account-creation-image" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { jwtDecode }  from 'jwt-decode';
import axios from 'axios';
import loginDayImage from '@/assets/images/login_day1.jpg';
import loginNightImage from '@/assets/images/login_night1.jpg';

const route = useRoute();
const isPasswordVisible = ref(false);
const form = ref({
  lastName: '',
  firstName: '',
  email: '',
  group: '',
  password: '',
  confirmPassword: '',
  role: '',
});

// Определение текущей темы
const isDarkTheme = computed(() => {
  return document.documentElement.classList.contains('dark-theme');
});

// ✅ Расшифровка токена при монтировании компонента
onMounted(() => {
  const token = route.query.token;
  if (token) {
    try {
      const decoded = jwtDecode(token);
      form.value.lastName = decoded.last_name;
      form.value.firstName = decoded.first_name;
      form.value.email = decoded.email;
      form.value.group = decoded.group;
      form.value.role = decoded.role;
    } catch (error) {
      console.error('Ошибка при декодировании токена:', error);
      alert('Ошибка при обработке данных регистрации');
    }
  }
});

// Логика пароля
const passwordFieldType = computed(() => 
  isPasswordVisible.value ? 'text' : 'password'
);

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value;
};

// Обработка отправки формы
const handleSubmit = async () => {
  if (form.value.password !== form.value.confirmPassword) {
    alert('Пароли не совпадают');
    return;
  }

  try {
    const response = await axios.post('http://localhost:8000/api/register/', {
      last_name: form.value.lastName,
      first_name: form.value.firstName,
      email: form.value.email,
      group: form.value.group,
      role: form.value.role,
      password: form.value.password,
    });

    window.location.href = 'http://localhost:5173/';
  } catch (error) {
    console.error('Ошибка при регистрации:', error);
    alert('Ошибка при регистрации');
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
.center-column-flex-box {
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
.header-nav-container1 {
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
}
.header-nav-container {
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  gap: 29.5px;
  align-items: center;
  justify-content: flex-start;
}

.vertical-divider {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 1px;
  height: 29px;
  border-left: 1px solid var(--text-color);
}

.vertical-menu-nav-item {
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
.login-heading-text-style:hover {
  text-decoration: underline;
  text-underline-offset: 5px;
}
.menu-icon {
  box-sizing: border-box;
  display: block;
  width: 42px;
  max-width: initial;
  height: 40px;
  margin-left: 56px;
  border: none;
  object-fit: cover;
}
.account-creation-form-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
.registration-form-container {
  box-sizing: border-box;
  min-width: 1280px;
  padding-top: 29px;
  padding-bottom: 70px;
}
.account-creation-section {
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
.account-creation-form {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  min-width: 504px;
}
.welcome-message-container {
  flex: 0 0 auto;
}
.welcome-message-style {
  padding: 0;
  margin: 0;
  font: 700 32px Raleway, sans-serif;
  color: var(--text-color);
}
.welcome-message-text-style {
  padding: 0;
  margin: 0;
  margin-top: 11px;
  font: 300 16px Raleway, sans-serif;
  color: var(--secondary-text);
}
.input-section {
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  margin-top: 29px;
}
.input-row {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  gap: 20px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.input-container {
  box-sizing: border-box;
  display: flex;
  flex: 1 1 0%;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  padding: 15px 19px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}
.input-style {
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
.input-style::placeholder {
  color: var(--secondary-text);
  opacity: 0.7;
}
.password-input-section {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  gap: 20px;
  margin-top: 10px;
}
.password-input-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 15px 19px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 10px;
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
.account-creation-button-container {
  display: flex;
  flex-direction: row;
  justify-content: center;
  margin-top: 30px;
}
.account-creation-button {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 15px 30px;
  font: 500 16px Raleway, sans-serif;
  color: var(--footer-text);
  background: var(--accent-color);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.account-creation-button:hover {
  background: var(--hover-accent);
}
.account-creation-image {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 600px;
  max-width: initial;
  height: 488px;
  border: none;
  border-radius: 35px;
  object-fit: cover;
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

