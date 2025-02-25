<template>
  <div style="display: inline-block; width: 1505px" data-ignore="used only for top most containter width">
    <div class="main-content-container1">
      <div class="profile-card-container">
        <div class="main-content-container">
          <div class="profile-card-container1">
            <Sidebar />
            <div class="vertical-divider1"></div>
            <div class="profile-card-container2">
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import Calendar from '@/components/Calendar.vue';
import StudentProfile from '@/components/StudentProfile.vue';
const activeTab = ref('Мой профиль');

const setActiveTab = (tab) => {
  activeTab.value = tab;
};
</script>

<style scoped>


.main-content-container1 {
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
.main-title-text-style1 {
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
.main-title-text-style2 {
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
.profile-image-styles {
  box-sizing: border-box;
  display: block;
  width: 42px;
  max-width: initial;
  height: 40px;
  border: none;
  object-fit: cover;
}
.profile-card-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
.main-content-container {
  box-sizing: border-box;
  min-width: 1280px;
  padding-top: 84px;
  padding-bottom: 96px;
}
.profile-card-container1 {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 48px;
  align-items: flex-start;
  justify-content: flex-start;
  width: 100%;
  padding: 57px 32px 225px;
  background: #f5f9f8;
  border-radius: 30px;
}
.sidebar-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 214px;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  padding-top: 24.5px;
}
.course-progress-stats-container {
  flex: 0 0 auto;
}
.course-progress-container {
  box-sizing: border-box;
  width: 100%;
}
.elegant-input-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: start;
  width: 100%;
  height: 47px;
  padding-left: 17px;
  font: 400 20px Raleway, sans-serif;
  color: #f5f9f8;
  background: #a094b8;
  border: none;
  border-radius: 15px;
}
.transparent-input {
  box-sizing: border-box;
  width: 100%;
  font: 400 20px Raleway, sans-serif;
  background: transparent;
  border: none;
  outline: none;
}
.input-style-d23edb9f::placeholder {
  color: #f5f9f8;
}
.course-progress-tracker {
  padding-right: 19px;
  padding-left: 19px;
  margin-top: 23px;
}
.progress-tracker-text-style {
  box-sizing: border-box;
  max-width: 195px;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #575667;
  text-align: left;
}
.course-progress-statistics {
  padding: 0;
  padding-right: 17px;
  padding-left: 17px;
  margin: 0;
  margin-top: 36px;
  font: 400 20px Raleway, sans-serif;
  color: #575667;
}
.progress-indicator-text-style {
  flex: 0 0 auto;
  align-self: center;
  padding: 0;
  margin: 0;
  margin-top: 151px;
  font: 400 20px Raleway, sans-serif;
  color: #da1f38;
}
.vertical-divider1 {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 3px;
  height: 716px;
  border-left: 3px solid #ebefef;
}
.profile-card-container2 {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 885px;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
}
.profile-heading {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 600 24px Raleway, sans-serif;
  color: #24222f;
}
.student-profile-container {
  flex: 0 0 auto;
  margin-top: 35px;
}
.profile-card {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  padding: 18px 25px 14px;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
}
.profile-image-container {
  box-sizing: border-box;
  display: block;
  width: 150px;
  max-width: initial;
  height: 150px;
  border: none;
  border-radius: 100px;
  object-fit: cover;
}
.student-info-card1 {
  flex: 0 0 auto;
  padding-top: 20px;
  margin-left: 29px;
}
.main-title-text-style {
  padding: 0;
  margin: 0;
  font: 400 32px Raleway, sans-serif;
  color: #24222f;
}
.student-info-container {
  box-sizing: border-box;
  width: 100%;
  margin-top: 15px;
}
.student-role-text-style {
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #3b3a4a;
}
.student-info-text-style {
  padding: 0;
  margin: 0;
  margin-top: 15px;
  font: 400 16px Raleway, sans-serif;
  color: #575667;
}
.profile-card1 {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
  width: 100%;
  margin-top: 25px;
}
.student-profile-card {
  box-sizing: border-box;
  display: flex;
  flex: 1 0 auto;
  flex-direction: row;
  gap: 8px;
  align-items: flex-start;
  justify-content: space-between;
  padding: 14px 19px 25px 24px;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
}
.student-info-card {
  flex: 0 0 auto;
  padding-top: 10px;
}
.email-label-text-style {
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  color: #575667;
}
.email-link-text-style {
  display: block;
  padding: 0;
  margin: 0;
  margin-top: 8px;
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
  text-decoration-line: none;
}
.vertical-section-divider {
  margin-top: 23px;
}
.education-details-text-style {
  padding: 0;
  margin: 0;
  margin-top: 8px;
  font: 400 16px Raleway, sans-serif;
  color: #24222f;
}
.group-info-block {
  box-sizing: border-box;
  width: 100%;
  margin-top: 23px;
}
.edit-section-container {
  flex: 0 0 auto;
  align-self: center;
  padding-bottom: 281px;
}
.edit-button-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  height: 36px;
  padding-right: 9px;
  padding-left: 10px;
  background: #f5f9f8;
  border: 2px solid #ebefef;
  border-radius: 15px;
}
.edit-button-text-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  color: #575667;
}
.edit-icon {
  box-sizing: border-box;
  display: block;
  width: 15px;
  max-width: initial;
  height: 15px;
  margin-left: 6px;
  border: none;
  object-fit: cover;
}
.schedule-container {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 430px;
  padding: 36px 44px;
  margin-left: 24px;
  background: url("@/assets/image_3c444adc.png") 50% / cover no-repeat;
}
.calendar-container2 {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: flex-start;
  justify-content: flex-start;
  width: 100%;
  height: 284px;
}
.calendar-container1 {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  align-items: center;
  align-self: stretch;
  justify-content: space-between;
}
.center-aligned-flex-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  gap: 20px;
  align-items: center;
  justify-content: center;
}
.vertical-center-text-box {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  width: 72px;
  height: 23px;
}
.majestic-heading {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 700 20px Raleway, sans-serif;
  color: #3b3a4a;
}
.month-year-display-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 20px Montserrat, sans-serif;
  color: #3b3a4a;
}
.horizontal-flex-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  gap: 24px;
  align-items: center;
  justify-content: flex-start;
}
.svg-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  width: 6.5px;
  height: 13px;
}
.calendar-container {
  box-sizing: border-box;
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  align-items: flex-start;
  align-self: stretch;
  justify-content: flex-start;
}
.flex-calendar-row {
  box-sizing: border-box;
  display: flex;
  flex: 1 1 auto;
  flex-direction: row;
  align-items: center;
  align-self: stretch;
  justify-content: space-between;
  padding-top: 10px;
  padding-bottom: 10px;
}
.schedule-item {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 31px;
  height: 31px;
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  color: #24222f;
}
.day-of-week-label {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 31px;
  height: 31px;
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  color: #24222f;
  text-align: center;
}
.day-of-week-badge {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 31px;
  height: 31px;
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  color: #da1f38;
  text-align: center;
}
.highlighted-day-of-week {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 31px;
  height: 31px;
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  color: #da1f38;
}
.number-highlighted {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 31px;
  height: 31px;
  padding: 0;
  margin: 0;
  font: 400 20px Montserrat, sans-serif;
  color: #c5c8cc;
}
.number-highlighted-text {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 31px;
  height: 31px;
  padding: 0;
  margin: 0;
  font: 400 20px Montserrat, sans-serif;
  color: #c5c8cc;
  text-align: center;
}
.text-block {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 31px;
  height: 31px;
  padding: 0;
  margin: 0;
  font: 400 20px Montserrat, sans-serif;
  color: #24222f;
  text-align: center;
}
.numeric-highlighted-text {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 31px;
  height: 31px;
  padding: 0;
  margin: 0;
  font: 400 20px Montserrat, sans-serif;
  color: #da1f38;
  text-align: center;
}
.number-highlighted-text1 {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 31px;
  height: 31px;
  padding: 0;
  margin: 0;
  font: 400 20px Montserrat, sans-serif;
  color: #24222f;
}

.main-content-container1 {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  min-width: 1480px;
  background: #ebefef;
}

.sidebar-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 20px;
  background: #f5f9f8;
  border-radius: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.sidebar-button {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: auto; /* Ширина кнопки по размеру текста */
  min-width: 150px; /* Минимальная ширина кнопки */
  height: 47px;
  padding: 0 20px;
  margin: 10px 0;
  font: 400 20px Raleway, sans-serif;
  color: #24222f;
  background: #f5f9f8;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease;
  text-align: left;
  white-space: nowrap; /* Запрет переноса текста */
}

.sidebar-button:hover {
  background-color: #e0e4e8;
}

.sidebar-button.active {
  background-color: #a094b8;
  color: #f5f9f8;
  border-color: #a094b8; /* Обводка активной кнопки */
}

.progress-indicator-text-style {
  margin-top: 20px;
  font: 400 16px Raleway, sans-serif;
  color: #da1f38;
  cursor: pointer;
}
</style>