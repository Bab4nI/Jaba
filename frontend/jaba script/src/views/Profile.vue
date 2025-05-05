<template>
  <div style="display: inline-block; width: 1505px" data-ignore="used only for top most containter width">
    <div class="main-content-container1">
      <div class="profile-card-container">
        <div class="main-content-container">
          <div class="profile-card-container1">
            <Sidebar/>
            <div class="vertical-divider1"></div>
            <component :is="currentComponent" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
//views/Profile.vue
import { computed } from 'vue';
import { useUserStore } from '@/stores/user';
import Sidebar from '@/components/Sidebar.vue';
import Profile from '@/components/Profile.vue';
import CourseProgress from '@/components/CourseProgress.vue';
import CourseStatistics from '@/components/CourseStatistics.vue';
import Homework from '@/components/Homework.vue';
import InviteUser from '@/components/InviteUser.vue';
import NewsManager from '@/components/NewsManager.vue';

const userStore = useUserStore();
const activeTab = computed(() => userStore.activeTab);

const componentMap = {
  'Мой профиль': Profile,
  'Прогресс прохождения курса': CourseProgress,
  'Статистика прохождения курса': CourseStatistics,
  'Домашние задания': Homework,
  'Пригласить пользователя': InviteUser,
  'Управление новостями': NewsManager,
};

const currentComponent = computed(() => componentMap[activeTab.value] || Profile);
</script>

<style scoped>
.main-content-container1 {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  min-width: 1480px;
  background: var(--background-color);
  transition: background-color 0.3s ease;
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
  background: var(--form-background);
  transition: background-color 0.3s ease;
}

.main-title-text-style1 {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 36px Helvetica;
  color: var(--text-color);
  transition: color 0.3s ease;
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
  color: var(--text-color);
  transition: color 0.3s ease;
}

.vertical-divider {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 1px;
  height: 29px;
  border-left: 1px solid var(--border-color);
  transition: border-color 0.3s ease;
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
  color: var(--text-color);
  transition: color 0.3s ease;
}

.personal-info-divider {
  flex: 0 0 auto;
  margin-top: 2px;
  border-top: 1px solid var(--border-color);
  transition: border-color 0.3s ease;
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
  padding-top: 40px;
  padding-bottom: 96px;
}

