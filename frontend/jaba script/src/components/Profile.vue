<template>
  <div class="profile-card-container2">
    <p class="profile-heading">Мой профиль</p>
    <div class="student-profile-container">
      <div class="profile-card">
        <div class="avatar-container">
          <img v-if="avatarBase64" :src="avatarBase64" alt="Аватар" class="profile-image" />
          <img v-else :src="avatarSrc" alt="Аватар" class="profile-image" />
          <input type="file" accept="image/*" @change="handleAvatarUpload" class="avatar-upload-input" />
        </div>
        <div class="student-info-card1">
          <p class="main-title-text-style">{{ fullName }}</p>
          <div class="student-info-container">
            <p class="student-role-text-style">{{ userRole === 'student' ? 'Студент' : 'Преподаватель' }}</p>
            <p class="student-info-text-style">{{ department }}</p>
          </div>
        </div>
      </div>
      <div class="profile-card1">
        <div class="student-profile-card">
          <div class="student-info-card">
            <div class="email-section">
              <div class="email-header">
                <p class="email-label-text-style">Адрес электронной почты</p>
                <div v-if="!isEditingEmail" class="edit-button-container" @click="toggleEditEmail">
                  <p class="edit-button-text-style">Редактировать</p>
                  <img src="@/assets/images/edit.png" class="edit-icon" />
                </div>
              </div>
              
              <div v-if="!isEditingEmail">
                <p class="email-link-text-style">{{ email }}</p>
              </div>
              
              <div v-else class="email-edit-wrapper">
                <input v-model="newEmail" type="email" class="email-input" placeholder="Введите новый email" />
                <p v-if="emailError" class="error-message">{{ emailError }}</p>
                
                <div v-if="!showVerificationCode" class="email-actions">
                  <button @click="saveEmail" class="save-button" :disabled="isSaving">
                    {{ isSaving ? 'Отправка...' : 'Продолжить' }}
                  </button>
                  <button @click="cancelEdit" class="cancel-button">Отмена</button>
                </div>

                <div v-if="showVerificationCode" class="verification-section">
                  <p class="verification-info">Код подтверждения отправлен на {{ newEmail }}</p>
                  <input 
                    v-model="verificationCode" 
                    type="text" 
                    placeholder="Введите 6-значный код" 
                    class="verification-input"
                    maxlength="6"
                  />
                  <p v-if="verificationError" class="error-message">{{ verificationError }}</p>
                  <div class="verification-actions">
                    <button @click="verifyCode" class="verify-button" :disabled="isVerifying">
                      {{ isVerifying ? 'Проверка...' : 'Подтвердить' }}
                    </button>
                    <button @click="resendCode" class="resend-button" :disabled="isResending">
                      {{ isResending ? 'Отправка...' : 'Отправить код повторно' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="vertical-section-divider">
              <div class="course-progress-container">
                <p class="email-label-text-style">Уровень обучения</p>
                <p class="education-details-text-style">{{ level }}</p>
              </div>
              <div class="group-info-block">
                <p class="email-label-text-style">Группа</p>
                <p class="education-details-text-style">{{ group }}</p>
              </div>
              <div class="group-info-block">
                <p class="email-label-text-style">Направление обучения</p>
                <p class="education-details-text-style">{{ course }}</p>
              </div>
              <div class="vertical-section-divider">
                <p class="email-label-text-style">Кафедра</p>
                <p class="education-details-text-style">{{ department }}</p>
              </div>
            </div>
          </div>
          <Calendar />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import Calendar from '@/components/Calendar.vue';
import axios from 'axios';
import { useRefreshStore } from '@/stores/auth';

const userStore = useUserStore();
const refreshStore = useRefreshStore();

// User data
const userRole = computed(() => userStore.role);
const fullName = computed(() => `${userStore.first_name} ${userStore.last_name} ${userStore.middle_name}`);
const email = computed(() => userStore.email);
const group = computed(() => userStore.group);
const avatarBase64 = computed(() => userStore.avatarBase64);
const department = computed(() => userStore.department || 'Не указано');
const level = computed(() => userStore.level || 'Не указано');
const course = computed(() => userStore.course || 'Не указано');

// Email change states
const newEmail = ref('');
const isEditingEmail = ref(false);
const emailError = ref('');
const isSaving = ref(false);
const showVerificationCode = ref(false);
const verificationCode = ref('');
const verificationError = ref('');
const isVerifying = ref(false);
const isResending = ref(false);

const avatarSrc = computed(() => {
  if (avatarBase64.value) return avatarBase64.value;
  return userRole.value === 'admin' 
    ? new URL('@/assets/images/admin-avatar.png', import.meta.url).href 
    : new URL('@/assets/images/default-avatar.png', import.meta.url).href;
});

const fetchUserProfile = () => userStore.fetchUserProfile();

const handleAvatarUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      userStore.updateAvatar(e.target.result);
    };
    reader.readAsDataURL(file);
  }
};

