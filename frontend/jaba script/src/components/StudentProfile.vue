<template>
  <div class="student-profile-wrapper">
    <p class="profile-heading">Мой профиль</p>
    <div class="student-profile-container">
      <div class="profile-card">
        <img src="@/assets/images/image_756d8ce5.jpeg" class="profile-image-container" />
        <div class="student-info-card1">
          <p class="main-title-text-style">Фамилия Имя Отчество</p>
          <div class="student-info-container">
            <p class="student-role-text-style">Студент</p>
            <p class="student-info-text-style">ИТА ЮФУ, ИКТИБ</p>
          </div>
        </div>
      </div>
      <div class="profile-card1">
        <div class="student-profile-card">
          <div class="student-info-card">
            <p class="email-label-text-style">Адрес электронной почты</p>
            <a href="mailto:smth@sfedu.ru" class="email-link-text-style">smth@sfedu.ru</a>
            <div class="vertical-section-divider">
              <div class="course-progress-container">
                <p class="email-label-text-style">Уровень обучения</p>
                <p class="education-details-text-style">Специалист</p>
              </div>
              <div class="group-info-block">
                <p class="email-label-text-style">Группа</p>
                <p class="education-details-text-style">КТсо2-4</p>
              </div>
              <div class="group-info-block">
                <p class="email-label-text-style">Направление обучения</p>
                <p class="education-details-text-style">10.05.03</p>
              </div>
              <div class="vertical-section-divider">
                <p class="email-label-text-style">Кафедра</p>
                <p class="education-details-text-style">БИТ им. О. Б. Макаревича</p>
              </div>
            </div>
          </div>
          <div class="edit-section-container">
            <div class="edit-button-container">
              <p class="edit-button-text-style">Редактировать</p>
              <img src="@/assets/images/edit.png" class="edit-icon" />
            </div>
          </div>
        </div>
        <Calendar />
      </div>
    </div>
  </div>
</template>

<script setup>
import Calendar from './Calendar.vue'; // Импортируем компонент календаря
</script>

<style scoped>
.student-profile-wrapper {
  flex: 1;
  padding: 20px;
}

.profile-heading {
  font: 600 24px Raleway, sans-serif;
  color: #24222f;
}

.student-profile-container {
  margin-top: 20px;
}

.profile-card {
  display: flex;
  align-items: center;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
  padding: 18px 25px;
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

.student-role-text-style {
  font: 400 20px Raleway, sans-serif;
  color: #3b3a4a;
}

.student-info-text-style {
  font: 400 16px Raleway, sans-serif;
  color: #575667;
}

.profile-card1 {
  margin-top: 25px;
}

.student-profile-card {
  display: flex;
  justify-content: space-between;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
  padding: 14px 19px 25px 24px;
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

.education-details-text-style {
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
}

.edit-button-text-style {
  font: 400 14px Raleway, sans-serif;
  color: #575667;
}

.edit-icon {
  width: 15px;
  height: 15px;
  margin-left: 6px;
}
</style>