.profile-card-container1 {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 25px;
  align-items: flex-start;
  justify-content: flex-start;
  width: 100%;
  padding: 57px 32px 225px;
  background: var(--form-background);
  border-radius: 30px;
  transition: background-color 0.3s ease;
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
  color: var(--footer-text);
  background: var(--accent-color);
  border: none;
  border-radius: 15px;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.transparent-input {
  box-sizing: border-box;
  width: 100%;
  font: 400 20px Raleway, sans-serif;
  background: transparent;
  border: none;
  outline: none;
  color: var(--footer-text);
  transition: color 0.3s ease;
}

.input-style-d23edb9f::placeholder {
  color: var(--footer-text);
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
  color: var(--secondary-text);
  text-align: left;
  transition: color 0.3s ease;
}

.course-progress-statistics {
  padding: 0;
  padding-right: 17px;
  padding-left: 17px;
  margin: 0;
  margin-top: 36px;
  font: 400 20px Raleway, sans-serif;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.progress-indicator-text-style {
  flex: 0 0 auto;
  align-self: center;
  padding: 0;
  margin: 0;
  margin-top: 151px;
  font: 400 20px Raleway, sans-serif;
  color: var(--error-color);
  transition: color 0.3s ease;
}

.vertical-divider1 {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: 3px;
  height: 716px;
  border-left: 3px solid var(--border-color);
  transition: border-color 0.3s ease;
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
  color: var(--text-color);
  transition: color 0.3s ease;
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
  background: var(--form-background);
  border: 2px solid var(--border-color);
  border-radius: 15px;
  transition: background-color 0.3s ease, border-color 0.3s ease;
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
  color: var(--text-color);
  transition: color 0.3s ease;
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
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.student-info-text-style {
  padding: 0;
  margin: 0;
  margin-top: 15px;
  font: 400 16px Raleway, sans-serif;
  color: var(--secondary-text);
  transition: color 0.3s ease;
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
  background: var(--form-background);
  border: 2px solid var(--border-color);
  border-radius: 15px;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.student-info-card {
  flex: 0 0 auto;
  padding-top: 10px;
}

.email-label-text-style {
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.email-link-text-style {
  display: block;
  padding: 0;
  margin: 0;
  margin-top: 8px;
  font: 400 16px Raleway, sans-serif;
  color: var(--text-color);
  text-decoration-line: none;
  transition: color 0.3s ease;
}

.vertical-section-divider {
  margin-top: 23px;
}

.education-details-text-style {
  padding: 0;
  margin: 0;
  margin-top: 8px;
  font: 400 16px Raleway, sans-serif;
  color: var(--text-color);
  transition: color 0.3s ease;
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
  gap: 6px;
  align-items: center;
  justify-content: flex-start;
  height: 36px;
  padding: 0 12px;
  background: var(--form-background);
  border: 2px solid var(--border-color);
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-button-container:hover {
  background: var(--hover-background);
}

.edit-button-text-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.edit-icon {
  box-sizing: border-box;
  display: block;
  width: 15px;
  max-width: initial;
  height: 15px;
  border: none;
  object-fit: cover;
  filter: brightness(1);
}

.dark-theme .edit-icon {
  filter: brightness(2);
}

.schedule-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  gap: 24px;
  align-items: flex-start;
  justify-content: flex-start;
  margin-left: 24px;
}

.calendar-container2 {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: flex-start;
  justify-content: flex-start;
  width: 300px;
  height: 284px;
}

.calendar-container1 {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 20px;
  align-items: center;
  justify-content: space-between;
}

.center-aligned-flex-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 20px;
  align-items: center;
  justify-content: center;
}

.vertical-center-text-box {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 23px;
}

.majestic-heading {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 700 17px Raleway, sans-serif;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.month-year-display-style {
  flex: 0 0 auto;
  padding: 0;
  margin: 0;
  font: 400 17px Raleway, sans-serif;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.horizontal-flex-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 20px;
  align-items: center;
  justify-content: flex-start;
}

.svg-container {
  box-sizing: border-box;
  display: flex;
  width: 7px;
  height: 13px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.svg-container svg {
  stroke: currentColor;
}

.calendar-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start;
  justify-content: flex-start;
}

.flex-calendar-row {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 10px;
  align-items: flex-start;
  justify-content: flex-start;
  padding-bottom: 10px;
}

.schedule-item {
  box-sizing: border-box;
  display: inline-block;
  width: 31px;
  max-width: 31px;
  max-height: initial;
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  color: var(--text-color);
  text-align: center;
  transition: color 0.3s ease;
}

.day-of-week-label {
  box-sizing: border-box;
  display: inline-block;
  width: 31px;
  max-width: 31px;
  max-height: initial;
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  text-align: center;
}

.day-of-week-badge {
  box-sizing: border-box;
  display: inline-block;
  width: 31px;
  max-width: 31px;
  max-height: initial;
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  text-align: center;
}

.highlighted-day-of-week {
  box-sizing: border-box;
  display: inline-block;
  width: 31px;
  max-width: 31px;
  max-height: initial;
  padding: 0;
  margin: 0;
  font: 400 14px Raleway, sans-serif;
  color: var(--error-color);
  text-align: center;
  transition: color 0.3s ease;
}

.weekend {
  color: var(--error-color);
  transition: color 0.3s ease;
}

.number-highlighted {
  box-sizing: border-box;
  width: 31px;
  max-width: 31px;
  max-height: initial;
  padding: 0;
  margin: 0;
  font: 400 20px Montserrat, sans-serif;
  color: var(--border-color);
  text-align: center;
  transition: color 0.3s ease;
}

.number-highlighted-text {
  box-sizing: border-box;
  display: inline-block;
  width: 31px;
  max-width: 31px;
  max-height: initial;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  text-align: center;
}

.text-block {
  box-sizing: border-box;
  width: 31px;
  max-width: 31px;
  max-height: initial;
  padding: 0;
  margin: 0;
  font: 400 20px Montserrat, sans-serif;
  color: var(--text-color);
  text-align: center;
  cursor: pointer;
  transition: color 0.3s ease;
}

.numeric-highlighted-text {
  box-sizing: border-box;
  display: inline-block;
  width: 31px;
  max-width: 31px;
  max-height: initial;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  text-align: center;
}

.number-highlighted-text1 {
  box-sizing: border-box;
  display: inline-block;
  width: 31px;
  max-width: 31px;
  max-height: initial;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: var(--text-color);
  text-align: center;
  transition: color 0.3s ease;
}

.sidebar-container {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 25px 0;
  width: 250px;
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