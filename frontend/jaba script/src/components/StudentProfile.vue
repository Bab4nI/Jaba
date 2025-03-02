<template>
  <div class="profile-card-container2">
    <p class="profile-heading">Мой профиль</p>
    <div class="student-profile-container">
      <div class="profile-card">
        <img src="@/assets/images/image_756d8ce5.jpeg" class="profile-image-container" />
        <div class="student-info-card1">
          <p class="main-title-text-style">{{ fullName }}</p>
          <div class="student-info-container">
            <p class="student-role-text-style">Студент</p>
            <p class="student-info-text-style">{{ department }}</p>
          </div>
        </div>
      </div>
      <div class="profile-card1">
        <div class="student-profile-card">
          <div class="student-info-card">
            <p class="email-label-text-style">Адрес электронной почты</p>
            <div v-if="!isEditingEmail">
              <a :href="'mailto:' + email" class="email-link-text-style">{{ email }}</a>
            </div>
            <div v-else>
              <input v-model="newEmail" type="email" class="email-input" />
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
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Calendar from '@/components/Calendar.vue';

// Данные пользователя
const fullName = ref('Фамилия Имя Отчество');
const email = ref('smth@sfedu.ru');
const newEmail = ref('');
const level = ref('Специалист');
const group = ref('КТсо2-4');
const course = ref('10.05.03');
const department = ref('БИТ им. О. Б. Макаревича');
const isEditingEmail = ref(false);

// Функция для загрузки данных пользователя с API
const fetchUserProfile = async () => {
  try {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      console.error('Отсутствует токен доступа');
      return;
    }

    // Получаем данные профиля
    const response = await axios.get('http://localhost:8000/api/profile/', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    // Обновляем данные профиля
    const userData = response.data;
    fullName.value = `${userData.last_name} ${userData.first_name}`;
    email.value = userData.email;
    newEmail.value = userData.email; // Инициализируем новое значение email
    level.value = userData.level;
    group.value = userData.group;
    course.value = userData.course;
    department.value = userData.department;
  } catch (error) {
    console.error('Ошибка при загрузке данных профиля:', error);
  }
};

// Включение/выключение режима редактирования email
const toggleEditEmail = () => {
  isEditingEmail.value = !isEditingEmail.value;
  if (isEditingEmail.value) {
    newEmail.value = email.value; // Устанавливаем текущий email в поле ввода
  }
};

// Сохранение нового email
const saveEmail = async () => {
  try {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      console.error('Отсутствует токен доступа');
      return;
    }

    // Отправляем запрос на обновление email
    const response = await axios.patch(
      'http://localhost:8000/api/profile/',
      { email: newEmail.value },
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );

    // Обновляем email на клиенте
    email.value = newEmail.value;
    isEditingEmail.value = false; // Выходим из режима редактирования
  } catch (error) {
    console.error('Ошибка при обновлении email:', error);
  }
};

// Отмена редактирования
const cancelEdit = () => {
  isEditingEmail.value = false;
};

// Загружаем данные при монтировании компонента
onMounted(() => {
  fetchUserProfile();
});
</script>

<style scoped>
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