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
                    <img 
                      :src="eyeIcon" 
                      class="password-input-icon" 
                      @click="togglePasswordVisibility" 
                      alt="Toggle Password Visibility"
                    />
                  </div>
                  <div class="password-input-container">
                    <input 
                      :type="passwordFieldType" 
                      placeholder="Подтвердите пароль" 
                      class="input-style"
                      v-model="form.confirmPassword"
                    />
                    <img 
                      :src="eyeIcon" 
                      class="password-input-icon" 
                      @click="togglePasswordVisibility" 
                      alt="Toggle Password Visibility"
                    />
                  </div>
              </div>
              <div class="account-creation-button-container">
                <button type="submit" class="account-creation-button">Создать учётную запись</button>
              </div>
              </form>
            </div>
            <img src="@/assets/images/login_day1.jpg" class="account-creation-image" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

// Иконки для пароля
import eyeOpen from '@/assets/images/psswd_open.png';
import eyeClosed from '@/assets/images/psswd_close.png';

// Состояния
const route = useRoute();
const isPasswordVisible = ref(false);
const form = ref({
  lastName: route.query.last_name || '',
  firstName: route.query.first_name || '',
  email: route.query.email || '',
  group: route.query.group || '',
  password: '',
  confirmPassword: '',
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
      password: form.value.password,
    });

    // Перенаправление на страницу входа
    window.location.href = 'http://localhost:5173/SignIn';
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
  background: #f5f9f8;
}
.main-title-text-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 36px Helvetica;
  color: #24222f;
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
  border-left: 1px solid #24222f;
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

.login-heading-text-style:hover {
    text-decoration: underline;
    text-underline-offset: 5px;
}

.main-nav-icon {
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
  background: #ebefef;
  border-radius: 35px;
}
.account-creation-form {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  align-self: flex-start;
  justify-content: flex-start;
  min-width: 504px;
  padding-top: 153px;
}
.welcome-message-container {
  flex: 0 0 auto;
}
.welcome-message-style {
  padding: 0;
  margin: 0;
  font: 700 32px Raleway, sans-serif;
  color: #24222f;
}
.welcome-message-text-style {
  padding: 0;
  margin: 0;
  margin-top: 11px;
  font: 300 16px Raleway, sans-serif;
  color: black;
}
.input-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 30px;
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
.input-style {
  width: 100%;
  font: 100 20px Raleway, sans-serif;
  background: transparent;
  border: none;
  outline: none;
}
.password-input-section {
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  gap: 27px;
  align-items: stretch;
  justify-content: center;
  margin-top: 48px;
}
.password-input-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
  height: 44px;
  padding-right: 13px;
  padding-left: 21px;
  background: #f5f9f8;
  border-radius: 20px;
}
.password-prompt-text-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 100 20px Raleway, sans-serif;
  color: black;
}
.password-input-icon {
  box-sizing: border-box;
  display: block;
  width: 27px;
  max-width: initial;
  height: 27px;
  border: none;
  object-fit: cover;
}
.account-creation-button-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  height: 51px;
  padding-right: 75px;
  padding-left: 75px;
  margin-top: 78px;
  background: #a094b8;
  border-radius: 20px;
}
.account-creation-button {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #f5f9f8;
  background: none;
  border: none;
  cursor: pointer;
}

.account-creation-button-container:hover {
  background: #7c54ca;
  transition: 0.5s ease;
}
.account-creation-image {
  box-sizing: border-box;
  display: block;
  width: 536px;
  max-width: initial;
  height: 723px;
  border: none;
  border-radius: 35px;
  object-fit: cover;
}
.input-row {
  display: flex;
  flex-direction: row;
  gap: 20px;
  margin-bottom: 20px;
}

.password-input-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.input-style {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 5px;
}

.password-input-icon {
  cursor: pointer;
  width: 24px;
  height: 24px;
}
</style>