const toggleEditEmail = () => {
  isEditingEmail.value = !isEditingEmail.value;
  if (isEditingEmail.value) {
    newEmail.value = email.value;
    emailError.value = '';
    showVerificationCode.value = false;
    verificationCode.value = '';
    verificationError.value = '';
  }
};

const cancelEdit = () => {
  isEditingEmail.value = false;
  newEmail.value = email.value;
  emailError.value = '';
  showVerificationCode.value = false;
};

const saveEmail = async () => {
  if (!newEmail.value) {
    emailError.value = 'Email обязателен';
    return;
  }

  if (newEmail.value === email.value) {
    isEditingEmail.value = false;
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(newEmail.value)) {
    emailError.value = 'Введите корректный email';
    return;
  }

  isSaving.value = true;
  emailError.value = '';

  try {
    const token = userStore.accessToken;
    if (!token) {
      throw new Error('Отсутствует токен доступа');
    }

    const response = await axios.post(
      'http://localhost:8000/api/change-email/',
      { new_email: newEmail.value },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.data.status === 'Код подтверждения отправлен на новый email') {
      showVerificationCode.value = true;
    } else {
      throw new Error('Неизвестный ответ сервера');
    }
  } catch (error) {
    console.error('Ошибка при запросе смены email:', error);
    if (error.response) {
      if (error.response.status === 400) {
        emailError.value = error.response.data.error || 'Этот email уже используется';
      } else if (error.response.status === 401) {
        await refreshStore.refreshToken();
        if (refreshStore.accessToken) {
          userStore.setAccessToken(refreshStore.accessToken);
          await saveEmail();
          return;
        }
        emailError.value = 'Сессия истекла. Пожалуйста, войдите снова.';
      } else {
        emailError.value = 'Ошибка сервера при смене email';
      }
    } else {
      emailError.value = 'Ошибка сети при смене email';
    }
  } finally {
    isSaving.value = false;
  }
};

const verifyCode = async () => {
  if (!verificationCode.value || verificationCode.value.length !== 6) {
    verificationError.value = 'Введите 6-значный код подтверждения';
    return;
  }

  isVerifying.value = true;
  verificationError.value = '';

  try {
    const token = userStore.accessToken;
    if (!token) {
      throw new Error('Отсутствует токен доступа');
    }

    const response = await axios.post(
      'http://localhost:8000/api/verify-email-code/',
      { code: verificationCode.value },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.data.status === 'Email успешно изменен') {
      userStore.email = newEmail.value;
      isEditingEmail.value = false;
      showVerificationCode.value = false;
    } else {
      throw new Error('Неизвестный ответ сервера');
    }
  } catch (error) {
    console.error('Ошибка при проверке кода:', error);
    if (error.response) {
      if (error.response.status === 400) {
        verificationError.value = error.response.data.error || 'Неверный код подтверждения';
      } else if (error.response.status === 401) {
        verificationError.value = 'Сессия истекла. Пожалуйста, войдите снова.';
      } else {
        verificationError.value = 'Ошибка сервера при проверке кода';
      }
    } else {
      verificationError.value = 'Ошибка сети при проверке кода';
    }
  } finally {
    isVerifying.value = false;
  }
};

