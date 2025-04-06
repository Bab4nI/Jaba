<template>
  <div style="display: inline-block; width: 1505px" data-ignore="used only for top most containter width">
    <div class="main-content-container">
      <div class="login-container1">
        <div class="welcome-message-container">
          <div class="welcome-login-container">
            <div class="login-container">
              <div class="password-prompt-container1">
                <p class="welcome-message">Сброс пароля</p>
                <p class="welcome-message1">Введите новый пароль и подтвердите его</p>
              </div>
              <div class="login-form-container">
                <div class="password-prompt-container1">
                  <div class="password-prompt-container">
                    <div class="password-input-container">
                      <input
                        v-model="form.newPassword"
                        :type="passwordFieldType"
                        class="transparent-input"
                        placeholder="Новый пароль"
                      />
                      <img
                        :src="eyeIcon"
                        class="password-input-icon"
                        @click="togglePasswordVisibility"
                        alt="Toggle password visibility"
                      />
                    </div>
                  </div>
                  <div class="password-prompt-container" style="margin-top: 27px">
                    <div class="password-input-container">
                      <input
                        v-model="form.confirmPassword"
                        :type="passwordFieldType"
                        class="transparent-input"
                        placeholder="Подтвердите пароль"
                      />
                      <img
                        :src="eyeIcon"
                        class="password-input-icon"
                        @click="togglePasswordVisibility"
                        alt="Toggle password visibility"
                      />
                    </div>
                  </div>
                  <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
                </div>
                <button 
                  class="login-button" 
                  @click="resetPassword"
                  :disabled="loading"
                >
                  {{ loading ? 'Сохранение...' : 'Сохранить пароль' }}
                </button>
                <p class="back-to-login">
                  <router-link to="/login">Вернуться к входу</router-link>
                </p>
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
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import eyeOpen from '@/assets/images/psswd_open.png';
import eyeClosed from '@/assets/images/psswd_close.png';

const route = useRoute();
const router = useRouter();
const errorMessage = ref('');
const loading = ref(false);

// Состояние видимости паролей (теперь одно для обоих полей)
const isPasswordVisible = ref(false);

// Форма с данными
const form = ref({
  newPassword: '',
  confirmPassword: '',
  token: route.query.token || '',
});

// Вычисляемое свойство для типа полей
const passwordFieldType = computed(() => 
  isPasswordVisible.value ? 'text' : 'password'
);

// Вычисляемое свойство для иконки
const eyeIcon = computed(() => 
  isPasswordVisible.value ? eyeOpen : eyeClosed
);

// Переключение видимости паролей
const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value;
};

// Валидация формы
const validateForm = () => {
  if (!form.value.newPassword) {
    errorMessage.value = 'Введите новый пароль';
    return false;
  }
  
  if (form.value.newPassword.length < 8) {
    errorMessage.value = 'Пароль должен содержать минимум 8 символов';
    return false;
  }
  
  if (form.value.newPassword !== form.value.confirmPassword) {
    errorMessage.value = 'Пароли не совпадают';
    return false;
  }
  
  if (!form.value.token) {
    errorMessage.value = 'Недействительная ссылка для сброса пароля';
    return false;
  }
  
  errorMessage.value = '';
  return true;
};

// Отправка формы
const resetPassword = async () => {
  if (!validateForm()) return;
  
  loading.value = true;
  
  try {
    const response = await axios.post('http://localhost:8000/api/password/reset/confirm/', {
      token: form.value.token,
      new_password: form.value.newPassword
    });

    if (response.status === 200) {
      alert('Пароль успешно изменен');
      router.push('/signin');
    }
  } catch (error) {
    console.error('Ошибка при сбросе пароля:', error);
    if (error.response?.data?.error) {
      errorMessage.value = error.response.data.error;
    } else {
      errorMessage.value = 'Произошла ошибка. Пожалуйста, проверьте данные и попробуйте снова.';
    }
  } finally {
    loading.value = false;
  }
};

// Проверка токена при загрузке компонента
onMounted(() => {
  if (!form.value.token) {
    errorMessage.value = 'Недействительная ссылка для сброса пароля';
  }
});
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
  .back-to-login {
    text-align: center;
    margin-top: 20px;
    font: 300 16px Raleway, sans-serif;
  }
  .back-to-login a {
    color: #a094b8;
    text-decoration: underline;
  }
  .back-to-login a:hover {
    color: #7c54ca;
  }
  .error-message {
    color: #ff5252;
    font: 300 16px Raleway, sans-serif;
    margin-top: 15px;
    text-align: center;
  }
  </style>