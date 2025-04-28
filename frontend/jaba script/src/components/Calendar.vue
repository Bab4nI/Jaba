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
}

.small-icon svg {
  width: 10px;
  height: 10px;
}

.majestic-heading {
  font: 700 20px Raleway, sans-serif;
  color: #3b3a4a;
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
  color: #24222f;
  text-align: center;
  width: 31px;
}

.weekend {
  color: #da1f38;
  font: 400 20px Montserrat, sans-serif;
  text-align: center;
  width: 31px;
}

.text-block {
  font: 400 20px Montserrat, sans-serif;
  color: #24222f;
  text-align: center;
  width: 31px;
  cursor: pointer;
}

.number-highlighted {
  font: 400 20px Montserrat, sans-serif;
  color: #c5c8cc;
  text-align: center;
  width: 31px;
}

/* Highlight for selected date */
.selected-date {
  background-color: #e0e0e0;
  border-radius: 50%;
  font: 400 20px Montserrat, sans-serif;
  color: #24222f;
  text-align: center;
  width: 31px;
  cursor: pointer;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.modal-header h3 {
  margin: 0;
  font: 700 18px Raleway, sans-serif;
  color: #3b3a4a;
}

.close-btn {
  cursor: pointer;
  font-size: 24px;
  color: #24222f;
}

.modal-body {
  margin-top: 10px;
}

.modal-body p {
  margin: 5px 0;
  font: 400 14px Raleway, sans-serif;
  color: #24222f;
}

.modal-body strong {
  font-weight: 700;
}
</style>