const resendCode = async () => {
  isResending.value = true;
  verificationError.value = '';

  try {
    const token = userStore.accessToken;
    if (!token) {
      throw new Error('Отсутствует токен доступа');
    }

    const response = await axios.post(
      'http://localhost:8000/api/change-email/',
      { new_email: newEmail.value },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.data.status === 'Код подтверждения отправлен на новый email') {
      verificationError.value = 'Новый код отправлен!';
    } else {
      throw new Error('Неизвестный ответ сервера');
    }
  } catch (error) {
    console.error('Ошибка при повторной отправке кода:', error);
    if (error.response) {
      if (error.response.status === 400) {
        verificationError.value = error.response.data.error || 'Ошибка при отправке кода';
      } else if (error.response.status === 401) {
        verificationError.value = 'Сессия истекла. Пожалуйста, войдите снова.';
      } else {
        verificationError.value = 'Ошибка сервера';
      }
    } else {
      verificationError.value = 'Ошибка сети';
    }
  } finally {
    isResending.value = false;
  }
};

onMounted(() => {
  fetchUserProfile();
});
</script>

<style scoped>
.profile-card-container2 {
  flex: 0 0 885px;
}

.profile-heading {
  font: 600 24px Raleway, sans-serif;
  color: #24222f;
  margin-bottom: 20px;
}

.student-profile-container {
  margin-top: 35px;
}

.profile-card {
  display: flex;
  align-items: center;
  padding: 18px 25px;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
  margin-bottom: 25px;
}

.avatar-container {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #ebefef;
  flex-shrink: 0;
}

.profile-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-upload-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.student-info-card1 {
  margin-left: 29px;
  flex-grow: 1;
}

.main-title-text-style {
  font: 400 32px Raleway, sans-serif;
  color: #24222f;
  margin: 0;
}

.student-info-container {
  margin-top: 15px;
}

.student-role-text-style {
  font: 400 20px Raleway, sans-serif;
  color: #3b3a4a;
  margin: 0;
}

.student-info-text-style {
  font: 400 16px Raleway, sans-serif;
  color: #575667;
  margin-top: 15px;
}

.profile-card1 {
  margin-top: 25px;
}

.student-profile-card {
  display: flex;
  padding: 25px;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
  gap: 40px;
}

.student-info-card {
  flex: 1;
}

.email-section {
  margin-bottom: 30px;
}

.email-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.email-label-text-style {
  font: 400 14px Raleway, sans-serif;
  color: #575667;
  margin: 0;
}

.email-link-text-style {
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
  margin: 0;
}

.edit-button-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  padding: 0 12px;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-button-container:hover {
  background: #ebefef;
}

.edit-button-text-style {
  font: 400 14px Raleway, sans-serif;
  color: #575667;
  margin: 0;
}

.edit-icon {
  width: 15px;
  height: 15px;
  margin-left: 6px;
}

.email-edit-wrapper {
  margin-top: 15px;
}

.email-input {
  width: 100%;
  max-width: 400px;
  padding: 10px 15px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font: 400 16px Raleway, sans-serif;
  transition: border-color 0.2s;
}

.email-input:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.error-message {
  color: #e74c3c;
  font: 400 14px Raleway, sans-serif;
  margin-top: 8px;
}

.email-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.vertical-section-divider {
  margin-top: 25px;
}

.course-progress-container,
.group-info-block {
  margin-bottom: 20px;
}

.education-details-text-style {
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
  margin-top: 8px;
}

/* Verification section */
.verification-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.verification-info {
  font: 400 14px Raleway, sans-serif;
  color: #575667;
  margin-bottom: 15px;
}

.verification-input {
  width: 100%;
  max-width: 200px;
  padding: 10px 15px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font: 400 16px Raleway, sans-serif;
  letter-spacing: 1px;
}

.verification-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

/* Buttons */
.save-button,
.cancel-button,
.verify-button,
.resend-button {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font: 500 14px Raleway, sans-serif;
  cursor: pointer;
  transition: all 0.2s;
}

.save-button,
.verify-button {
  background-color: #4caf50;
  color: white;
}

.save-button:hover,
.verify-button:hover {
  background-color: #3e8e41;
}

.save-button:disabled,
.verify-button:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.cancel-button {
  background-color: #f44336;
  color: white;
}

.cancel-button:hover {
  background-color: #d32f2f;
}

.resend-button {
  background-color: #2196f3;
  color: white;
}

.resend-button:hover {
  background-color: #0b7dda;
}

.resend-button:disabled {
  background-color: #90caf9;
  cursor: not-allowed;
}

/* Calendar section */
.calendar-container {
  flex: 0 0 300px;
}
</style>