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
            <p class="email-label-text-style">Адрес электронной почты</p>
            <div v-if="!isEditingEmail">
              <p class="email-link-text-style">{{ email }}</p>
            </div>
            <div v-else>
              <input v-model="newEmail" type="email" class="email-input" />
              <p v-if="emailError" class="error-message">{{ emailError }}</p>
              <button @click="saveEmail" class="save-button">Сохранить</button>
              <button @click="cancelEdit" class="cancel-button">Отмена</button>
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
          <div class="edit-section-container">
            <div class="edit-button-container" @click="toggleEditEmail">
              <p class="edit-button-text-style">Редактировать</p>
              <img src="@/assets/images/edit.png" class="edit-icon" />
            </div>
          </div>
          <Calendar />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
//components/profile.vue
import { computed, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import Calendar from '@/components/Calendar.vue';

const userStore = useUserStore();
const userRole = computed(() => userStore.role);
const fullName = computed(() => `${userStore.first_name} ${userStore.last_name} ${userStore.middle_name}`);
const email = computed(() => userStore.email);
const group = computed(() => userStore.group);
const avatarBase64 = computed(() => userStore.avatarBase64);

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

const avatarSrc = computed(() => {
  if (avatarBase64) return avatarBase64;
  return userRole === 'admin' 
    ? new URL('@/assets/images/admin-avatar.png', import.meta.url).href 
    : new URL('@/assets/images/default-avatar.png', import.meta.url).href;
});

const toggleEditEmail = () => userStore.toggleEditEmail();
const saveEmail = () => userStore.saveEmail();
const cancelEdit = () => userStore.cancelEdit();

onMounted(() => {
  console.log('Компонент смонтирован');
  fetchUserProfile();
});
</script>

<style scoped>
.avatar-container {
  position: relative;
  width: 150px; /* Фиксированная ширина */
  height: 150px; /* Фиксированная высота */
  border-radius: 50%; /* Делаем контейнер круглым */
  overflow: hidden; /* Обрезаем лишнее */
  border: 2px solid #ebefef; /* Добавляем рамку */
}

.profile-image {
  width: 100%; /* Заполняем контейнер по ширине */
  height: 100%; /* Заполняем контейнер по высоте */
  object-fit: cover; /* Масштабируем изображение с сохранением пропорций */
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
.error-message {
  color: red;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.profile-card-container2 {
  flex: 0 0 885px; /* Ширина контейнера профиля */
}

.profile-heading {
  font: 600 24px Raleway, sans-serif;
  color: #24222f;
}

.student-profile-container {
  margin-top: 35px;
}

.profile-card {
  display: flex;
  align-items: center;
  padding: 18px 25px 14px;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
}

.profile-image-container {
  width: 150px;
  height: 150px;
  border-radius: 100px;
  object-fit: cover;
}

.student-info-card1 {
  margin-left: 29px;
}

.main-title-text-style {
  font: 400 32px Raleway, sans-serif;
  color: #24222f;
}

.student-info-container {
  margin-top: 15px;
}

.student-role-text-style {
  font: 400 20px Raleway, sans-serif;
  color: #3b3a4a;
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
  justify-content: space-between;
  padding: 14px 19px 25px 24px;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
}

.email-label-text-style {
  font: 400 14px Raleway, sans-serif;
  color: #575667;
}

.email-link-text-style {
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
  text-decoration: none;
}

.vertical-section-divider {
  margin-top: 23px;
}

.education-details-text-style {
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
  margin-top: 8px;
}

.group-info-block {
  margin-top: 23px;
}

.edit-section-container {
  align-self: center;
  padding-bottom: 281px;
}

.edit-button-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  padding: 0 10px;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
}

.edit-button-text-style {
  font: 400 14px Raleway, sans-serif;
  color: #575667;
}
.edit-button-text-style {
  cursor: pointer;
}
.edit-icon {
  width: 15px;
  height: 15px;
  margin-left: 6px;
}

.email-input {
  padding: 5px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-right: 10px;
}

.save-button,
.cancel-button {
  padding: 5px 10px;
  font-size: 14px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-button {
  background-color: #4caf50;
  color: white;
}

.cancel-button {
  background-color: #f44336;
  color: white;
  margin-left: 5px;
}

.save-button:hover,
.cancel-button:hover {
  opacity: 0.8;
}
</style>