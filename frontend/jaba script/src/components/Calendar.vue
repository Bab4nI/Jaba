<template>
  <div class="schedule-container">
    <div class="calendar-container2">
      <div class="calendar-container1">
        <div class="horizontal-flex-container">
          <div class="svg-container small-icon" @click="prevMonth">
            <svg viewBox="0 0 6.5 13" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6,0.5l-5.5,6l5.5,6" stroke="#24222F" />
            </svg>
          </div>
          <div class="vertical-center-text-box">
            <p class="majestic-heading">{{ currentMonthName }} {{ currentYear }}</p>
          </div>
          <div class="svg-container small-icon" @click="nextMonth">
            <svg viewBox="0 0 6.5 13" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M0.5,0.5l5.5,6l-5.5,6" stroke="#24222F" />
            </svg>
          </div>
        </div>
      </div>
      <div class="calendar-container">
        <div class="flex-calendar-row">
          <p class="schedule-item">Пн</p>
          <p class="schedule-item">Вт</p>
          <p class="schedule-item">Ср</p>
          <p class="schedule-item">Чт</p>
          <p class="schedule-item">Пт</p>
          <p class="schedule-item weekend">Сб</p>
          <p class="schedule-item weekend">Вс</p>
        </div>
        <div class="calendar-grid">
          <div class="flex-calendar-row" v-for="(week, weekIndex) in calendarWeeks" :key="weekIndex">
            <p
              v-for="(day, index) in week"
              :key="index"
              :class="{
                'text-block': day.isCurrentMonth && index < 5,
                'weekend': day.isCurrentMonth && index >= 5,
                'number-highlighted': !day.isCurrentMonth,
                'selected-date': day.isCurrentMonth && selectedDate === day.day,
              }"
              @click="day.isCurrentMonth && openModal(day.day)"
            >
              {{ day.day }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Контроль работы №1</h3>
          <span class="close-btn" @click="closeModal">&times;</span>
        </div>
        <div class="modal-body">
          <p><strong>Номер:</strong> 2 февраля 2025г. 13:45-15:20</p>
          <p>
            <strong>Тест:</strong> по темам 1-10 модуля "Основы административной
            службы Linux". Протокол может быть упразднён.
          </p>
          <p><strong>КТ:</strong> 204-2, КТ606-7, КТ603-8</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const currentDate = ref(new Date());
const months = [
  "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
];

// Modal state
const showModal = ref(false);
const selectedDate = ref(null);

const currentMonth = computed(() => currentDate.value.getMonth());
const currentYear = computed(() => currentDate.value.getFullYear());
const currentMonthName = computed(() => months[currentMonth.value]);

const calendarWeeks = computed(() => {
  const year = currentYear.value;
  const month = currentMonth.value;
  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const startDay = firstDayOfMonth.getDay() === 0 ? 6 : firstDayOfMonth.getDay() - 1;
  const daysInMonth = lastDayOfMonth.getDate();
  const weeks = [];
  let week = [];

  for (let i = 0; i < startDay; i++) {
    week.push({ day: '', isCurrentMonth: false });
  }
  for (let day = 1; day <= daysInMonth; day++) {
    week.push({ day, isCurrentMonth: true });
    if (week.length === 7) {
      weeks.push(week);
      week = [];
    }
  }
  if (week.length > 0) {
    while (week.length < 7) {
      week.push({ day: '', isCurrentMonth: false });
    }
    weeks.push(week);
  }
  return weeks;
});

const prevMonth = () => {
  const newDate = new Date(currentDate.value);
  newDate.setMonth(newDate.getMonth() - 1);

  const minDate = new Date();
  minDate.setMonth(minDate.getMonth() - 2);

  if (newDate >= minDate) {
    currentDate.value = newDate;
  }
};

const nextMonth = () => {
  const newDate = new Date(currentDate.value);
  newDate.setMonth(newDate.getMonth() + 1);

  const maxDate = new Date();
  maxDate.setMonth(maxDate.getMonth() + 2);

  if (newDate <= maxDate) {
    currentDate.value = newDate;
  }
};

// Modal functions
const openModal = (day) => {
  selectedDate.value = day;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedDate.value = null;
};
</script>

<style scoped>
/* Existing styles */
.horizontal-flex-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  width: 100%;
}

.vertical-center-text-box {
  width: 150px;
  text-align: center;
}

.schedule-container {
  width: 430px;
  padding: 0px 44px;
}

.calendar-container2 {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.calendar-container1 {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.horizontal-flex-container {
  display: flex;
  align-items: center;
  gap: 20px;
}

.svg-container {
  cursor: pointer;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.svg-container svg {
  stroke: currentColor;
}

.small-icon svg {
  width: 10px;
  height: 10px;
}

.majestic-heading {
  font: 700 20px Raleway, sans-serif;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.flex-calendar-row {
  display: flex;
  justify-content: space-between;
}

.calendar-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.schedule-item {
  font: 400 14px Raleway, sans-serif;
  color: var(--text-color);
  text-align: center;
  width: 31px;
  transition: color 0.3s ease;
}

.weekend {
  color: var(--error-color);
  font: 400 20px Montserrat, sans-serif;
  text-align: center;
  width: 31px;
  transition: color 0.3s ease;
}

.text-block {
  font: 400 20px Montserrat, sans-serif;
  color: var(--text-color);
  text-align: center;
  width: 31px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.text-block:hover {
  background-color: var(--hover-background);
  border-radius: 50%;
}

.number-highlighted {
  font: 400 20px Montserrat, sans-serif;
  color: var(--border-color);
  text-align: center;
  width: 31px;
  transition: color 0.3s ease;
}

/* Highlight for selected date */
.selected-date {
  background-color: var(--hover-background);
  border-radius: 50%;
  font: 400 20px Montserrat, sans-serif;
  color: var(--text-color);
  transition: all 0.3s ease;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--form-background);
  border-radius: 8px;
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
  transition: border-color 0.3s ease;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.close-btn {
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  color: var(--secondary-text);
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: var(--text-color);
}

.modal-body {
  padding: 20px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.modal-body p {
  margin: 0 0 10px;
  line-height: 1.5;
}

.modal-body strong {
  font-weight: 600;
  color: var(--text-color);
  transition: color 0.3s ease;
}
</style>