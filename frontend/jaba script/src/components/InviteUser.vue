<template>
    <div class="new-user-invitation-form-container">
      <p class="invitation-heading">Приглашение нового пользователя</p>
      <div class="user-invite-form">
        <div class="form-grid">
          <!-- Фамилия -->
          <div class="form-field">
            <p class="form-field-label">Фамилия:</p>
            <input
              v-model="formData.last_name"
              type="text"
              class="form-input"
              placeholder="Введите фамилию"
            />
          </div>
  
          <!-- Имя -->
          <div class="form-field">
            <p class="form-field-label">Имя:</p>
            <input
              v-model="formData.first_name"
              type="text"
              class="form-input"
              placeholder="Введите имя"
            />
          </div>
  
          <!-- Отчество -->
          <div class="form-field">
            <p class="form-field-label">Отчество (при наличии):</p>
            <input
              v-model="formData.middle_name"
              type="text"
              class="form-input"
              placeholder="Введите отчество"
            />
          </div>
  
          <!-- Группа -->
          <div class="form-field">
            <p class="form-field-label">Группа:</p>
            <input
              v-model="formData.group"
              type="text"
              class="form-input"
              placeholder="Введите группу"
            />
          </div>
  
          <!-- Почта -->
          <div class="form-field">
            <p class="form-field-label">Почта:</p>
            <input
              v-model="formData.email"
              type="email"
              class="form-input"
              placeholder="Введите почту"
            />
          </div>
  
          <!-- Роль -->
          <div class="form-field">
            <p class="form-field-label">Роль:</p>
            <select v-model="formData.role" class="form-input">
              <option value="student">Студент</option>
              <option value="admin">Администратор</option>
            </select>
          </div>
        </div>
  
        <!-- Кнопка отправки -->
        <button class="send-invite-button" @click="submitForm">
          Отправить приглашение
        </button>
  
        <!-- Сообщение об ошибке или успехе -->
        <p v-if="message" :class="messageClass">{{ message }}</p>
      </div>
    </div>
  </template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

// Состояние формы
const formData = ref({
  last_name: '', // Фамилия
  first_name: '', // Имя
  middle_name: '', // Отчество
  group: '', // Группа
  email: '', // Почта
  role: 'student', // Роль
});

// Сообщение об ошибке или успехе
const message = ref('');
const messageClass = ref('');

// Метод для отправки данных
const submitForm = async () => {
  console.log('formData:', formData.value); // Отладка

  try {
    // Проверка обязательных полей
    if (
      !formData.value.last_name.trim() ||
      !formData.value.first_name.trim() ||
      !formData.value.email.trim() ||
      !formData.value.role.trim()
    ) {
      message.value = 'Пожалуйста, заполните все обязательные поля.';
      messageClass.value = 'error-message';
      return;
    }

    // Отправка данных на сервер
    const response = await axios.post(
      'http://localhost:8000/api/send-registration-link/',
      formData.value,
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      }
    );

    // Обработка успешного ответа
    message.value = 'Приглашение успешно отправлено!';
    messageClass.value = 'success-message';

    // Очистка формы
    formData.value = {
      last_name: '',
      first_name: '',
      middle_name: '',
      group: '',
      email: '',
      role: 'student',
    };
  } catch (error) {
    // Обработка ошибки
    if (error.response) {
      message.value = `Ошибка: ${error.response.data.details || error.response.data.message || 'Неизвестная ошибка'}`;
    } else {
      message.value = `Ошибка: ${error.message}`;
    }
    messageClass.value = 'error-message';
  }
};
</script>

<style scoped>
.new-user-invitation-form-container {
  box-sizing: border-box;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #f5f9f8;
  border-radius: 20px;
}

.invitation-heading {
  font: 600 24px Raleway, sans-serif;
  color: #24222f;
  text-align: center;
  margin-bottom: 30px;
}

.user-invite-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-field-label {
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
}

.form-input {
  padding: 10px;
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
  background: #ebefef;
  border: 1px solid #c5c8cc;
  border-radius: 10px;
  outline: none;
}

.form-input:focus {
  border-color: #a094b8;
}

.send-invite-button {
  padding: 10px 20px;
  font: 400 16px Raleway, sans-serif;
  color: #f5f9f8;
  background: #a094b8;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  align-self: center;
  margin-top: 20px;
}

.send-invite-button:hover {
  background: #8a7fa3;
}

.success-message {
  color: green;
  text-align: center;
}

.error-message {
  color: red;
  text-align: center;
}

.new-user-invitation-form-container {
  box-sizing: border-box;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #f5f9f8;
  border-radius: 20px;
}

.invitation-heading {
  font: 600 24px Raleway, sans-serif;
  color: #24222f;
  text-align: center;
  margin-bottom: 30px;
}

.user-invite-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-field-label {
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
}

.form-input {
  padding: 10px;
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
  background: #ebefef;
  border: 1px solid #c5c8cc;
  border-radius: 10px;
  outline: none;
}

.form-input:focus {
  border-color: #a094b8;
}

.send-invite-button {
  padding: 10px 20px;
  font: 400 16px Raleway, sans-serif;
  color: #f5f9f8;
  background: #a094b8;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  align-self: center;
  margin-top: 20px;
}

.send-invite-button:hover {
  background: #8a7fa3;
}
.main-content-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  min-width: 1480px;
  background: #ebefef;
}
.flex-column-centered {
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
.navigation-bar {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  gap: 29.5px;
  align-items: center;
  justify-content: flex-start;
  min-width: 485px;
}
.main-section-title {
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
.personal-info-container {
  display: flex;
  flex: 1 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  padding-top: 9px;
  padding-bottom: 5px;
}
.personal-cabinet-heading {
  flex: 0 0 auto;
  align-self: center;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
}
.personal-info-divider {
  flex: 0 0 auto;
  margin-top: 2px;
  border-top: 1px solid #24222f;
}
.profile-image-placeholder {
  box-sizing: border-box;
  display: block;
  width: 42px;
  max-width: initial;
  height: 40px;
  border: none;
  object-fit: cover;
}
.user-profile-widget-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
.user-invite-form-container {
  box-sizing: border-box;
  min-width: 1280px;
  padding-top: 84px;
  padding-bottom: 96px;
}
.user-profile-invitation-section {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 48px;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  padding: 57px 32px 225px;
  background: #f5f9f8;
  border-radius: 30px;
}
.user-profile-sidebar-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 1 214px;
  flex-direction: column;
  align-items: stretch;
  align-self: flex-start;
  justify-content: flex-start;
  max-width: 214px;
  padding-top: 37px;
}
.user-profile-title-container {
  flex: 0 0 auto;
  padding-right: 17px;
  padding-left: 17px;
}
.user-profile-title-widget-style {
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #575667;
  white-space: pre-wrap;
}
.user-profile-title-margin-top {
  margin-top: 35px;
}
.user-profile-title-widget-style:first-child {
  margin-top: 0px;
}
.course-statistics-heading {
  box-sizing: border-box;
  width: 100%;
  text-align: left;
}
.user-invite-container {
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  margin-top: 31px;
}
.user-invite-card {
  box-sizing: border-box;
  flex: 0 0 auto;
  height: 54px;
  background: #a094b8;
  border-radius: 15px;
}
.user-invite-card1 {
  flex: 0 0 auto;
  padding-right: 17px;
  padding-left: 17px;
  margin-top: -50px;
}
.user-invitation-text-style {
  box-sizing: border-box;
  max-width: 197px;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #f5f9f8;
  text-align: left;
}
.account-logout-button-text-style {
  flex: 0 0 auto;
  padding: 0;
  padding-right: 19px;
  padding-left: 19px;
  margin: 0;
  margin-top: 66px;
  font: 400 20px Raleway, sans-serif;
  color: #da1f38;
}
.sidebar-divider {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 3px;
  height: 716px;
  border-left: 3px solid #ebefef;
}
.new-user-invitation-form-container {
  box-sizing: border-box;
  flex: 0 0 829px;
  padding-top: 12.5px;
}
.invitation-heading {
  padding: 0;
  margin: 0;
  font: 600 24px Raleway, sans-serif;
  color: #24222f;
}
.user-invite-form {
  box-sizing: border-box;
  width: 100%;
  padding-right: 16px;
  padding-left: 16px;
  margin-top: 95px;
}
.user-form-layout {
  box-sizing: border-box;
  width: 100%;
}
.personal-info-form-layout {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 8px;
  align-items: flex-start;
  justify-content: space-between;
  width: 100%;
}
.vertical-flex-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  width: 322px;
}
.form-field-label {
  flex: 0 0 auto;
  padding: 0;
  padding-right: 15px;
  padding-left: 15px;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
}
.profile-info-box {
  box-sizing: border-box;
  flex: 0 0 auto;
  height: 53px;
  margin-top: 5px;
  background: #ebefef;
  border: 1px solid #c5c8cc;
  border-radius: 20px;
}
.flex-row-with-spacing {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-top: 26px;
}
.role-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  min-width: 322px;
}
.option-list-container {
  flex: 0 0 auto;
  margin-top: 5px;
}
.fullwidth-container {
  box-sizing: border-box;
  width: 100%;
}
.option-container {
  display: flex;
  flex: 0 0 auto;
  width: 20px;
  height: 20px;
}
.select-options-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  min-width: 322px;
  height: 53px;
  padding-right: 18px;
  padding-left: 18px;
  background: #ebefef;
  border: 1px solid #c5c8cc;
  border-radius: 20px;
}
.vertical-section-heading {
  box-sizing: border-box;
  width: 100%;
  margin-top: 27px;
}
.info-text {
  padding: 0;
  padding-right: 15px;
  padding-left: 15px;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
}
.student-info-card {
  box-sizing: border-box;
  width: 322px;
  height: 53px;
  margin-top: 5px;
  background: #ebefef;
  border: 1px solid #c5c8cc;
  border-radius: 20px;
}
.send-invite-button {
  box-sizing: border-box;
  display: block;
  width: 378px;
  min-width: 378px;
  height: 51px;
  margin-top: 109px;
  font: 400 20px Raleway, sans-serif;
  color: #f5f9f8;
  cursor: pointer;
  background: #a094b8;
  border: none;
  border-radius: 20px;
}
</style>
